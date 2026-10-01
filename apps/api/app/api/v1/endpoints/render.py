from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import structlog
import asyncio
import os
import tempfile
import json
import ffmpeg
from datetime import datetime, timedelta, timezone

from app.core.database import prisma
from app.api.v1.endpoints.auth import get_current_user
from app.core.exceptions import ValidationError, InsufficientCreditsError
from app.core.cloudinary import cloudinary_service
from app.core.config import settings

logger = structlog.get_logger()

router = APIRouter()


class ExportRequest(BaseModel):
    quality: str = "1080p"
    includeWatermark: bool = True


class ExportResponse(BaseModel):
    downloadUrl: str
    expiresAt: str


class RenderJobResponse(BaseModel):
    id: str
    projectId: str
    status: str
    priority: int
    outputVideoUrl: Optional[str]
    thumbnailUrl: Optional[str]
    duration: Optional[int]
    fileSize: Optional[int]
    costIncurred: float
    errorMessage: Optional[str]
    startedAt: Optional[str]
    completedAt: Optional[str]
    createdAt: str
    cloudinaryPublicId: Optional[str] = None


@router.post("/projects/{project_id}/render", response_model=RenderJobResponse)
async def start_render(
    project_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    project = await prisma.project.find_unique(where={"id": project_id})
    if not project or project.userId != current_user["id"]:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.status not in ["VISUALS_READY", "CAPTIONS_READY", "COMPLETE"]:
        raise ValidationError(f"Project not ready for rendering. Current status: {project.status}")

    credits_required = 1
    if current_user["credits_remaining"] < credits_required:
        raise InsufficientCreditsError(required=credits_required, available=current_user["credits_remaining"])

    await prisma.user.update(
        where={"id": current_user["id"]},
        data={"creditsRemaining": {"decrement": credits_required}, "creditsUsed": {"increment": credits_required}},
    )

    render_job = await prisma.renderjob.create(
        data={
            "projectId": project_id,
            "userId": current_user["id"],
            "status": "PENDING",
            "priority": 10 if current_user["plan"] != "FREE" else 1,
        }
    )

    await prisma.project.update(
        where={"id": project_id},
        data={"status": "RENDERING"},
    )

    background_tasks.add_task(process_render_job, render_job.id)

    logger.info("Render job created", job_id=render_job.id, project_id=project_id, user_id=current_user["id"])

    return RenderJobResponse(**render_job.model_dump())


async def process_render_job(job_id: str):
    try:
        job = await prisma.renderjob.find_unique(where={"id": job_id})
        if not job:
            return

        project = await prisma.project.find_unique(
            where={"id": job.projectId},
            include={"segments": True},
        )
        if not project:
            raise ValueError(f"Project {job.projectId} not found")

        await prisma.renderjob.update(
            where={"id": job_id},
            data={"status": "PROCESSING", "startedAt": "now()"},
        )

        output_path, thumbnail_path, duration, file_size = await render_video(job_id, project)

        upload_result = await upload_to_cloudinary(job_id, output_path, thumbnail_path, project.userId)

        await prisma.renderjob.update(
            where={"id": job_id},
            data={
                "status": "COMPLETE",
                "outputVideoUrl": upload_result["video_url"],
                "thumbnailUrl": upload_result["thumbnail_url"],
                "duration": duration,
                "fileSize": file_size,
                "costIncurred": 0.025,
                "completedAt": "now()",
            },
        )

        await prisma.project.update(
            where={"id": job.projectId},
            data={"status": "COMPLETE", "completedAt": "now()", "thumbnailUrl": upload_result["thumbnail_url"]},
        )

        cleanup_temp_files([output_path, thumbnail_path])

        logger.info("Render job completed", job_id=job_id, video_url=upload_result["video_url"])
    except Exception as e:
        logger.exception("Render job failed", job_id=job_id, error=str(e))
        await prisma.renderjob.update(
            where={"id": job_id},
            data={"status": "FAILED", "errorMessage": str(e)},
        )


async def render_video(job_id: str, project) -> tuple[str, str, int, int]:
    segments = project.scriptJson.get("segments", []) if project.scriptJson else []
    project_segments = project.segments

    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, f"render_{job_id}.mp4")
    thumbnail_path = os.path.join(temp_dir, f"thumb_{job_id}.jpg")

    segment_files = []
    total_duration = 0.0

    for idx, (seg_data, seg_db) in enumerate(zip(segments, project_segments)):
        visual_url = seg_data.get("visualUrl") or seg_db.visualUrl
        voiceover_url = seg_data.get("voiceoverUrl") or seg_db.voiceoverUrl

        if not visual_url:
            logger.warning(f"Segment {idx} has no visual URL, skipping")
            continue

        segment_path = os.path.join(temp_dir, f"seg_{job_id}_{idx}.mp4")

        try:
            video_stream = ffmpeg.input(visual_url)
            if voiceover_url:
                audio_stream = ffmpeg.input(voiceover_url)
                video_stream = ffmpeg.concat(video_stream, audio_stream, v=1, a=1).node[0]
        except Exception:
            video_stream = ffmpeg.input(visual_url)

        video_stream = ffmpeg.filter(video_stream, "scale", 1080, 1920, force_original_aspect_ratio="decrease")
        video_stream = ffmpeg.filter(video_stream, "pad", 1080, 1920, "(ow-iw)/2", "(oh-ih)/2", color="black")
        video_stream = ffmpeg.filter(video_stream, "setsar", 1)

        out = ffmpeg.output(
            video_stream,
            segment_path,
            vcodec="libx264",
            acodec="aac",
            preset="medium",
            crf=23,
            r=30,
            pix_fmt="yuv420p",
            movflags="+faststart",
        )
        await asyncio.to_thread(out.overwrite_output().run, capture_stdout=True, capture_stderr=True)

        segment_files.append(segment_path)
        segment_duration = float(seg_data.get("durationEstimate", 0) or seg_db.visualDuration or 5.0)
        total_duration += segment_duration

    if not segment_files:
        raise ValueError("No valid segments to render")

    concat_file = os.path.join(temp_dir, f"concat_{job_id}.txt")
    with open(concat_file, "w") as f:
        for seg_file in segment_files:
            f.write(f"file '{seg_file}'\n")

    concat_out = ffmpeg.input(concat_file, format="concat", safe=0)
    concat_out = ffmpeg.output(
        concat_out,
        output_path,
        vcodec="libx264",
        acodec="aac",
        preset="medium",
        crf=23,
        r=30,
        pix_fmt="yuv420p",
        movflags="+faststart",
    )
    await asyncio.to_thread(concat_out.overwrite_output().run, capture_stdout=True, capture_stderr=True)

    thumb_out = ffmpeg.input(output_path, ss=1)
    thumb_out = ffmpeg.output(thumb_out, thumbnail_path, vframes=1, format="image2", vcodec="mjpeg")
    await asyncio.to_thread(thumb_out.overwrite_output().run, capture_stdout=True, capture_stderr=True)

    file_size = os.path.getsize(output_path)

    cleanup_temp_files(segment_files + [concat_file])

    return output_path, thumbnail_path, int(total_duration), file_size


async def upload_to_cloudinary(job_id: str, video_path: str, thumbnail_path: str, user_id: str) -> dict:
    video_public_id = f"videogen/{user_id}/videos/{job_id}"

    video_result = cloudinary_service.upload_video(
        video_path,
        public_id=video_public_id,
        eager=[
            {"width": 1080, "height": 1920, "crop": "fill", "gravity": "auto", "aspect_ratio": "9:16"},
            {"quality": "auto", "fetch_format": "auto"},
        ],
        eager_async=True,
    )

    thumbnail_public_id = f"videogen/{user_id}/thumbnails/{job_id}"
    thumb_result = cloudinary_service.upload_image(
        thumbnail_path,
        public_id=thumbnail_public_id,
    )

    video_url = cloudinary_service.get_video_url(video_result["public_id"])
    thumbnail_url = cloudinary_service.get_thumbnail_url(video_result["public_id"])

    return {
        "video_url": video_url,
        "thumbnail_url": thumbnail_url,
        "video_public_id": video_result["public_id"],
        "thumbnail_public_id": thumb_result["public_id"],
    }


def cleanup_temp_files(file_paths: List[str]):
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.warning("Failed to cleanup temp file", path=path, error=str(e))


@router.get("/jobs/{job_id}", response_model=RenderJobResponse)
async def get_render_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
):
    job = await prisma.renderjob.find_unique(where={"id": job_id})
    if not job or job.userId != current_user["id"]:
        raise HTTPException(status_code=404, detail="Render job not found")
    return RenderJobResponse(**job.model_dump())


@router.get("/projects/{project_id}/jobs", response_model=list[RenderJobResponse])
async def list_render_jobs(
    project_id: str,
    current_user: dict = Depends(get_current_user),
):
    project = await prisma.project.find_unique(where={"id": project_id})
    if not project or project.userId != current_user["id"]:
        raise HTTPException(status_code=404, detail="Project not found")

    jobs = await prisma.renderjob.find_many(
        where={"projectId": project_id},
        order={"createdAt": "desc"},
    )
    return [RenderJobResponse(**j.model_dump()) for j in jobs]


@router.post("/projects/{project_id}/export", response_model=ExportResponse)
async def export_video(
    project_id: str,
    data: ExportRequest,
    current_user: dict = Depends(get_current_user),
):
    project = await prisma.project.find_unique(where={"id": project_id})
    if not project or project.userId != current_user["id"]:
        raise HTTPException(status_code=404, detail="Project not found")

    latest_job = await prisma.renderjob.find_first(
        where={"projectId": project_id, "status": "COMPLETE"},
        order={"completedAt": "desc"},
    )
    if not latest_job or not latest_job.outputVideoUrl:
        raise ValidationError("No completed render available for export")

    include_watermark = data.includeWatermark and current_user["plan"] == "FREE"

    if include_watermark:
        video_public_id = f"videogen/{current_user['id']}/videos/{latest_job.id}"
        download_url = cloudinary_service.get_watermarked_video_url(video_public_id)
    else:
        download_url = latest_job.outputVideoUrl

    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    return ExportResponse(
        downloadUrl=download_url,
        expiresAt=expires_at.isoformat(),
    )
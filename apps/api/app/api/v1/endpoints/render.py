from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import structlog

from app.core.database import prisma
from app.api.v1.endpoints.auth import get_current_user
from app.core.exceptions import ValidationError, InsufficientCreditsError

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

        await prisma.renderjob.update(
            where={"id": job_id},
            data={"status": "PROCESSING", "startedAt": "now()"},
        )

        import asyncio
        await asyncio.sleep(10)

        await prisma.renderjob.update(
            where={"id": job_id},
            data={
                "status": "COMPLETE",
                "outputVideoUrl": f"https://example.com/videos/{job_id}.mp4",
                "thumbnailUrl": f"https://example.com/thumbnails/{job_id}.jpg",
                "duration": 60,
                "fileSize": 5000000,
                "costIncurred": 0.025,
                "completedAt": "now()",
            },
        )

        await prisma.project.update(
            where={"id": job.projectId},
            data={"status": "COMPLETE", "completedAt": "now()"},
        )

        logger.info("Render job completed", job_id=job_id)
    except Exception as e:
        logger.exception("Render job failed", job_id=job_id, error=str(e))
        await prisma.renderjob.update(
            where={"id": job_id},
            data={"status": "FAILED", "errorMessage": str(e)},
        )


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

    return ExportResponse(
        downloadUrl=latest_job.outputVideoUrl + ("?watermark=1" if include_watermark else ""),
        expiresAt="2024-12-31T23:59:59Z",
    )
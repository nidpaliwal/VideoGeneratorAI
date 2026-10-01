from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
import structlog
import tempfile
import os
import cloudinary
import cloudinary.uploader

from app.core.database import prisma
from app.api.v1.endpoints.auth import get_current_user
from app.core.exceptions import ValidationError
from app.core.cloudinary import cloudinary_service
from app.core.config import settings

logger = structlog.get_logger()

router = APIRouter(prefix="/media", tags=["Media"])


class MediaItem(BaseModel):
    public_id: str
    url: str
    secure_url: str
    resource_type: str
    format: str
    width: Optional[int]
    height: Optional[int]
    duration: Optional[float]
    bytes: int
    created_at: str
    folder: str
    tags: List[str] = []


class MediaListResponse(BaseModel):
    items: List[MediaItem]
    total: int
    page: int
    page_size: int
    next_cursor: Optional[str]


class UploadResponse(BaseModel):
    public_id: str
    url: str
    secure_url: str
    resource_type: str
    format: str
    width: Optional[int]
    height: Optional[int]
    duration: Optional[float]
    bytes: int


class TransformationRequest(BaseModel):
    public_id: str
    transformations: List[dict]
    resource_type: str = "video"


@router.get("", response_model=MediaListResponse)
async def list_media(
    resource_type: str = Query("video", pattern="^(video|image|raw)$"),
    folder: str = Query("videogen/"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    prefix = f"{folder}{current_user['id']}/"
    max_results = page_size

    resources = cloudinary_service.list_resources(
        resource_type=resource_type,
        prefix=prefix,
        max_results=max_results,
    )

    items = [
        MediaItem(
            public_id=r["public_id"],
            url=r["url"],
            secure_url=r["secure_url"],
            resource_type=r["resource_type"],
            format=r["format"],
            width=r.get("width"),
            height=r.get("height"),
            duration=r.get("duration"),
            bytes=r["bytes"],
            created_at=r["created_at"],
            folder=r.get("folder", ""),
            tags=r.get("tags", []),
        )
        for r in resources
    ]

    return MediaListResponse(
        items=items,
        total=len(items),
        page=page,
        page_size=page_size,
        next_cursor=None,
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    folder: str = Form("videogen/uploads"),
    resource_type: str = Form("video"),
    current_user: dict = Depends(get_current_user),
):
    user_folder = f"{folder}/{current_user['id']}"

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        if resource_type == "video":
            result = cloudinary_service.upload_video(tmp_path, folder=user_folder)
        elif resource_type == "image":
            result = cloudinary_service.upload_image(tmp_path, folder=user_folder)
        else:
            result = cloudinary.uploader.upload(tmp_path, resource_type=resource_type, folder=user_folder)
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    return UploadResponse(
        public_id=result["public_id"],
        url=result["url"],
        secure_url=result["secure_url"],
        resource_type=result["resource_type"],
        format=result["format"],
        width=result.get("width"),
        height=result.get("height"),
        duration=result.get("duration"),
        bytes=result["bytes"],
    )


@router.post("/transform", response_model=UploadResponse)
async def transform_media(
    data: TransformationRequest,
    current_user: dict = Depends(get_current_user),
):
    url = cloudinary_service.get_delivery_url(
        data.public_id,
        resource_type=data.resource_type,
        transformations=data.transformations,
    )

    resource_info = cloudinary_service.get_resource_info(data.public_id, data.resource_type)

    return UploadResponse(
        public_id=data.public_id,
        url=url,
        secure_url=url,
        resource_type=data.resource_type,
        format=resource_info.get("format", ""),
        width=resource_info.get("width"),
        height=resource_info.get("height"),
        duration=resource_info.get("duration"),
        bytes=resource_info.get("bytes", 0),
    )


@router.get("/preview/{public_id:path}")
async def preview_media(
    public_id: str,
    resource_type: str = Query("video", pattern="^(video|image|raw)$"),
    transformation: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    user_prefix = f"videogen/{current_user['id']}/"
    if not public_id.startswith(user_prefix):
        public_id = f"{user_prefix}{public_id}"

    transformations = None
    if transformation:
        import json
        try:
            transformations = json.loads(transformation)
        except Exception:
            pass

    url = cloudinary_service.get_delivery_url(
        public_id,
        resource_type=resource_type,
        transformations=transformations,
    )

    return {
        "preview_url": url,
        "public_id": public_id,
        "transformations_applied": transformations,
    }


@router.get("/{public_id:path}")
async def get_media(
    public_id: str,
    resource_type: str = Query("video", pattern="^(video|image|raw)$"),
    current_user: dict = Depends(get_current_user),
):
    user_prefix = f"videogen/{current_user['id']}/"
    if not public_id.startswith(user_prefix.replace("/", "%2F")) and not public_id.startswith(user_prefix):
        public_id = f"{user_prefix}{public_id}"

    try:
        resource = cloudinary_service.get_resource_info(public_id, resource_type)
    except Exception as e:
        logger.error("Failed to get media info", public_id=public_id, error=str(e))
        raise HTTPException(status_code=404, detail="Media not found")

    return {
        "public_id": resource["public_id"],
        "url": resource["url"],
        "secure_url": resource["secure_url"],
        "resource_type": resource["resource_type"],
        "format": resource["format"],
        "width": resource.get("width"),
        "height": resource.get("height"),
        "duration": resource.get("duration"),
        "bytes": resource["bytes"],
        "created_at": resource["created_at"],
        "tags": resource.get("tags", []),
    }


@router.delete("/{public_id:path}")
async def delete_media(
    public_id: str,
    resource_type: str = Query("video", pattern="^(video|image|raw)$"),
    current_user: dict = Depends(get_current_user),
):
    user_prefix = f"videogen/{current_user['id']}/"
    if not public_id.startswith(user_prefix):
        public_id = f"{user_prefix}{public_id}"

    result = cloudinary_service.delete_resource(public_id, resource_type)

    if result.get("result") != "ok":
        raise HTTPException(status_code=400, detail="Failed to delete media")

    return {"message": "Media deleted successfully", "public_id": public_id}


@router.post("/signed-upload-url")
async def get_signed_upload_url(
    folder: str = Form("videogen/uploads"),
    resource_type: str = Form("video"),
    current_user: dict = Depends(get_current_user),
):
    user_folder = f"{folder}/{current_user['id']}"

    import cloudinary.utils
    params = {
        "folder": user_folder,
        "resource_type": resource_type,
        "timestamp": int(__import__("time").time()),
    }
    signature = cloudinary.utils.api_sign_request(params, settings.CLOUDINARY_API_SECRET)
    params["signature"] = signature
    params["api_key"] = settings.CLOUDINARY_API_KEY

    return {
        "upload_url": f"https://api.cloudinary.com/v1_1/{settings.CLOUDINARY_CLOUD_NAME}/{resource_type}/upload",
        "params": params,
    }
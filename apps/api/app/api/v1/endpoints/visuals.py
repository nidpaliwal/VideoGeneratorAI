from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import structlog

from app.core.database import prisma
from app.api.v1.endpoints.auth import get_current_user
from app.core.exceptions import ValidationError

logger = structlog.get_logger()

router = APIRouter()


class VisualSegmentRequest(BaseModel):
    keywords: List[str]
    duration: float
    styleTemplate: str = "STOCK_MONTAGE"


class VisualSearchRequest(BaseModel):
    projectId: str
    segments: List[VisualSegmentRequest]


class VisualOption(BaseModel):
    providerUrl: str
    previewUrl: str
    duration: float
    cost: float
    provider: str


class VisualSearchResponse(BaseModel):
    segmentOptions: List[List[VisualOption]]


class VisualSelection(BaseModel):
    segmentIndex: int
    providerUrl: str


class VisualSelectRequest(BaseModel):
    projectId: str
    selections: List[VisualSelection]


@router.post("/search", response_model=VisualSearchResponse)
async def search_visuals(
    data: VisualSearchRequest,
    current_user: dict = Depends(get_current_user),
):
    project = await prisma.project.find_unique(where={"id": data.projectId})
    if not project or project.userId != current_user["id"]:
        raise HTTPException(status_code=404, detail="Project not found")

    segment_options = []
    for seg in data.segments:
        options = [
            VisualOption(
                providerUrl=f"https://images.pexels.com/photos/{1000000+i}/pexels-photo-{1000000+i}.jpeg",
                previewUrl=f"https://images.pexels.com/photos/{1000000+i}/pexels-photo-{1000000+i}.jpeg?w=400",
                duration=seg.duration,
                cost=0.0,
                provider="pexels",
            )
            for i in range(3)
        ]
        segment_options.append(options)

    return VisualSearchResponse(segmentOptions=segment_options)


@router.post("/select")
async def select_visuals(
    data: VisualSelectRequest,
    current_user: dict = Depends(get_current_user),
):
    project = await prisma.project.find_unique(where={"id": data.projectId})
    if not project or project.userId != current_user["id"]:
        raise HTTPException(status_code=404, detail="Project not found")

    script_json = project.scriptJson
    segments = script_json.get("segments", [])

    for selection in data.selections:
        if selection.segmentIndex < len(segments):
            segments[selection.segmentIndex]["visualUrl"] = selection.providerUrl
            segments[selection.segmentIndex]["visualProvider"] = "pexels"

    await prisma.project.update(
        where={"id": data.projectId},
        data={"scriptJson": script_json, "status": "VISUALS_READY"},
    )

    return {"message": "Visuals selected successfully"}
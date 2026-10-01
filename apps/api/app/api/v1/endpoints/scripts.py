from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
import structlog

from app.core.database import prisma
from app.api.v1.endpoints.auth import get_current_user
from app.core.exceptions import ValidationError, InsufficientCreditsError

logger = structlog.get_logger()

router = APIRouter()


class ScriptSegmentRequest(BaseModel):
    text: str
    visualKeywords: List[str] = []
    durationEstimate: Optional[float] = None


class GenerateScriptRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500)
    tone: Optional[str] = "informative"
    lengthSeconds: Optional[int] = Field(default=60, ge=15, le=90)
    language: Optional[str] = "en"


class ScriptSegmentResponse(BaseModel):
    id: str
    orderIndex: int
    text: str
    visualKeywords: List[str]
    durationEstimate: Optional[float]


class GenerateScriptResponse(BaseModel):
    script: str
    segments: List[ScriptSegmentResponse]


@router.post("/generate", response_model=GenerateScriptResponse)
async def generate_script(
    data: GenerateScriptRequest,
    current_user: dict = Depends(get_current_user),
):
    if current_user["credits_remaining"] < 1:
        raise InsufficientCreditsError(required=1, available=current_user["credits_remaining"])

    await prisma.user.update(
        where={"id": current_user["id"]},
        data={"creditsRemaining": {"decrement": 1}, "creditsUsed": {"increment": 1}},
    )

    await prisma.usagelog.create(
        data={
            "userId": current_user["id"],
            "action": "script_generate",
            "creditsCost": 1,
            "metadata": {"topic": data.topic, "tone": data.tone, "lengthSeconds": data.lengthSeconds},
        }
    )

    segments = [
        ScriptSegmentResponse(
            id=f"seg-{i}",
            orderIndex=i,
            text=f"Segment {i+1} about {data.topic}",
            visualKeywords=[data.topic, "background", "abstract"],
            durationEstimate=10.0,
        )
        for i in range(3)
    ]

    return GenerateScriptResponse(
        script="\n\n".join([s.text for s in segments]),
        segments=segments,
    )


@router.post("/projects/{project_id}/script")
async def save_script(
    project_id: str,
    data: GenerateScriptResponse,
    current_user: dict = Depends(get_current_user),
):
    project = await prisma.project.find_unique(where={"id": project_id})
    if not project or project.userId != current_user["id"]:
        raise HTTPException(status_code=404, detail="Project not found")

    script_json = {
        "segments": [s.model_dump() for s in data.segments],
        "totalDurationEstimate": sum(s.durationEstimate or 0 for s in data.segments),
        "topic": data.segments[0].text.split(" ")[-1] if data.segments else "",
        "tone": "informative",
        "language": "en",
    }

    updated = await prisma.project.update(
        where={"id": project_id},
        data={"scriptJson": script_json, "status": "SCRIPT_READY"},
    )

    return {"project": updated, "message": "Script saved successfully"}
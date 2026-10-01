from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import structlog

from app.core.database import prisma
from app.api.v1.endpoints.auth import get_current_user
from app.core.exceptions import ValidationError

logger = structlog.get_logger()

router = APIRouter()


class CaptionStyle(BaseModel):
    font: Literal["Inter", "Montserrat", "Bebas Neue", "Anton"] = "Inter"
    fontSize: float = Field(default=4.0, ge=2.0, le=8.0)
    color: str = "#FFFFFF"
    highlightColor: str = "#FFD700"
    strokeWidth: int = Field(default=2, ge=0, le=5)
    strokeColor: str = "#000000"
    position: Literal["bottom", "center", "top"] = "bottom"
    animation: Literal["none", "fade", "pop", "karaoke"] = "karaoke"
    maxLines: Literal[1, 2] = 2


class WordTimestamp(BaseModel):
    word: str
    start: float
    end: float
    confidence: float


class GenerateCaptionsRequest(BaseModel):
    projectId: str
    audioUrl: str
    style: CaptionStyle


class GenerateCaptionsResponse(BaseModel):
    srtContent: str
    wordTimestamps: List[WordTimestamp]
    styleApplied: CaptionStyle


@router.post("/generate", response_model=GenerateCaptionsResponse)
async def generate_captions(
    data: GenerateCaptionsRequest,
    current_user: dict = Depends(get_current_user),
):
    project = await prisma.project.find_unique(where={"id": data.projectId})
    if not project or project.userId != current_user["id"]:
        raise HTTPException(status_code=404, detail="Project not found")

    await prisma.project.update(
        where={"id": data.projectId},
        data={"status": "CAPTIONS_READY"},
    )

    return GenerateCaptionsResponse(
        srtContent="1\n00:00:00,000 --> 00:00:05,000\nSample caption\n",
        wordTimestamps=[
            WordTimestamp(word="Sample", start=0.0, end=1.0, confidence=0.99),
            WordTimestamp(word="caption", start=1.0, end=2.0, confidence=0.98),
        ],
        styleApplied=data.style,
    )


@router.get("/styles")
async def get_caption_styles(current_user: dict = Depends(get_current_user)):
    return {
        "fonts": ["Inter", "Montserrat", "Bebas Neue", "Anton"],
        "animations": ["none", "fade", "pop", "karaoke"],
        "positions": ["bottom", "center", "top"],
        "presets": [
            {
                "name": "Modern Clean",
                "font": "Inter",
                "fontSize": 4.0,
                "color": "#FFFFFF",
                "highlightColor": "#0EA5E9",
                "strokeWidth": 2,
                "strokeColor": "#000000",
                "position": "bottom",
                "animation": "fade",
                "maxLines": 2,
            },
            {
                "name": "Bold Impact",
                "font": "Bebas Neue",
                "fontSize": 5.0,
                "color": "#FFFFFF",
                "highlightColor": "#FFD700",
                "strokeWidth": 3,
                "strokeColor": "#000000",
                "position": "center",
                "animation": "pop",
                "maxLines": 1,
            },
            {
                "name": "Karaoke Pro",
                "font": "Montserrat",
                "fontSize": 4.5,
                "color": "#FFFFFF",
                "highlightColor": "#FF6B6B",
                "strokeWidth": 2,
                "strokeColor": "#000000",
                "position": "bottom",
                "animation": "karaoke",
                "maxLines": 2,
            },
        ],
    }
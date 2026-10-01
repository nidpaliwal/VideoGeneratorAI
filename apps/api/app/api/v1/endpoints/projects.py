from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import structlog

from app.core.database import prisma
from app.api.v1.endpoints.auth import get_current_user

logger = structlog.get_logger()

router = APIRouter()


class ProjectCreate(BaseModel):
    title: Optional[str] = None
    scriptJson: dict


class ProjectResponse(BaseModel):
    id: str
    userId: str
    title: Optional[str]
    scriptJson: dict
    status: str
    duration: Optional[int]
    thumbnailUrl: Optional[str]
    createdAt: str
    updatedAt: str
    completedAt: Optional[str]


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
    page: int
    pageSize: int


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate,
    current_user: dict = Depends(get_current_user),
):
    project = await prisma.project.create(
        data={
            "userId": current_user["id"],
            "title": data.title,
            "scriptJson": data.scriptJson,
            "status": "DRAFT",
        }
    )
    return ProjectResponse(**project.model_dump())


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    where = {"userId": current_user["id"]}
    if status:
        where["status"] = status

    total = await prisma.project.count(where=where)
    projects = await prisma.project.find_many(
        where=where,
        skip=(page - 1) * pageSize,
        take=pageSize,
        order={"createdAt": "desc"},
        include={"renderJobs": {"take": 1, "order": {"createdAt": "desc"}}},
    )

    return ProjectListResponse(
        projects=[ProjectResponse(**p.model_dump()) for p in projects],
        total=total,
        page=page,
        pageSize=pageSize,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
):
    project = await prisma.project.find_unique(
        where={"id": project_id},
        include={"segments": True, "renderJobs": True},
    )
    if not project or project.userId != current_user["id"]:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse(**project.model_dump())


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: dict,
    current_user: dict = Depends(get_current_user),
):
    project = await prisma.project.find_unique(where={"id": project_id})
    if not project or project.userId != current_user["id"]:
        raise HTTPException(status_code=404, detail="Project not found")

    allowed_fields = ["title", "scriptJson", "status", "thumbnailUrl"]
    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    updated = await prisma.project.update(
        where={"id": project_id},
        data=update_data,
    )
    return ProjectResponse(**updated.model_dump())


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
):
    project = await prisma.project.find_unique(where={"id": project_id})
    if not project or project.userId != current_user["id"]:
        raise HTTPException(status_code=404, detail="Project not found")

    await prisma.project.delete(where={"id": project_id})
    return {"message": "Project deleted successfully"}
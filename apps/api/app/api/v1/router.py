from fastapi import APIRouter

from app.api.v1.endpoints import auth, scripts, voiceover, visuals, captions, projects, render, billing, webhooks

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(scripts.router, prefix="/scripts", tags=["Script Generation"])
api_router.include_router(voiceover.router, prefix="/voiceover", tags=["Voiceover"])
api_router.include_router(visuals.router, prefix="/visuals", tags=["Visuals"])
api_router.include_router(captions.router, prefix="/captions", tags=["Captions"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(render.router, prefix="/render", tags=["Rendering"])
api_router.include_router(billing.router, prefix="/billing", tags=["Billing"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
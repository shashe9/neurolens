from fastapi import APIRouter
from app.api.endpoints import (
    health,
    children,
    observations,
    milestones,
    visits,
    reports
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(children.router, prefix="/children", tags=["children"])
api_router.include_router(observations.router, tags=["observations"])
api_router.include_router(milestones.router, prefix="/milestones", tags=["milestones"])
api_router.include_router(visits.router, prefix="/visits", tags=["visits"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

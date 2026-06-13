from fastapi import APIRouter
from app.api.endpoints import (
    health,
    children,
    observations,
    milestones,
    visits,
    reports,
    ai,
    auth,
    feedback,
    validation,
    analytics
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(children.router, prefix="/children", tags=["children"])
api_router.include_router(observations.router, tags=["observations"])
api_router.include_router(milestones.router, tags=["milestones"])
api_router.include_router(visits.router, prefix="/visits", tags=["visits"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(validation.router, prefix="/validation-study", tags=["validation-study"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])


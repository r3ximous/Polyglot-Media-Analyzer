from fastapi import APIRouter
from .media import router as media_router
from .search import router as search_router

api_router = APIRouter()

# Include routers
api_router.include_router(media_router, prefix="/media", tags=["media"])
api_router.include_router(search_router, prefix="/search", tags=["search"])
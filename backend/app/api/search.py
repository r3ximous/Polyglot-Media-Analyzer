from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any

from ..core.database import get_db
from ..services.elasticsearch_service import ElasticSearchService
from ..api.schemas import SearchRequest, SearchResponse

router = APIRouter()
es_service = ElasticSearchService()

@router.post("/search", response_model=SearchResponse)
async def search_media_content(search_request: SearchRequest):
    """Search through media content"""
    try:
        results = await es_service.search_content(
            search_request.query,
            search_request.filters,
            search_request.size
        )
        
        return SearchResponse(
            total=results["total"],
            results=results["results"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_media_content_get(
    q: str = Query(..., description="Search query"),
    file_type: Optional[str] = Query(None, description="Filter by file type"),
    language: Optional[str] = Query(None, description="Filter by language"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment"),
    size: int = Query(10, description="Number of results to return")
):
    """Search through media content via GET request"""
    try:
        filters = {}
        if file_type:
            filters["file_type"] = file_type
        if language:
            filters["language"] = language
        if sentiment:
            filters["sentiment"] = sentiment
        
        results = await es_service.search_content(q, filters if filters else None, size)
        
        return SearchResponse(
            total=results["total"],
            results=results["results"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/aggregations/{field}")
async def get_field_aggregations(field: str):
    """Get aggregations for a specific field"""
    try:
        aggregations = await es_service.get_aggregations(field)
        return {"field": field, "buckets": aggregations}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/overview")
async def get_analytics_overview():
    """Get overview analytics"""
    try:
        # Get aggregations for different fields
        file_types = await es_service.get_aggregations("file_type")
        languages = await es_service.get_aggregations("language")
        sentiments = await es_service.get_aggregations("sentiment")
        
        return {
            "file_types": file_types,
            "languages": languages,
            "sentiments": sentiments
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
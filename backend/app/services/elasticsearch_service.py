from elasticsearch import AsyncElasticsearch
import json
import logging
from typing import List, Dict, Any, Optional
from ..core.config import settings

logger = logging.getLogger(__name__)

class ElasticSearchService:
    def __init__(self):
        self.client = None
        self.index_name = settings.ELASTICSEARCH_INDEX
        self._connect()
    
    def _connect(self):
        try:
            self.client = AsyncElasticsearch(
                [settings.ELASTICSEARCH_URL],
                verify_certs=False,
                ssl_show_warn=False
            )
            logger.info("Connected to ElasticSearch")
        except Exception as e:
            logger.error(f"Failed to connect to ElasticSearch: {e}")
    
    async def create_index(self):
        """Create the media content index with proper mappings"""
        try:
            if await self.client.indices.exists(index=self.index_name):
                logger.info(f"Index {self.index_name} already exists")
                return
            
            mapping = {
                "mappings": {
                    "properties": {
                        "file_id": {
                            "type": "keyword"
                        },
                        "filename": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "file_type": {
                            "type": "keyword"
                        },
                        "transcription_text": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "translation_text": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "summary_text": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "language": {
                            "type": "keyword"
                        },
                        "sentiment": {
                            "type": "keyword"
                        },
                        "objects_detected": {
                            "type": "keyword"
                        },
                        "created_at": {
                            "type": "date"
                        },
                        "duration": {
                            "type": "float"
                        },
                        "confidence_scores": {
                            "type": "object",
                            "enabled": False
                        }
                    }
                }
            }
            
            await self.client.indices.create(index=self.index_name, body=mapping)
            logger.info(f"Created index {self.index_name}")
            
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            raise
    
    async def index_media_content(self, file_id: str, content: Dict[str, Any]):
        """Index media analysis results for search"""
        try:
            await self.client.index(
                index=self.index_name,
                id=file_id,
                body=content
            )
            logger.info(f"Indexed content for file {file_id}")
            
        except Exception as e:
            logger.error(f"Failed to index content: {e}")
            raise
    
    async def search_content(self, query: str, filters: Optional[Dict[str, Any]] = None, size: int = 10) -> Dict[str, Any]:
        """Search through indexed media content"""
        try:
            # Build query
            search_query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": [
                                        "filename^2",
                                        "transcription_text",
                                        "translation_text",
                                        "summary_text",
                                        "objects_detected"
                                    ]
                                }
                            }
                        ]
                    }
                },
                "size": size,
                "highlight": {
                    "fields": {
                        "transcription_text": {},
                        "translation_text": {},
                        "summary_text": {}
                    }
                }
            }
            
            # Add filters if provided
            if filters:
                filter_clauses = []
                
                if "file_type" in filters:
                    filter_clauses.append({"term": {"file_type": filters["file_type"]}})
                
                if "language" in filters:
                    filter_clauses.append({"term": {"language": filters["language"]}})
                
                if "sentiment" in filters:
                    filter_clauses.append({"term": {"sentiment": filters["sentiment"]}})
                
                if "date_range" in filters:
                    filter_clauses.append({
                        "range": {
                            "created_at": {
                                "gte": filters["date_range"]["start"],
                                "lte": filters["date_range"]["end"]
                            }
                        }
                    })
                
                if filter_clauses:
                    search_query["query"]["bool"]["filter"] = filter_clauses
            
            # Execute search
            response = await self.client.search(
                index=self.index_name,
                body=search_query
            )
            
            return {
                "total": response["hits"]["total"]["value"],
                "results": [
                    {
                        "file_id": hit["_id"],
                        "source": hit["_source"],
                        "score": hit["_score"],
                        "highlights": hit.get("highlight", {})
                    }
                    for hit in response["hits"]["hits"]
                ]
            }
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    async def get_aggregations(self, field: str) -> Dict[str, Any]:
        """Get aggregations for a specific field"""
        try:
            search_query = {
                "size": 0,
                "aggs": {
                    f"{field}_stats": {
                        "terms": {
                            "field": field,
                            "size": 50
                        }
                    }
                }
            }
            
            response = await self.client.search(
                index=self.index_name,
                body=search_query
            )
            
            return response["aggregations"][f"{field}_stats"]["buckets"]
            
        except Exception as e:
            logger.error(f"Aggregation failed: {e}")
            raise
    
    async def delete_document(self, file_id: str):
        """Delete document from index"""
        try:
            await self.client.delete(index=self.index_name, id=file_id)
            logger.info(f"Deleted document {file_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            raise
    
    async def close(self):
        """Close ElasticSearch connection"""
        if self.client:
            await self.client.close()
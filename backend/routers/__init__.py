"""
API routers for AICA-SyS
"""

from .analysis import router as analysis_router
from .collection import router as collection_router
from .content import router as content_router

__all__ = [
    "content_router",
    "collection_router", 
    "analysis_router"
]

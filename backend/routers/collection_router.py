"""
コレクション関連のAPIエンドポイント
"""

from fastapi import APIRouter

router = APIRouter(prefix="/collection", tags=["Collection"])


@router.get("/")
async def get_collections():
    """コレクション一覧を取得"""
    return {"message": "Collection endpoint", "status": "ok"}

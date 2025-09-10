"""
コンテンツ関連のAPIエンドポイント
"""

from fastapi import APIRouter

router = APIRouter(prefix="/content", tags=["Content"])

@router.get("/")
async def get_content():
    """コンテンツ一覧を取得"""
    return {"message": "Content endpoint", "status": "ok"}

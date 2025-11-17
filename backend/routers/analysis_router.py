"""
分析関連のAPIエンドポイント
"""

from fastapi import APIRouter

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get("/")
async def get_analysis():
    """分析結果を取得"""
    return {"message": "Analysis endpoint", "status": "ok"}

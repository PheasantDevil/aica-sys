"""
AI関連のAPIエンドポイント
データ収集、分析、コンテンツ生成の統合API
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.ai_models import (
    AnalysisResult,
    CollectedContent,
    ContentCollection,
    GeneratedContent,
    TrendAnalysis,
    create_analysis_from_result,
    create_content_from_item,
    create_generated_content_from_result,
)
from services.ai_analyzer import AIAnalyzer
from services.ai_analyzer import AnalysisResult as ARAnalysisResult
from services.content_generator import ContentGenerator, ContentType
from services.content_generator import GeneratedContent as GCGeneratedContent
from services.data_collector import ContentItem, DataCollector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Services"])


# 依存性注入用の設定（実際の実装では環境変数から取得）
async def get_data_collector():
    """データ収集サービスのインスタンスを取得"""
    github_token = "your_github_token"  # 環境変数から取得
    return DataCollector(github_token)


async def get_ai_analyzer():
    """AI分析サービスのインスタンスを取得"""
    openai_key = "your_openai_key"  # 環境変数から取得
    google_ai_key = "your_google_ai_key"  # 環境変数から取得
    return AIAnalyzer(openai_key, google_ai_key)


async def get_content_generator():
    """コンテンツ生成サービスのインスタンスを取得"""
    openai_key = "your_openai_key"  # 環境変数から取得
    google_ai_key = "your_google_ai_key"  # 環境変数から取得
    return ContentGenerator(openai_key, google_ai_key)


@router.post("/collect")
async def collect_data(
    background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """データ収集を実行"""
    try:
        logger.info("データ収集を開始します...")

        # バックグラウンドでデータ収集を実行
        background_tasks.add_task(run_data_collection, db)

        return {
            "message": "データ収集を開始しました",
            "status": "started",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"データ収集開始エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_data_collection(db: Session):
    """データ収集の実行（バックグラウンド）"""
    try:
        async with DataCollector("your_github_token") as collector:
            items = await collector.collect_all_data()

            # データベースに保存
            for item in items:
                try:
                    # 重複チェック
                    existing = (
                        db.query(CollectedContent)
                        .filter(CollectedContent.url == item.url)
                        .first()
                    )
                    if not existing:
                        content = create_content_from_item(item)
                        db.add(content)
                        db.commit()
                        logger.info(f"新しいコンテンツを保存: {item.title}")
                except Exception as e:
                    logger.error(f"コンテンツ保存エラー: {e}")
                    continue

            logger.info(f"データ収集完了: {len(items)} 件")
    except Exception as e:
        logger.error(f"データ収集エラー: {e}")


@router.post("/analyze")
async def analyze_content(
    background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """コンテンツ分析を実行"""
    try:
        logger.info("コンテンツ分析を開始します...")

        # バックグラウンドで分析を実行
        background_tasks.add_task(run_content_analysis, db)

        return {
            "message": "コンテンツ分析を開始しました",
            "status": "started",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"分析開始エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_content_analysis(db: Session):
    """コンテンツ分析の実行（バックグラウンド）"""
    try:
        # 未分析のコンテンツを取得
        unanalyzed_content = (
            db.query(CollectedContent)
            .filter(
                ~CollectedContent.id.in_(db.query(AnalysisResult.content_id).distinct())
            )
            .limit(50)
            .all()
        )

        if not unanalyzed_content:
            logger.info("分析対象のコンテンツがありません")
            return

        # ContentItemに変換
        items = []
        for content in unanalyzed_content:
            item = ContentItem(
                title=content.title,
                url=content.url,
                content=content.content or "",
                source=content.source,
                published_at=content.published_at,
                tags=content.raw_data.get("tags", []) if content.raw_data else [],
                author=content.author,
                summary=content.summary,
            )
            items.append(item)

        # AI分析を実行
        analyzer = AIAnalyzer("your_openai_key", "your_google_ai_key")
        analysis_results = await analyzer.analyze_content(items)

        # データベースに保存
        for i, result in enumerate(analysis_results):
            try:
                analysis = create_analysis_from_result(result, unanalyzed_content[i].id)
                db.add(analysis)
                db.commit()
                logger.info(f"分析結果を保存: {result.category}")
            except Exception as e:
                logger.error(f"分析結果保存エラー: {e}")
                continue

        logger.info(f"コンテンツ分析完了: {len(analysis_results)} 件")
    except Exception as e:
        logger.error(f"コンテンツ分析エラー: {e}")


@router.post("/generate")
async def generate_content(
    content_type: str,
    target_audience: str = "developers",
    tone: str = "professional",
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
):
    """コンテンツ生成を実行"""
    try:
        logger.info(f"{content_type} の生成を開始します...")

        # バックグラウンドでコンテンツ生成を実行
        if background_tasks:
            background_tasks.add_task(
                run_content_generation, content_type, target_audience, tone, db
            )
        else:
            await run_content_generation(content_type, target_audience, tone, db)

        return {
            "message": f"{content_type} の生成を開始しました",
            "status": "started",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"コンテンツ生成開始エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_content_generation(
    content_type: str, target_audience: str, tone: str, db: Session
):
    """コンテンツ生成の実行"""
    try:
        # 最新の分析結果を取得
        analysis_results = (
            db.query(AnalysisResult)
            .order_by(AnalysisResult.created_at.desc())
            .limit(20)
            .all()
        )

        if not analysis_results:
            logger.warning("分析結果が見つかりません")
            return

        # ARAnalysisResultに変換
        ar_results = []
        for result in analysis_results:
            ar_result = ARAnalysisResult(
                content_id=str(result.id),
                importance_score=result.importance_score,
                category=result.category,
                subcategory=result.subcategory,
                trend_score=result.trend_score,
                sentiment=result.sentiment,
                key_topics=result.key_topics or [],
                summary=result.summary or "",
                recommendations=result.recommendations or [],
                created_at=result.created_at,
            )
            ar_results.append(ar_result)

        # コンテンツ生成
        generator = ContentGenerator("your_openai_key", "your_google_ai_key")
        content_type_enum = ContentType(content_type)
        generated_content = await generator.generate_content(
            content_type_enum, ar_results, target_audience, tone
        )

        # データベースに保存
        gc_content = create_generated_content_from_result(generated_content)
        db.add(gc_content)
        db.commit()

        logger.info(f"コンテンツ生成完了: {generated_content.title}")
    except Exception as e:
        logger.error(f"コンテンツ生成エラー: {e}")


@router.get("/content")
async def get_collected_content(
    skip: int = 0,
    limit: int = 20,
    source: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """収集されたコンテンツを取得"""
    try:
        query = db.query(CollectedContent)

        if source:
            query = query.filter(CollectedContent.source.contains(source))

        content = (
            query.order_by(CollectedContent.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return {
            "content": [
                {
                    "id": item.id,
                    "title": item.title,
                    "url": item.url,
                    "source": item.source,
                    "published_at": item.published_at.isoformat(),
                    "author": item.author,
                    "summary": item.summary,
                }
                for item in content
            ],
            "total": query.count(),
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"コンテンツ取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis")
async def get_analysis_results(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    min_importance: float = 0.0,
    db: Session = Depends(get_db),
):
    """分析結果を取得"""
    try:
        query = db.query(AnalysisResult)

        if category:
            query = query.filter(AnalysisResult.category == category)

        query = query.filter(AnalysisResult.importance_score >= min_importance)

        results = (
            query.order_by(AnalysisResult.importance_score.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return {
            "results": [
                {
                    "id": result.id,
                    "content_id": result.content_id,
                    "importance_score": result.importance_score,
                    "category": result.category,
                    "subcategory": result.subcategory,
                    "trend_score": result.trend_score,
                    "sentiment": result.sentiment,
                    "key_topics": result.key_topics,
                    "summary": result.summary,
                    "created_at": result.created_at.isoformat(),
                }
                for result in results
            ],
            "total": query.count(),
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"分析結果取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generated")
async def get_generated_content(
    skip: int = 0,
    limit: int = 20,
    content_type: Optional[str] = None,
    is_published: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """生成されたコンテンツを取得"""
    try:
        query = db.query(GeneratedContent)

        if content_type:
            query = query.filter(GeneratedContent.content_type == content_type)

        if is_published is not None:
            query = query.filter(GeneratedContent.is_published == is_published)

        content = (
            query.order_by(GeneratedContent.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return {
            "content": [
                {
                    "id": item.id,
                    "content_type": item.content_type,
                    "title": item.title,
                    "summary": item.summary,
                    "tags": item.tags,
                    "target_audience": item.target_audience,
                    "tone": item.tone,
                    "word_count": item.word_count,
                    "is_published": item.is_published,
                    "created_at": item.created_at.isoformat(),
                }
                for item in content
            ],
            "total": query.count(),
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"生成コンテンツ取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def get_trend_analysis(period: str = "weekly", db: Session = Depends(get_db)):
    """トレンド分析結果を取得"""
    try:
        # 最新のトレンド分析を取得
        trend = (
            db.query(TrendAnalysis)
            .filter(TrendAnalysis.period_type == period)
            .order_by(TrendAnalysis.analysis_date.desc())
            .first()
        )

        if not trend:
            return {"message": "トレンド分析データが見つかりません"}

        return {
            "analysis_date": trend.analysis_date.isoformat(),
            "period_type": trend.period_type,
            "total_content_count": trend.total_content_count,
            "high_importance_count": trend.high_importance_count,
            "trending_count": trend.trending_count,
            "category_distribution": trend.category_distribution,
            "sentiment_distribution": trend.sentiment_distribution,
            "top_topics": trend.top_topics,
            "trending_content_ids": trend.trending_content_ids,
        }
    except Exception as e:
        logger.error(f"トレンド分析取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/publish/{content_id}")
async def publish_content(content_id: int, db: Session = Depends(get_db)):
    """コンテンツを公開"""
    try:
        content = (
            db.query(GeneratedContent).filter(GeneratedContent.id == content_id).first()
        )

        if not content:
            raise HTTPException(status_code=404, detail="コンテンツが見つかりません")

        content.is_published = True
        content.published_at = datetime.utcnow()
        db.commit()

        return {
            "message": "コンテンツを公開しました",
            "content_id": content_id,
            "published_at": content.published_at.isoformat(),
        }
    except Exception as e:
        logger.error(f"コンテンツ公開エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_ai_stats(db: Session = Depends(get_db)):
    """AI関連の統計情報を取得"""
    try:
        total_content = db.query(CollectedContent).count()
        total_analysis = db.query(AnalysisResult).count()
        total_generated = db.query(GeneratedContent).count()
        published_content = (
            db.query(GeneratedContent)
            .filter(GeneratedContent.is_published == True)
            .count()
        )

        # カテゴリ別統計
        category_stats = (
            db.query(
                AnalysisResult.category, db.func.count(AnalysisResult.id).label("count")
            )
            .group_by(AnalysisResult.category)
            .all()
        )

        return {
            "total_collected_content": total_content,
            "total_analysis_results": total_analysis,
            "total_generated_content": total_generated,
            "published_content": published_content,
            "category_distribution": {cat: count for cat, count in category_stats},
            "last_updated": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"統計情報取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

"""
Analysis API router for AICA-SyS
"""

from typing import List, Optional

from agents.analysis_agent import AnalysisAgent
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from models.collection import AnalysisResult
from sqlalchemy.orm import Session
from utils.ai_client import AIClient

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/results")
async def get_analysis_results(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sentiment: Optional[str] = None,
    relevance_min: Optional[float] = Query(None, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    """Get analysis results with filtering"""
    query = db.query(AnalysisResult)
    
    if sentiment:
        query = query.filter(AnalysisResult.sentiment == sentiment)
    
    if relevance_min is not None:
        query = query.filter(AnalysisResult.relevance >= relevance_min)
    
    results = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "results": results,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/results/{result_id}")
async def get_analysis_result(result_id: str, db: Session = Depends(get_db)):
    """Get specific analysis result by ID"""
    result = db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Analysis result not found")
    
    return result


@router.post("/analyze")
async def start_analysis(db: Session = Depends(get_db)):
    """Start analysis process"""
    try:
        # Initialize AI client
        ai_client = AIClient()
        
        # Initialize analysis agent
        analysis_agent = AnalysisAgent(db, ai_client)
        
        # Start analysis
        results = await analysis_agent.analyze_collected_data()
        
        return {
            "message": "Analysis started successfully",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/summary")
async def get_analysis_summary(db: Session = Depends(get_db)):
    """Get analysis summary"""
    try:
        # Initialize AI client
        ai_client = AIClient()
        
        # Initialize analysis agent
        analysis_agent = AnalysisAgent(db, ai_client)
        
        # Get summary
        summary = await analysis_agent.get_analysis_summary()
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analysis summary: {str(e)}")


@router.get("/trends")
async def get_trend_insights(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get trend insights from analysis results"""
    try:
        # Get high-relevance results
        high_relevance_results = db.query(AnalysisResult).filter(
            AnalysisResult.relevance >= 0.7
        ).offset(skip).limit(limit).all()
        
        # Group by sentiment
        sentiment_counts = {}
        for result in high_relevance_results:
            sentiment = result.sentiment
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        # Get most common key points
        all_key_points = []
        for result in high_relevance_results:
            all_key_points.extend(result.key_points)
        
        # Count key points (simplified)
        key_point_counts = {}
        for point in all_key_points:
            key_point_counts[point] = key_point_counts.get(point, 0) + 1
        
        # Get top key points
        top_key_points = sorted(
            key_point_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        return {
            "high_relevance_count": len(high_relevance_results),
            "sentiment_distribution": sentiment_counts,
            "top_key_points": [{"point": point, "count": count} for point, count in top_key_points],
            "results": high_relevance_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trend insights: {str(e)}")


@router.get("/sentiment")
async def get_sentiment_analysis(db: Session = Depends(get_db)):
    """Get sentiment analysis overview"""
    try:
        # Get all analysis results
        all_results = db.query(AnalysisResult).all()
        
        if not all_results:
            return {
                "total_analyzed": 0,
                "sentiment_distribution": {},
                "average_relevance": 0.0,
                "insights": []
            }
        
        # Calculate sentiment distribution
        sentiment_counts = {}
        total_relevance = 0.0
        
        for result in all_results:
            sentiment = result.sentiment
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            total_relevance += result.relevance
        
        # Calculate percentages
        total_count = len(all_results)
        sentiment_percentages = {
            sentiment: (count / total_count) * 100 
            for sentiment, count in sentiment_counts.items()
        }
        
        # Calculate average relevance
        average_relevance = total_relevance / total_count
        
        # Generate insights
        insights = []
        if sentiment_percentages.get("positive", 0) > 50:
            insights.append("Overall sentiment is positive - good news for TypeScript ecosystem")
        elif sentiment_percentages.get("negative", 0) > 30:
            insights.append("Significant negative sentiment detected - may need attention")
        
        if average_relevance > 0.7:
            insights.append("High relevance content detected - valuable insights available")
        
        return {
            "total_analyzed": total_count,
            "sentiment_distribution": sentiment_percentages,
            "average_relevance": round(average_relevance, 2),
            "insights": insights
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sentiment analysis: {str(e)}")


@router.post("/content/generate")
async def generate_content(db: Session = Depends(get_db)):
    """Generate content from analysis results"""
    try:
        # Initialize AI client
        ai_client = AIClient()
        
        # Initialize content generation agent
        from agents.content_generation_agent import ContentGenerationAgent
        content_agent = ContentGenerationAgent(db, ai_client)
        
        # Generate content
        results = await content_agent.generate_weekly_content()
        
        return {
            "message": "Content generation started successfully",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

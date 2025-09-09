"""
Collection API router for AICA-SyS
"""

from typing import List, Optional

from agents.collection_agent import CollectionAgent
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from models.collection import AnalysisResult, CollectionJob
from sqlalchemy.orm import Session
from utils.ai_client import AIClient

router = APIRouter(prefix="/api/collection", tags=["collection"])


@router.get("/jobs")
async def get_collection_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get collection jobs"""
    query = db.query(CollectionJob)
    
    if status:
        query = query.filter(CollectionJob.status == status)
    
    jobs = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "jobs": jobs,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/jobs/{job_id}")
async def get_collection_job(job_id: str, db: Session = Depends(get_db)):
    """Get specific collection job by ID"""
    job = db.query(CollectionJob).filter(CollectionJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Collection job not found")
    
    return job


@router.post("/start")
async def start_collection(
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Start collection process"""
    try:
        # Initialize AI client (you would get API keys from environment)
        ai_client = AIClient()
        
        # Initialize collection agent
        collection_agent = CollectionAgent(db, github_token=None)
        
        # Start collection
        results = await collection_agent.collect_all()
        
        return {
            "message": "Collection started successfully",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Collection failed: {str(e)}")


@router.get("/analysis")
async def get_analysis_results(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sentiment: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get analysis results"""
    query = db.query(AnalysisResult)
    
    if sentiment:
        query = query.filter(AnalysisResult.sentiment == sentiment)
    
    results = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "results": results,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/analysis/{result_id}")
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
        from agents.analysis_agent import AnalysisAgent
        analysis_agent = AnalysisAgent(db, ai_client)
        
        # Start analysis
        results = await analysis_agent.analyze_collected_data()
        
        return {
            "message": "Analysis started successfully",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/stats")
async def get_collection_stats(db: Session = Depends(get_db)):
    """Get collection and analysis statistics"""
    try:
        # Collection job stats
        total_jobs = db.query(CollectionJob).count()
        completed_jobs = db.query(CollectionJob).filter(CollectionJob.status == "completed").count()
        failed_jobs = db.query(CollectionJob).filter(CollectionJob.status == "failed").count()
        
        # Analysis result stats
        total_analyzed = db.query(AnalysisResult).count()
        
        # Recent activity (last 24 hours)
        from datetime import datetime, timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        recent_jobs = db.query(CollectionJob).filter(
            CollectionJob.created_at >= yesterday
        ).count()
        
        recent_analyzed = db.query(AnalysisResult).filter(
            AnalysisResult.created_at >= yesterday
        ).count()
        
        return {
            "collection": {
                "total_jobs": total_jobs,
                "completed_jobs": completed_jobs,
                "failed_jobs": failed_jobs,
                "recent_jobs": recent_jobs
            },
            "analysis": {
                "total_analyzed": total_analyzed,
                "recent_analyzed": recent_analyzed
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

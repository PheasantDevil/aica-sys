"""
Premium Reports Router
Handles premium report generation and sales for revenue generation
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import stripe
import os
import json

from database import get_db
from models.content import Article, Newsletter, Trend
from models.user import User
from models.subscription import Subscription
from security.auth_middleware import get_current_user
from utils.logging import get_logger
from services.ai_analyzer import AIAnalyzer
from services.content_generator import ContentGenerator

router = APIRouter(prefix="/api/reports", tags=["reports"])
logger = get_logger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@router.get("/available")
async def get_available_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available premium reports"""
    try:
        # Check if user has active subscription
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        ).first()
        
        reports = [
            {
                "id": "typescript-trends-2024",
                "title": "TypeScript Ecosystem Trends 2024",
                "description": "Comprehensive analysis of TypeScript ecosystem trends, framework adoption, and developer preferences",
                "price": 4980,
                "currency": "JPY",
                "estimated_pages": 25,
                "topics": [
                    "Framework adoption rates",
                    "Developer tool preferences", 
                    "Performance benchmarks",
                    "Community growth metrics",
                    "Future predictions"
                ],
                "is_premium_only": True,
                "requires_subscription": not subscription
            },
            {
                "id": "nextjs-performance-guide",
                "title": "Next.js Performance Optimization Guide",
                "description": "Advanced techniques for optimizing Next.js applications for production",
                "price": 4980,
                "currency": "JPY", 
                "estimated_pages": 20,
                "topics": [
                    "Core Web Vitals optimization",
                    "Bundle size reduction",
                    "Image optimization",
                    "Caching strategies",
                    "Performance monitoring"
                ],
                "is_premium_only": True,
                "requires_subscription": not subscription
            },
            {
                "id": "ai-development-tools",
                "title": "AI-Powered Development Tools Analysis",
                "description": "Analysis of AI tools transforming TypeScript development workflows",
                "price": 4980,
                "currency": "JPY",
                "estimated_pages": 18,
                "topics": [
                    "Code generation tools",
                    "AI-assisted debugging",
                    "Automated testing",
                    "Documentation generation",
                    "Performance optimization"
                ],
                "is_premium_only": True,
                "requires_subscription": not subscription
            }
        ]
        
        return {"reports": reports}
        
    except Exception as e:
        logger.error(f"Error fetching available reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch available reports"
        )

@router.post("/purchase/{report_id}")
async def purchase_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Purchase a premium report"""
    try:
        # Get report details
        report_details = await get_report_details(report_id)
        if not report_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Create Stripe checkout session for one-time payment
        session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'jpy',
                    'product_data': {
                        'name': report_details['title'],
                        'description': report_details['description'],
                    },
                    'unit_amount': report_details['price'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{os.getenv('NEXTAUTH_URL')}/reports/{report_id}?success=true",
            cancel_url=f"{os.getenv('NEXTAUTH_URL')}/reports?canceled=true",
            metadata={
                'user_id': str(current_user.id),
                'report_id': report_id,
                'type': 'premium_report'
            }
        )
        
        return {
            "checkout_url": session.url,
            "session_id": session.id
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment processing error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )

@router.get("/{report_id}")
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific report (if purchased)"""
    try:
        # Check if user has purchased this report
        # This would typically be stored in a purchases table
        # For now, we'll check if user has active subscription
        
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Report access requires active subscription or purchase"
            )
        
        # Generate report content
        report_content = await generate_report_content(report_id, db)
        
        return {
            "report_id": report_id,
            "content": report_content,
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch report"
        )

@router.post("/generate/{report_id}")
async def generate_report(
    report_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a premium report (background task)"""
    try:
        # Check if user has access
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Report generation requires active subscription"
            )
        
        # Add background task to generate report
        background_tasks.add_task(generate_report_background, report_id, current_user.id, db)
        
        return {
            "message": "Report generation started",
            "report_id": report_id,
            "status": "generating"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting report generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start report generation"
        )

async def get_report_details(report_id: str) -> Optional[dict]:
    """Get report details by ID"""
    reports = {
        "typescript-trends-2024": {
            "title": "TypeScript Ecosystem Trends 2024",
            "description": "Comprehensive analysis of TypeScript ecosystem trends, framework adoption, and developer preferences",
            "price": 4980,
            "topics": [
                "Framework adoption rates",
                "Developer tool preferences", 
                "Performance benchmarks",
                "Community growth metrics",
                "Future predictions"
            ]
        },
        "nextjs-performance-guide": {
            "title": "Next.js Performance Optimization Guide",
            "description": "Advanced techniques for optimizing Next.js applications for production",
            "price": 4980,
            "topics": [
                "Core Web Vitals optimization",
                "Bundle size reduction",
                "Image optimization",
                "Caching strategies",
                "Performance monitoring"
            ]
        },
        "ai-development-tools": {
            "title": "AI-Powered Development Tools Analysis",
            "description": "Analysis of AI tools transforming TypeScript development workflows",
            "price": 4980,
            "topics": [
                "Code generation tools",
                "AI-assisted debugging",
                "Automated testing",
                "Documentation generation",
                "Performance optimization"
            ]
        }
    }
    
    return reports.get(report_id)

async def generate_report_content(report_id: str, db: Session) -> dict:
    """Generate report content using AI"""
    try:
        ai_analyzer = AIAnalyzer()
        content_generator = ContentGenerator()
        
        # Get relevant data for the report
        articles = db.query(Article).filter(
            Article.created_at >= datetime.now() - timedelta(days=30)
        ).limit(50).all()
        
        trends = db.query(Trend).filter(
            Trend.created_at >= datetime.now() - timedelta(days=30)
        ).limit(20).all()
        
        newsletters = db.query(Newsletter).filter(
            Newsletter.created_at >= datetime.now() - timedelta(days=30)
        ).limit(10).all()
        
        # Generate report based on report type
        if report_id == "typescript-trends-2024":
            content = await generate_typescript_trends_report(articles, trends, newsletters, ai_analyzer, content_generator)
        elif report_id == "nextjs-performance-guide":
            content = await generate_nextjs_performance_report(articles, trends, ai_analyzer, content_generator)
        elif report_id == "ai-development-tools":
            content = await generate_ai_tools_report(articles, trends, ai_analyzer, content_generator)
        else:
            content = {"error": "Unknown report type"}
        
        return content
        
    except Exception as e:
        logger.error(f"Error generating report content: {e}")
        return {"error": "Failed to generate report content"}

async def generate_typescript_trends_report(articles, trends, newsletters, ai_analyzer, content_generator):
    """Generate TypeScript trends report"""
    # This would use AI to analyze the data and generate comprehensive report
    return {
        "title": "TypeScript Ecosystem Trends 2024",
        "sections": [
            {
                "title": "Executive Summary",
                "content": "Analysis of TypeScript ecosystem trends based on recent data..."
            },
            {
                "title": "Framework Adoption",
                "content": "Detailed analysis of framework adoption rates..."
            },
            {
                "title": "Developer Preferences",
                "content": "Insights into developer tool preferences..."
            }
        ],
        "data_points": len(articles) + len(trends) + len(newsletters),
        "generated_at": datetime.now().isoformat()
    }

async def generate_nextjs_performance_report(articles, trends, ai_analyzer, content_generator):
    """Generate Next.js performance report"""
    return {
        "title": "Next.js Performance Optimization Guide",
        "sections": [
            {
                "title": "Core Web Vitals Optimization",
                "content": "Best practices for optimizing Core Web Vitals..."
            },
            {
                "title": "Bundle Size Reduction",
                "content": "Techniques for reducing bundle size..."
            }
        ],
        "data_points": len(articles) + len(trends),
        "generated_at": datetime.now().isoformat()
    }

async def generate_ai_tools_report(articles, trends, ai_analyzer, content_generator):
    """Generate AI tools report"""
    return {
        "title": "AI-Powered Development Tools Analysis",
        "sections": [
            {
                "title": "Code Generation Tools",
                "content": "Analysis of AI code generation tools..."
            },
            {
                "title": "AI-Assisted Debugging",
                "content": "Overview of AI debugging tools..."
            }
        ],
        "data_points": len(articles) + len(trends),
        "generated_at": datetime.now().isoformat()
    }

async def generate_report_background(report_id: str, user_id: int, db: Session):
    """Background task to generate report"""
    try:
        logger.info(f"Starting background report generation for {report_id}")
        
        # Generate report content
        content = await generate_report_content(report_id, db)
        
        # Store generated report (this would typically be saved to database)
        logger.info(f"Report {report_id} generated successfully for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error in background report generation: {e}")

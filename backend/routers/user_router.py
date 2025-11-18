"""
User Management Router
Handles user-related API endpoints for production user management
"""

import os
from datetime import datetime, timedelta
from typing import List, Optional

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.subscription import Subscription
from models.user import User
from pydantic import BaseModel, EmailStr
from security.auth_middleware import get_current_user
from sqlalchemy.orm import Session
from utils.logging import get_logger

router = APIRouter(prefix="/api/users", tags=["users"])
logger = get_logger(__name__)


# Pydantic models for request/response
class UserProfile(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    image: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    role: str = "user"


class UserUpdate(BaseModel):
    name: Optional[str] = None
    image: Optional[str] = None


class UserSettings(BaseModel):
    email_notifications: bool = True
    newsletter_subscription: bool = True
    marketing_emails: bool = False
    theme: str = "light"
    language: str = "ja"


class UserStats(BaseModel):
    total_articles_read: int = 0
    total_newsletters_received: int = 0
    subscription_status: Optional[str] = None
    subscription_plan: Optional[str] = None
    subscription_expires: Optional[datetime] = None


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's profile"""
    try:
        return UserProfile(
            id=str(current_user.id),
            email=current_user.email,
            name=current_user.name,
            image=current_user.image,
            created_at=current_user.created_at,
            last_login=current_user.last_login,
            is_active=current_user.is_active,
            role=current_user.role,
        )
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile",
        )


@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile"""
    try:
        # Update user fields
        if user_update.name is not None:
            current_user.name = user_update.name
        if user_update.image is not None:
            current_user.image = user_update.image

        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)

        return UserProfile(
            id=str(current_user.id),
            email=current_user.email,
            name=current_user.name,
            image=current_user.image,
            created_at=current_user.created_at,
            last_login=current_user.last_login,
            is_active=current_user.is_active,
            role=current_user.role,
        )
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile",
        )


@router.get("/settings")
async def get_user_settings(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's settings"""
    try:
        # Get user settings from database or return defaults
        settings = {
            "email_notifications": getattr(current_user, "email_notifications", True),
            "newsletter_subscription": getattr(
                current_user, "newsletter_subscription", True
            ),
            "marketing_emails": getattr(current_user, "marketing_emails", False),
            "theme": getattr(current_user, "theme", "light"),
            "language": getattr(current_user, "language", "ja"),
        }

        return {"settings": settings}
    except Exception as e:
        logger.error(f"Error fetching user settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user settings",
        )


@router.put("/settings")
async def update_user_settings(
    settings: UserSettings,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's settings"""
    try:
        # Update user settings
        current_user.email_notifications = settings.email_notifications
        current_user.newsletter_subscription = settings.newsletter_subscription
        current_user.marketing_emails = settings.marketing_emails
        current_user.theme = settings.theme
        current_user.language = settings.language
        current_user.updated_at = datetime.utcnow()

        db.commit()

        return {"message": "Settings updated successfully"}
    except Exception as e:
        logger.error(f"Error updating user settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user settings",
        )


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's statistics"""
    try:
        # Get user subscription
        subscription = (
            db.query(Subscription)
            .filter(
                Subscription.user_id == current_user.id, Subscription.status == "active"
            )
            .first()
        )

        # Calculate stats (this would typically come from analytics)
        stats = UserStats(
            total_articles_read=getattr(current_user, "articles_read", 0),
            total_newsletters_received=getattr(current_user, "newsletters_received", 0),
            subscription_status=subscription.status if subscription else None,
            subscription_plan=(
                subscription.plan.name if subscription and subscription.plan else None
            ),
            subscription_expires=(
                subscription.current_period_end if subscription else None
            ),
        )

        return stats
    except Exception as e:
        logger.error(f"Error fetching user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user stats",
        )


@router.post("/activity")
async def log_user_activity(
    activity_type: str,
    activity_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Log user activity for analytics"""
    try:
        # Log user activity (this would typically be stored in an analytics table)
        logger.info(
            f"User activity: {current_user.email} - {activity_type}",
            extra={
                "user_id": str(current_user.id),
                "activity_type": activity_type,
                "activity_data": activity_data,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        return {"message": "Activity logged successfully"}
    except Exception as e:
        logger.error(f"Error logging user activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log user activity",
        )


@router.get("/subscription")
async def get_user_subscription(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's subscription details"""
    try:
        subscription = (
            db.query(Subscription)
            .filter(Subscription.user_id == current_user.id)
            .first()
        )

        if not subscription:
            return {"subscription": None}

        return {
            "subscription": {
                "id": str(subscription.id),
                "status": subscription.status,
                "plan": (
                    {
                        "name": subscription.plan.name,
                        "price": subscription.plan.price,
                        "currency": subscription.plan.currency,
                        "features": subscription.plan.features,
                    }
                    if subscription.plan
                    else None
                ),
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "created_at": subscription.created_at,
            }
        }
    except Exception as e:
        logger.error(f"Error fetching user subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user subscription",
        )


@router.delete("/account")
async def delete_user_account(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Delete current user's account (soft delete)"""
    try:
        # Soft delete user account
        current_user.is_active = False
        current_user.deleted_at = datetime.utcnow()
        current_user.email = f"deleted_{current_user.id}@deleted.com"  # Anonymize email

        # Cancel any active subscriptions
        subscriptions = (
            db.query(Subscription)
            .filter(
                Subscription.user_id == current_user.id, Subscription.status == "active"
            )
            .all()
        )

        for subscription in subscriptions:
            subscription.status = "canceled"
            subscription.canceled_at = datetime.utcnow()

        db.commit()

        logger.info(f"User account deleted: {current_user.id}")

        return {"message": "Account deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting user account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user account",
        )


# Admin endpoints (require admin role)
@router.get("/admin/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all users (admin only)"""
    try:
        # Check if user is admin
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        users = (
            db.query(User)
            .filter(User.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

        return {
            "users": [
                {
                    "id": str(user.id),
                    "email": user.email,
                    "name": user.name,
                    "role": user.role,
                    "created_at": user.created_at,
                    "last_login": user.last_login,
                    "is_active": user.is_active,
                }
                for user in users
            ],
            "total": db.query(User).filter(User.is_active == True).count(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching all users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users",
        )


@router.put("/admin/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    new_role: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user role (admin only)"""
    try:
        # Check if current user is admin
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        # Find target user
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Update role
        target_user.role = new_role
        target_user.updated_at = datetime.utcnow()
        db.commit()

        logger.info(f"User role updated: {target_user.email} -> {new_role}")

        return {"message": "User role updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role",
        )

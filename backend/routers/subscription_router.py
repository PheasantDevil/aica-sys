"""
Subscription Management Router
Handles subscription-related API endpoints for production revenue features
"""

import os
from datetime import datetime, timedelta
from typing import List, Optional

import stripe
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Request, status
from models.subscription import Subscription, SubscriptionPlan
from models.user import User
from security.auth_middleware import get_current_user
from sqlalchemy.orm import Session
from utils.logging import get_logger

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])
logger = get_logger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@router.get("/plans")
async def get_subscription_plans(db: Session = Depends(get_db)):
    """Get available subscription plans"""
    try:
        plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
        return {
            "plans": [
                {
                    "id": plan.id,
                    "name": plan.name,
                    "price": plan.price,
                    "currency": plan.currency,
                    "interval": plan.interval,
                    "features": plan.features,
                    "stripe_price_id": plan.stripe_price_id
                }
                for plan in plans
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching subscription plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscription plans"
        )

@router.get("/current")
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription"""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.status.in_(["active", "past_due", "canceled"])
        ).first()
        
        if not subscription:
            return {"subscription": None}
        
        return {
            "subscription": {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "plan": {
                    "name": subscription.plan.name,
                    "price": subscription.plan.price,
                    "currency": subscription.plan.currency,
                    "features": subscription.plan.features
                } if subscription.plan else None
            }
        }
    except Exception as e:
        logger.error(f"Error fetching current subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscription"
        )

@router.post("/create-checkout-session")
async def create_checkout_session(
    price_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe checkout session for subscription"""
    try:
        # Get the subscription plan
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.stripe_price_id == price_id
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription plan not found"
            )
        
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{os.getenv('NEXTAUTH_URL')}/dashboard/subscription?success=true",
            cancel_url=f"{os.getenv('NEXTAUTH_URL')}/pricing?canceled=true",
            metadata={
                'user_id': str(current_user.id),
                'plan_id': str(plan.id)
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

@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel current subscription"""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        # Cancel subscription in Stripe
        stripe_subscription = stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        # Update local subscription
        subscription.cancel_at_period_end = True
        subscription.status = "canceled"
        db.commit()
        
        return {
            "message": "Subscription canceled successfully",
            "cancel_at_period_end": subscription.current_period_end
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error canceling subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment processing error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )

@router.post("/reactivate")
async def reactivate_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reactivate canceled subscription"""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.status == "canceled"
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No canceled subscription found"
            )
        
        # Reactivate subscription in Stripe
        stripe_subscription = stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=False
        )
        
        # Update local subscription
        subscription.cancel_at_period_end = False
        subscription.status = "active"
        db.commit()
        
        return {
            "message": "Subscription reactivated successfully"
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error reactivating subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment processing error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error reactivating subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reactivate subscription"
        )

@router.get("/customer-portal")
async def create_customer_portal_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe customer portal session"""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No subscription found"
            )
        
        # Create customer portal session
        session = stripe.billing_portal.Session.create(
            customer=subscription.customer_id,
            return_url=f"{os.getenv('NEXTAUTH_URL')}/dashboard/subscription"
        )
        
        return {
            "portal_url": session.url
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating customer portal: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment processing error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating customer portal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create customer portal"
        )

# Webhook handlers for Stripe events
@router.post("/webhook")
async def handle_stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
        
        # Handle the event
        if event['type'] == 'customer.subscription.created':
            await handle_subscription_created(event['data']['object'], db)
        elif event['type'] == 'customer.subscription.updated':
            await handle_subscription_updated(event['data']['object'], db)
        elif event['type'] == 'customer.subscription.deleted':
            await handle_subscription_deleted(event['data']['object'], db)
        elif event['type'] == 'invoice.payment_succeeded':
            await handle_payment_succeeded(event['data']['object'], db)
        elif event['type'] == 'invoice.payment_failed':
            await handle_payment_failed(event['data']['object'], db)
        
        return {"status": "success"}
        
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook error")

async def handle_subscription_created(subscription_data, db: Session):
    """Handle subscription created webhook"""
    try:
        subscription = Subscription(
            stripe_subscription_id=subscription_data['id'],
            customer_id=subscription_data['customer'],
            user_id=subscription_data['metadata'].get('user_id'),
            status=subscription_data['status'],
            current_period_start=datetime.fromtimestamp(subscription_data['current_period_start']),
            current_period_end=datetime.fromtimestamp(subscription_data['current_period_end']),
            price_id=subscription_data['items']['data'][0]['price']['id']
        )
        db.add(subscription)
        db.commit()
        logger.info(f"Subscription created: {subscription_data['id']}")
    except Exception as e:
        logger.error(f"Error handling subscription created: {e}")

async def handle_subscription_updated(subscription_data, db: Session):
    """Handle subscription updated webhook"""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_data['id']
        ).first()
        
        if subscription:
            subscription.status = subscription_data['status']
            subscription.current_period_start = datetime.fromtimestamp(subscription_data['current_period_start'])
            subscription.current_period_end = datetime.fromtimestamp(subscription_data['current_period_end'])
            subscription.cancel_at_period_end = subscription_data['cancel_at_period_end']
            db.commit()
            logger.info(f"Subscription updated: {subscription_data['id']}")
    except Exception as e:
        logger.error(f"Error handling subscription updated: {e}")

async def handle_subscription_deleted(subscription_data, db: Session):
    """Handle subscription deleted webhook"""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_data['id']
        ).first()
        
        if subscription:
            subscription.status = 'canceled'
            db.commit()
            logger.info(f"Subscription deleted: {subscription_data['id']}")
    except Exception as e:
        logger.error(f"Error handling subscription deleted: {e}")

async def handle_payment_succeeded(invoice_data, db: Session):
    """Handle payment succeeded webhook"""
    try:
        if invoice_data['subscription']:
            subscription = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == invoice_data['subscription']
            ).first()
            
            if subscription:
                subscription.status = 'active'
                subscription.last_payment_date = datetime.now()
                db.commit()
                logger.info(f"Payment succeeded for subscription: {invoice_data['subscription']}")
    except Exception as e:
        logger.error(f"Error handling payment succeeded: {e}")

async def handle_payment_failed(invoice_data, db: Session):
    """Handle payment failed webhook"""
    try:
        if invoice_data['subscription']:
            subscription = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == invoice_data['subscription']
            ).first()
            
            if subscription:
                subscription.status = 'past_due'
                subscription.last_payment_failed_date = datetime.now()
                db.commit()
                logger.info(f"Payment failed for subscription: {invoice_data['subscription']}")
    except Exception as e:
        logger.error(f"Error handling payment failed: {e}")

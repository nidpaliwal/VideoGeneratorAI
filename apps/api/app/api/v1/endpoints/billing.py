from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import stripe
import structlog

from app.core.config import settings
from app.core.database import prisma
from app.api.v1.endpoints.auth import get_current_user

logger = structlog.get_logger()

router = APIRouter()

stripe.api_key = settings.STRIPE_SECRET_KEY


class CheckoutSessionRequest(BaseModel):
    priceId: str
    successUrl: str
    cancelUrl: str


class CheckoutSessionResponse(BaseModel):
    sessionId: str
    url: str


class SubscriptionResponse(BaseModel):
    id: str
    plan: str
    status: str
    currentPeriodEnd: str
    cancelAtPeriodEnd: bool


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    data: CheckoutSessionRequest,
    current_user: dict = Depends(get_current_user),
):
    if not current_user.get("stripeCustomerId"):
        customer = stripe.Customer.create(email=current_user["email"], metadata={"user_id": current_user["id"]})
        await prisma.user.update(
            where={"id": current_user["id"]},
            data={"stripeCustomerId": customer.id},
        )
        customer_id = customer.id
    else:
        customer_id = current_user["stripeCustomerId"]

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{"price": data.priceId, "quantity": 1}],
        mode="subscription",
        success_url=data.successUrl,
        cancel_url=data.cancelUrl,
        metadata={"user_id": current_user["id"]},
    )

    return CheckoutSessionResponse(sessionId=session.id, url=session.url)


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(current_user: dict = Depends(get_current_user)):
    if not current_user.get("stripeSubscriptionId"):
        return SubscriptionResponse(
            id="",
            plan=current_user["plan"],
            status="inactive",
            currentPeriodEnd="",
            cancelAtPeriodEnd=False,
        )

    sub = stripe.Subscription.retrieve(current_user["stripeSubscriptionId"])
    return SubscriptionResponse(
        id=sub.id,
        plan=current_user["plan"],
        status=sub.status,
        currentPeriodEnd=str(sub.current_period_end),
        cancelAtPeriodEnd=sub.cancel_at_period_end,
    )


@router.post("/portal")
async def create_portal_session(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    if not current_user.get("stripeCustomerId"):
        raise HTTPException(status_code=400, detail="No Stripe customer found")

    body = await request.json()
    return_url = body.get("returnUrl", "http://localhost:3000/dashboard")

    session = stripe.billing_portal.Session.create(
        customer=current_user["stripeCustomerId"],
        return_url=return_url,
    )

    return {"url": session.url}


@router.get("/usage")
async def get_usage(current_user: dict = Depends(get_current_user)):
    from datetime import datetime, timedelta

    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    usage = await prisma.usagelog.group_by(
        by=["action"],
        where={"userId": current_user["id"], "createdAt": {"gte": start_of_month}},
        _sum={"creditsCost": True},
    )

    return {
        "plan": current_user["plan"],
        "creditsRemaining": current_user["creditsRemaining"],
        "creditsUsed": current_user["creditsUsed"],
        "monthlyUsage": {u.action: u._sum.creditsCost or 0 for u in usage},
    }
from fastapi import APIRouter, Request, HTTPException, Header
import stripe
import structlog

from app.core.config import settings
from app.core.database import prisma

logger = structlog.get_logger()

router = APIRouter()

stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    logger.info("Stripe webhook received", type=event.type, id=event.id)

    if event.type == "checkout.session.completed":
        session = event.data.object
        user_id = session.metadata.get("user_id")
        if user_id:
            await handle_checkout_completed(user_id, session)

    elif event.type == "invoice.payment_succeeded":
        invoice = event.data.object
        customer_id = invoice.customer
        await handle_payment_succeeded(customer_id, invoice)

    elif event.type == "customer.subscription.updated":
        subscription = event.data.object
        await handle_subscription_updated(subscription)

    elif event.type == "customer.subscription.deleted":
        subscription = event.data.object
        await handle_subscription_deleted(subscription)

    return {"received": True}


async def handle_checkout_completed(user_id: str, session):
    subscription = stripe.Subscription.retrieve(session.subscription)
    price_id = subscription.items.data[0].price.id

    plan_map = {
        settings.STRIPE_PRICE_PRO: "PRO",
        settings.STRIPE_PRICE_CREATOR: "CREATOR",
    }
    plan = plan_map.get(price_id, "FREE")
    credits_map = {"PRO": 50, "CREATOR": 200, "FREE": 3}

    await prisma.user.update(
        where={"id": user_id},
        data={
            "plan": plan,
            "creditsRemaining": credits_map[plan],
            "stripeSubscriptionId": subscription.id,
        },
    )

    await prisma.subscription.upsert(
        where={"userId": user_id},
        data={
            "create": {
                "userId": user_id,
                "stripeSubscriptionId": subscription.id,
                "stripePriceId": price_id,
                "stripeCurrentPeriodEnd": subscription.current_period_end,
                "status": subscription.status.upper(),
            },
            "update": {
                "stripeSubscriptionId": subscription.id,
                "stripePriceId": price_id,
                "stripeCurrentPeriodEnd": subscription.current_period_end,
                "status": subscription.status.upper(),
            },
        },
    )

    logger.info("Subscription created", user_id=user_id, plan=plan)


async def handle_payment_succeeded(customer_id: str, invoice):
    user = await prisma.user.find_first(where={"stripeCustomerId": customer_id})
    if user and invoice.subscription:
        subscription = stripe.Subscription.retrieve(invoice.subscription)
        await prisma.subscription.update(
            where={"userId": user.id},
            data={
                "stripeCurrentPeriodEnd": subscription.current_period_end,
                "status": subscription.status.upper(),
            },
        )


async def handle_subscription_updated(subscription):
    customer_id = subscription.customer
    user = await prisma.user.find_first(where={"stripeCustomerId": customer_id})
    if user:
        price_id = subscription.items.data[0].price.id
        plan_map = {
            settings.STRIPE_PRICE_PRO: "PRO",
            settings.STRIPE_PRICE_CREATOR: "CREATOR",
        }
        plan = plan_map.get(price_id, "FREE")
        credits_map = {"PRO": 50, "CREATOR": 200, "FREE": 3}

        await prisma.user.update(
            where={"id": user.id},
            data={
                "plan": plan,
                "creditsRemaining": credits_map[plan],
            },
        )

        await prisma.subscription.update(
            where={"userId": user.id},
            data={
                "stripePriceId": price_id,
                "stripeCurrentPeriodEnd": subscription.current_period_end,
                "status": subscription.status.upper(),
                "cancelAtPeriodEnd": subscription.cancel_at_period_end,
            },
        )


async def handle_subscription_deleted(subscription):
    customer_id = subscription.customer
    user = await prisma.user.find_first(where={"stripeCustomerId": customer_id})
    if user:
        await prisma.user.update(
            where={"id": user.id},
            data={
                "plan": "FREE",
                "creditsRemaining": 3,
                "stripeSubscriptionId": None,
            },
        )
        await prisma.subscription.update(
            where={"userId": user.id},
            data={"status": "CANCELED"},
        )
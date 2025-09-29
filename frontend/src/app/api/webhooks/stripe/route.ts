import { headers } from 'next/headers';
import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
});

const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!;

export async function POST(request: NextRequest) {
  try {
    const body = await request.text();
    const signature = headers().get('stripe-signature')!;

    let event: Stripe.Event;

    try {
      event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
    } catch (err) {
      console.error('Webhook signature verification failed:', err);
      return NextResponse.json(
        { error: 'Webhook signature verification failed' },
        { status: 400 }
      );
    }

    console.log('Received webhook event:', event.type);

    // Handle the event
    switch (event.type) {
      case 'customer.subscription.created':
        await handleSubscriptionCreated(
          event.data.object as Stripe.Subscription
        );
        break;

      case 'customer.subscription.updated':
        await handleSubscriptionUpdated(
          event.data.object as Stripe.Subscription
        );
        break;

      case 'customer.subscription.deleted':
        await handleSubscriptionDeleted(
          event.data.object as Stripe.Subscription
        );
        break;

      case 'invoice.payment_succeeded':
        await handlePaymentSucceeded(event.data.object as Stripe.Invoice);
        break;

      case 'invoice.payment_failed':
        await handlePaymentFailed(event.data.object as Stripe.Invoice);
        break;

      case 'payment_intent.succeeded':
        await handlePaymentIntentSucceeded(
          event.data.object as Stripe.PaymentIntent
        );
        break;

      case 'checkout.session.completed':
        await handleCheckoutCompleted(
          event.data.object as Stripe.Checkout.Session
        );
        break;

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    return NextResponse.json({ received: true });
  } catch (error) {
    console.error('Webhook error:', error);
    return NextResponse.json(
      { error: 'Webhook handler failed' },
      { status: 500 }
    );
  }
}

async function handleSubscriptionCreated(subscription: Stripe.Subscription) {
  console.log('Subscription created:', subscription.id);

  try {
    // Update user subscription status in database
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/subscriptions`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          stripe_subscription_id: subscription.id,
          customer_id: subscription.customer as string,
          status: subscription.status,
          current_period_start: new Date(
            subscription.current_period_start * 1000
          ),
          current_period_end: new Date(subscription.current_period_end * 1000),
          price_id: subscription.items.data[0]?.price.id,
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to update subscription: ${response.statusText}`);
    }

    console.log('Subscription created successfully');
  } catch (error) {
    console.error('Error handling subscription creation:', error);
  }
}

async function handleSubscriptionUpdated(subscription: Stripe.Subscription) {
  console.log('Subscription updated:', subscription.id);

  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/subscriptions/${subscription.id}`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: subscription.status,
          current_period_start: new Date(
            subscription.current_period_start * 1000
          ),
          current_period_end: new Date(subscription.current_period_end * 1000),
          cancel_at_period_end: subscription.cancel_at_period_end,
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to update subscription: ${response.statusText}`);
    }

    console.log('Subscription updated successfully');
  } catch (error) {
    console.error('Error handling subscription update:', error);
  }
}

async function handleSubscriptionDeleted(subscription: Stripe.Subscription) {
  console.log('Subscription deleted:', subscription.id);

  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/subscriptions/${subscription.id}`,
      {
        method: 'DELETE',
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to delete subscription: ${response.statusText}`);
    }

    console.log('Subscription deleted successfully');
  } catch (error) {
    console.error('Error handling subscription deletion:', error);
  }
}

async function handlePaymentSucceeded(invoice: Stripe.Invoice) {
  console.log('Payment succeeded for invoice:', invoice.id);

  try {
    // Update subscription status to active
    if (invoice.subscription) {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/subscriptions/${invoice.subscription}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            status: 'active',
            last_payment_date: new Date(),
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Failed to update subscription: ${response.statusText}`
        );
      }
    }

    console.log('Payment succeeded handled successfully');
  } catch (error) {
    console.error('Error handling payment success:', error);
  }
}

async function handlePaymentFailed(invoice: Stripe.Invoice) {
  console.log('Payment failed for invoice:', invoice.id);

  try {
    // Update subscription status to past_due
    if (invoice.subscription) {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/subscriptions/${invoice.subscription}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            status: 'past_due',
            last_payment_failed_date: new Date(),
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Failed to update subscription: ${response.statusText}`
        );
      }
    }

    console.log('Payment failed handled successfully');
  } catch (error) {
    console.error('Error handling payment failure:', error);
  }
}

async function handlePaymentIntentSucceeded(
  paymentIntent: Stripe.PaymentIntent
) {
  console.log('Payment intent succeeded:', paymentIntent.id);

  try {
    // Handle one-time payments (like premium reports)
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/payments`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          stripe_payment_intent_id: paymentIntent.id,
          amount: paymentIntent.amount,
          currency: paymentIntent.currency,
          status: 'succeeded',
          metadata: paymentIntent.metadata,
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to record payment: ${response.statusText}`);
    }

    console.log('Payment intent succeeded handled successfully');
  } catch (error) {
    console.error('Error handling payment intent success:', error);
  }
}

async function handleCheckoutCompleted(session: Stripe.Checkout.Session) {
  console.log('Checkout session completed:', session.id);

  try {
    // Handle successful checkout completion
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/checkout/completed`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: session.id,
          customer_id: session.customer,
          subscription_id: session.subscription,
          payment_intent_id: session.payment_intent,
          metadata: session.metadata,
        }),
      }
    );

    if (!response.ok) {
      throw new Error(
        `Failed to handle checkout completion: ${response.statusText}`
      );
    }

    console.log('Checkout completion handled successfully');
  } catch (error) {
    console.error('Error handling checkout completion:', error);
  }
}

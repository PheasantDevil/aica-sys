import { prisma } from './prisma';
import { stripe } from './stripe-server';

export const PLANS = {
  FREE: {
    name: 'フリー',
    price: 0,
    features: [
      '週1回のトレンドレポート',
      '基本記事の閲覧',
      'コミュニティアクセス',
      'メールサポート',
    ],
    stripePriceId: null,
  },
  PREMIUM: {
    name: 'プレミアム',
    price: 1980,
    features: [
      '日次トレンドレポート',
      '全記事の閲覧',
      'プレミアムコンテンツ',
      '優先サポート',
      'API アクセス',
      'カスタム分析',
    ],
    stripePriceId: process.env.STRIPE_PREMIUM_PRICE_ID!,
  },
  ENTERPRISE: {
    name: 'エンタープライズ',
    price: 0, // カスタム価格
    features: [
      '無制限アクセス',
      'チーム管理機能',
      'カスタムブランディング',
      '専任サポート',
      'オンプレミス対応',
      'SLA保証',
    ],
    stripePriceId: null,
  },
} as const;

export type PlanType = keyof typeof PLANS;

export async function getUserSubscription(userId: string) {
  return await prisma.subscription.findUnique({
    where: { userId },
    include: { user: true },
  });
}

export async function createStripeCustomer(userId: string, email: string) {
  const customer = await stripe.customers.create({
    email,
    metadata: { userId },
  });

  await prisma.subscription.upsert({
    where: { userId },
    update: { stripeCustomerId: customer.id },
    create: {
      userId,
      stripeCustomerId: customer.id,
      status: 'inactive',
      plan: 'free',
    },
  });

  return customer;
}

export async function createCheckoutSession(
  userId: string,
  priceId: string,
  successUrl: string,
  cancelUrl: string
) {
  const subscription = await getUserSubscription(userId);

  if (!subscription?.stripeCustomerId) {
    throw new Error('Stripe customer not found');
  }

  const session = await stripe.checkout.sessions.create({
    customer: subscription.stripeCustomerId,
    payment_method_types: ['card'],
    line_items: [
      {
        price: priceId,
        quantity: 1,
      },
    ],
    mode: 'subscription',
    success_url: successUrl,
    cancel_url: cancelUrl,
    metadata: { userId },
  });

  return session;
}

export async function handleWebhook(event: Stripe.Event) {
  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object as Stripe.Checkout.Session;
      const userId = session.metadata?.userId;

      if (userId) {
        await prisma.subscription.update({
          where: { userId },
          data: {
            stripeSubscriptionId: session.subscription as string,
            status: 'active',
            plan: 'premium',
          },
        });
      }
      break;
    }

    case 'customer.subscription.updated': {
      const subscription = event.data.object as Stripe.Subscription;
      const customerId = subscription.customer as string;

      const dbSubscription = await prisma.subscription.findUnique({
        where: { stripeCustomerId: customerId },
      });

      if (dbSubscription) {
        await prisma.subscription.update({
          where: { id: dbSubscription.id },
          data: {
            status: subscription.status,
            stripeCurrentPeriodEnd: new Date(
              subscription.current_period_end * 1000
            ),
          },
        });
      }
      break;
    }

    case 'customer.subscription.deleted': {
      const subscription = event.data.object as Stripe.Subscription;
      const customerId = subscription.customer as string;

      const dbSubscription = await prisma.subscription.findUnique({
        where: { stripeCustomerId: customerId },
      });

      if (dbSubscription) {
        await prisma.subscription.update({
          where: { id: dbSubscription.id },
          data: {
            status: 'canceled',
            plan: 'free',
          },
        });
      }
      break;
    }
  }
}

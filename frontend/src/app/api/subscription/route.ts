import { getServerSession } from 'next-auth';
import { NextRequest, NextResponse } from 'next/server';
import { authOptions } from '../auth/[...nextauth]/route';

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);

    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // 実際の実装では、データベースからユーザーのサブスクリプション情報を取得
    const subscription = {
      id: 'sub_1234567890',
      status: 'active',
      plan: 'premium',
      planName: 'プレミアム',
      price: '¥1,980',
      period: '月',
      currentPeriodStart: '2024-09-01',
      currentPeriodEnd: '2024-10-01',
      cancelAtPeriodEnd: false,
      nextBillingDate: '2024-10-01',
      paymentMethod: {
        type: 'card',
        last4: '4242',
        brand: 'visa',
      },
    };

    return NextResponse.json(subscription);
  } catch (error) {
    console.error('Error fetching subscription:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function PUT(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);

    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json();
    const { action, planId } = body;

    // 実際の実装では、Stripe APIを呼び出してサブスクリプションを更新
    switch (action) {
      case 'cancel':
        console.log('Cancelling subscription for user:', session.user.email);
        // Stripe API call to cancel subscription
        break;
      case 'upgrade':
        console.log('Upgrading subscription to plan:', planId);
        // Stripe API call to upgrade subscription
        break;
      case 'downgrade':
        console.log('Downgrading subscription to plan:', planId);
        // Stripe API call to downgrade subscription
        break;
      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error updating subscription:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

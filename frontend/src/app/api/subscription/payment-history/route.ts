import { getServerSession } from 'next-auth';
import { NextRequest, NextResponse } from 'next/server';
import { authOptions } from '../../auth/[...nextauth]/route';

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);

    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // 実際の実装では、Stripe APIから支払い履歴を取得
    const paymentHistory = [
      {
        id: 'pi_1',
        amount: '¥1,980',
        status: 'succeeded',
        date: '2024-09-01',
        description: 'プレミアムプラン',
        invoiceUrl: 'https://invoice.stripe.com/i/acct_123/test_invoice',
      },
      {
        id: 'pi_2',
        amount: '¥1,980',
        status: 'succeeded',
        date: '2024-08-01',
        description: 'プレミアムプラン',
        invoiceUrl: 'https://invoice.stripe.com/i/acct_123/test_invoice',
      },
      {
        id: 'pi_3',
        amount: '¥1,980',
        status: 'succeeded',
        date: '2024-07-01',
        description: 'プレミアムプラン',
        invoiceUrl: 'https://invoice.stripe.com/i/acct_123/test_invoice',
      },
      {
        id: 'pi_4',
        amount: '¥1,980',
        status: 'succeeded',
        date: '2024-06-01',
        description: 'プレミアムプラン',
        invoiceUrl: 'https://invoice.stripe.com/i/acct_123/test_invoice',
      },
      {
        id: 'pi_5',
        amount: '¥1,980',
        status: 'succeeded',
        date: '2024-05-01',
        description: 'プレミアムプラン',
        invoiceUrl: 'https://invoice.stripe.com/i/acct_123/test_invoice',
      },
    ];

    return NextResponse.json(paymentHistory);
  } catch (error) {
    console.error('Error fetching payment history:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

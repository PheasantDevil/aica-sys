import { getServerSession } from 'next-auth';
import { NextRequest, NextResponse } from 'next/server';
import { authOptions } from '../../auth/[...nextauth]/route';

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);

    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // 実際の実装では、データベースからユーザーの利用状況を取得
    const usage = {
      articles: {
        current: 1234,
        limit: -1, // -1 means unlimited
        period: 'month',
      },
      newsletters: {
        current: 4,
        limit: -1, // -1 means unlimited
        period: 'month',
      },
      apiRequests: {
        current: 2456,
        limit: 10000,
        period: 'month',
      },
      storage: {
        current: 2.5, // GB
        limit: 10, // GB
        period: 'month',
      },
    };

    return NextResponse.json(usage);
  } catch (error) {
    console.error('Error fetching usage:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

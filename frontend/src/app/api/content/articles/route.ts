import axios from 'axios';
import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const queryString = searchParams.toString();
    const url = `${BACKEND_URL}/api/content/articles${
      queryString ? `?${queryString}` : ''
    }`;

    console.log('Proxying request to:', url);

    const response = await axios.get(url, {
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      timeout: 10000, // 10 second timeout
    });

    console.log('Backend response status:', response.status);
    console.log('Backend response data:', response.data);
    return NextResponse.json(response.data);
  } catch (error) {
    console.error('Error proxying to backend:', error);
    return NextResponse.json(
      {
        error: 'Failed to fetch articles',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

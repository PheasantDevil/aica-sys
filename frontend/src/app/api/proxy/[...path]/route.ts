import { NextRequest, NextResponse } from "next/server";
import { resolveBackendUrl } from "@/lib/backend-url";

const BACKEND_URL = resolveBackendUrl();

const METHODS_WITHOUT_BODY = new Set(["GET", "HEAD"]);
const CONTENT_FALLBACK_PATHS = new Set(["articles", "newsletters", "trends"]);

function resolveBackendPath(path: string): string {
  const firstSegment = path.split("/")[0];
  if (CONTENT_FALLBACK_PATHS.has(firstSegment)) {
    return `/api/content/${path}`;
  }
  return `/${path}`;
}

function getFallbackResponse(path: string): NextResponse | null {
  const firstSegment = path.split("/")[0];
  if (firstSegment === "articles") {
    return NextResponse.json({
      articles: [
        {
          id: "fallback-1",
          title: "TypeScript 5.0の新機能とベストプラクティス",
          description:
            "バックエンド疎通に失敗したため、フォールバック記事を表示しています。環境復旧後に最新データへ切り替わります。",
          content: "",
          category: "tutorial",
          tags: ["TypeScript", "Fallback"],
          publishedAt: "2024-01-15T10:00:00Z",
          readTime: 8,
          views: 1234,
          likes: 89,
          isPremium: false,
          author: { name: "AICA-SyS" },
        },
      ],
      total: 1,
      fallback: true,
    });
  }

  if (firstSegment === "newsletters") {
    return NextResponse.json({
      newsletters: [
        {
          id: "fallback-newsletter-1",
          title: "TypeScript Weekly フォールバック版",
          description: "バックエンド未接続時の代替ニュースレターです。",
          content: "",
          publishedAt: "2024-01-15T10:00:00Z",
          subscribers: 1000,
          openRate: 75,
          clickRate: 25,
          isPremium: false,
          tags: ["Fallback"],
        },
      ],
      total: 1,
      fallback: true,
    });
  }

  if (firstSegment === "trends") {
    return NextResponse.json({
      trends: [
        {
          id: "fallback-trend-1",
          title: "TypeScript 5.0 Adoption",
          description: "バックエンド未接続時の代替トレンドデータです。",
          category: "language",
          trendScore: 85,
        },
      ],
      total: 1,
      fallback: true,
    });
  }

  return null;
}

async function forwardToBackend(
  request: NextRequest,
  { params }: { params: { path: string[] } },
): Promise<NextResponse> {
  const path = params.path?.join("/") || "";
  const backendPath = resolveBackendPath(path);
  const targetUrl = new URL(backendPath, BACKEND_URL);
  targetUrl.search = request.nextUrl.search;

  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("connection");
  headers.delete("content-length");

  const body = METHODS_WITHOUT_BODY.has(request.method) ? undefined : await request.arrayBuffer();

  try {
    const response = await fetch(targetUrl.toString(), {
      method: request.method,
      headers,
      body,
      redirect: "manual",
    });

    if (!response.ok) {
      const fallbackResponse = getFallbackResponse(path);
      if (fallbackResponse && (response.status === 404 || response.status >= 500)) {
        return fallbackResponse;
      }
    }

    return new NextResponse(response.body, {
      status: response.status,
      headers: response.headers,
    });
  } catch (error) {
    const fallbackResponse = getFallbackResponse(path);
    if (fallbackResponse) {
      return fallbackResponse;
    }

    return NextResponse.json(
      {
        error: "Failed to proxy request",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 502 },
    );
  }
}

export async function GET(request: NextRequest, context: { params: { path: string[] } }) {
  return forwardToBackend(request, context);
}

export async function POST(request: NextRequest, context: { params: { path: string[] } }) {
  return forwardToBackend(request, context);
}

export async function PUT(request: NextRequest, context: { params: { path: string[] } }) {
  return forwardToBackend(request, context);
}

export async function PATCH(request: NextRequest, context: { params: { path: string[] } }) {
  return forwardToBackend(request, context);
}

export async function DELETE(request: NextRequest, context: { params: { path: string[] } }) {
  return forwardToBackend(request, context);
}

export async function OPTIONS(request: NextRequest, context: { params: { path: string[] } }) {
  return forwardToBackend(request, context);
}

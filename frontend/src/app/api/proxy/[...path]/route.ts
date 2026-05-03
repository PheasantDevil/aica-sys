import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const METHODS_WITHOUT_BODY = new Set(["GET", "HEAD"]);

async function forwardToBackend(
  request: NextRequest,
  { params }: { params: { path: string[] } },
): Promise<NextResponse> {
  const path = params.path?.join("/") || "";
  const targetUrl = new URL(`/${path}`, BACKEND_URL);
  targetUrl.search = request.nextUrl.search;

  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("connection");
  headers.delete("content-length");

  const body = METHODS_WITHOUT_BODY.has(request.method) ? undefined : await request.arrayBuffer();

  const response = await fetch(targetUrl.toString(), {
    method: request.method,
    headers,
    body,
    redirect: "manual",
  });

  return new NextResponse(response.body, {
    status: response.status,
    headers: response.headers,
  });
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

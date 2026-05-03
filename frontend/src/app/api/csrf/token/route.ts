import { NextRequest, NextResponse } from "next/server";
import { csrfProtection } from "@/lib/csrf";
import { randomUUID } from "crypto";

export async function GET(request: NextRequest) {
  try {
    const sessionId = request.cookies.get("csrf_session_id")?.value || randomUUID();

    // CSRFトークンを生成
    const token = csrfProtection.generateToken(sessionId);

    const response = NextResponse.json({ token });
    response.cookies.set("csrf_session_id", sessionId, {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 60 * 60 * 24 * 30,
    });
    return response;
  } catch (error) {
    console.error("CSRF token generation error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

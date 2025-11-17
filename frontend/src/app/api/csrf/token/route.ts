import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { csrfProtection } from "@/lib/csrf";

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);

    if (!session?.user?.email) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // セッションIDを生成（実際の実装では適切なセッションIDを使用）
    const sessionId = session.user.email;

    // CSRFトークンを生成
    const token = csrfProtection.generateToken(sessionId);

    return NextResponse.json({ token });
  } catch (error) {
    console.error("CSRF token generation error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

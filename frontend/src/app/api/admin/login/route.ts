import { NextRequest, NextResponse } from "next/server";

const MAX_AGE_SECONDS = 60 * 60 * 12; // 12 hours

export async function POST(request: NextRequest) {
  try {
    const { passcode } = await request.json();

    if (!passcode) {
      return NextResponse.json({ error: "アクセスキーを入力してください" }, { status: 400 });
    }

    const expectedPasscode = process.env.ADMIN_ACCESS_CODE;

    if (!expectedPasscode) {
      return NextResponse.json(
        {
          error:
            "管理者アクセスキーが設定されていません。サーバー環境変数 ADMIN_ACCESS_CODE を設定してください。",
        },
        { status: 500 },
      );
    }

    if (passcode !== expectedPasscode) {
      return NextResponse.json({ error: "アクセスキーが正しくありません" }, { status: 401 });
    }

    const response = NextResponse.json({ success: true });
    response.cookies.set("admin_access", "granted", {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: MAX_AGE_SECONDS,
    });

    return response;
  } catch (error) {
    console.error("Admin login error", error);
    return NextResponse.json({ error: "ログイン処理に失敗しました" }, { status: 500 });
  }
}

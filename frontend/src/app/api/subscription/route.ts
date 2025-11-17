import { authOptions } from "@/lib/auth";
import { getUserSubscription } from "@/lib/subscription";
import { getServerSession } from "next-auth";
import { NextResponse } from "next/server";

export async function GET() {
  try {
    const session = await getServerSession(authOptions);

    if (!session?.user?.email) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const subscription = await getUserSubscription(session.user.email);

    return NextResponse.json(subscription);
  } catch (error) {
    console.error("Subscription fetch error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

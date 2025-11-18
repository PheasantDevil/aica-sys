"use client";

import { Button } from "@/components/ui/button";
import { LogOut, User } from "lucide-react";
import { signIn, signOut, useSession } from "next-auth/react";

export function SignInButton() {
  const { data: session, status } = useSession();

  if (status === "loading") {
    return <Button disabled>読み込み中...</Button>;
  }

  if (session) {
    return (
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-2">
          <User className="h-4 w-4" />
          <span className="text-sm">{session.user?.name || session.user?.email}</span>
        </div>
        <Button variant="outline" size="sm" onClick={() => signOut()}>
          <LogOut className="h-4 w-4 mr-2" />
          ログアウト
        </Button>
      </div>
    );
  }

  return <Button onClick={() => signIn("google")}>Googleでログイン</Button>;
}

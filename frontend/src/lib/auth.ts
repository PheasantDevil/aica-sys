import { PrismaAdapter } from "@auth/prisma-adapter";
import { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import { prisma } from "./prisma";

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      authorization: {
        params: {
          scope: "openid email profile",
          prompt: "consent",
          access_type: "offline",
          response_type: "code",
        },
      },
    }),
  ],
  callbacks: {
    async signIn({ user, account, profile }) {
      // 本番環境でのサインイン制御
      if (process.env.NODE_ENV === "production") {
        // 必要に応じてドメイン制限を追加
        // if (user.email && !user.email.endsWith('@allowed-domain.com')) {
        //   return false;
        // }
      }
      return true;
    },
    async session({ session, token, user }) {
      if (session?.user && token?.sub) {
        (session.user as any).id = token.sub;
        (session.user as any).role = token.role || "user";
        (session.user as any).subscription = token.subscription || null;
      }
      return session;
    },
    async jwt({ token, user, account, profile }) {
      if (user) {
        token.uid = user.id;
        token.role = "user"; // デフォルトロール
      }

      // Google OAuth情報の保存
      if (account && profile) {
        token.googleId = profile.sub;
        token.email = profile.email;
        token.name = profile.name;
        // @ts-ignore - profile.picture exists in Google profile
        token.picture = profile.picture;
      }

      return token;
    },
    async redirect({ url, baseUrl }) {
      // 本番環境でのリダイレクト制御
      if (url.startsWith("/")) return `${baseUrl}${url}`;
      if (new URL(url).origin === baseUrl) return url;
      return baseUrl;
    },
  },
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30日
    updateAge: 24 * 60 * 60, // 24時間
  },
  jwt: {
    maxAge: 30 * 24 * 60 * 60, // 30日
  },
  pages: {
    signIn: "/auth/signin",
    error: "/auth/error",
    signOut: "/auth/signout",
  },
  events: {
    async signIn({ user, account, profile, isNewUser }) {
      console.log("User signed in:", { user: user.email, isNewUser });
    },
    async signOut({ session, token }) {
      console.log("User signed out:", { user: session?.user?.email });
    },
    async createUser({ user }) {
      console.log("New user created:", { user: user.email });
    },
  },
  debug: process.env.NODE_ENV === "development",
  secret: process.env.NEXTAUTH_SECRET,
};

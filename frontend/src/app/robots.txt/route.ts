import { NextRequest, NextResponse } from "next/server";

const SITE_URL = process.env.NEXT_PUBLIC_BASE_URL || "https://aica-sys.vercel.app";

export async function GET(request: NextRequest) {
  try {
    const robotsTxt = generateRobotsTxt();

    return new NextResponse(robotsTxt, {
      status: 200,
      headers: {
        "Content-Type": "text/plain",
        "Cache-Control": "public, max-age=86400, s-maxage=86400", // 24時間キャッシュ
      },
    });
  } catch (error) {
    console.error("Error generating robots.txt:", error);
    return new NextResponse("Error generating robots.txt", { status: 500 });
  }
}

function generateRobotsTxt(): string {
  const isProduction = process.env.NODE_ENV === "production";

  if (!isProduction) {
    // 開発環境では全てのクローラーをブロック
    return `User-agent: *
Disallow: /

# Development environment - all crawling blocked
# Generated at: ${new Date().toISOString()}`;
  }

  // 本番環境のrobots.txt
  return `User-agent: *
Allow: /

# Sitemap
Sitemap: ${SITE_URL}/sitemap.xml

# Disallow sensitive areas
Disallow: /api/
Disallow: /admin/
Disallow: /dashboard/
Disallow: /monitoring/
Disallow: /_next/
Disallow: /auth/
Disallow: /checkout/
Disallow: /webhooks/

# Allow important pages
Allow: /articles/
Allow: /newsletters/
Allow: /trends/
Allow: /pricing/
Allow: /about/
Allow: /contact/

# Crawl delay for respectful crawling
Crawl-delay: 1

# Generated at: ${new Date().toISOString()}`;
}

import { ImageResponse } from "next/og";

export const runtime = "edge";

const IMAGE_WIDTH = 1200;
const IMAGE_HEIGHT = 630;

const gradients = {
  dark: {
    background: "#050816",
    gradientFrom: "#0f172a",
    gradientTo: "#1e293b",
    title: "#f8fafc",
    description: "#cbd5f5",
    accent: "#38bdf8",
    badgeBg: "rgba(56, 189, 248, 0.18)",
    badgeText: "#bae6fd",
  },
  light: {
    background: "#f8fafc",
    gradientFrom: "#e0f2fe",
    gradientTo: "#e2e8f0",
    title: "#0f172a",
    description: "#334155",
    accent: "#2563eb",
    badgeBg: "rgba(37, 99, 235, 0.15)",
    badgeText: "#1d4ed8",
  },
} as const;

const defaultDescription =
  "TypeScriptエコシステム特化のAI自動コンテンツ生成プラットフォーム AICA-SyS";

function normalizeText(value: string | null, fallback: string, maxLength: number) {
  if (!value) return fallback;
  if (value.length <= maxLength) return value;
  return `${value.substring(0, maxLength - 1)}…`;
}

function parseHashtags(rawTags: string | null): string[] {
  if (!rawTags) {
    return ["TypeScript", "AI自動生成", "Next.js"];
  }

  return rawTags
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean)
    .slice(0, 4);
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const theme = searchParams.get("theme") === "light" ? "light" : "dark";
  const palette = gradients[theme];

  const title = normalizeText(searchParams.get("title"), "AICA-SyS 最新記事", 70);
  const description = normalizeText(searchParams.get("description"), defaultDescription, 120);
  const badge = normalizeText(searchParams.get("badge"), "AI × TypeScript Automation", 40);
  const slug = normalizeText(searchParams.get("slug"), "aica-sys", 40);
  const hashtags = parseHashtags(searchParams.get("tags"));

  try {
    return new ImageResponse(
      (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            width: "100%",
            height: "100%",
            background: palette.background,
            backgroundImage: `linear-gradient(135deg, ${palette.gradientFrom}, ${palette.gradientTo})`,
            padding: "64px 72px",
            fontFamily: "Noto Sans JP, Inter, sans-serif",
            position: "relative",
          }}
        >
          <div
            style={{
              position: "absolute",
              inset: "32px",
              border:
                theme === "dark"
                  ? "1px solid rgba(255,255,255,0.08)"
                  : "1px solid rgba(15,23,42,0.08)",
              borderRadius: "32px",
              pointerEvents: "none",
            }}
          />

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "36px",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                fontSize: 28,
                fontWeight: 700,
                color: palette.title,
                gap: 12,
              }}
            >
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: "14px",
                  background: palette.accent,
                  color: "#0f172a",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: 800,
                  fontSize: 24,
                }}
              >
                AI
              </div>
              <span>AICA-SyS</span>
            </div>

            <div
              style={{
                fontSize: 22,
                color: palette.badgeText,
                background: palette.badgeBg,
                padding: "8px 18px",
                borderRadius: "999px",
              }}
            >
              {badge}
            </div>
          </div>

          <div
            style={{
              fontSize: 60,
              fontWeight: 700,
              color: palette.title,
              lineHeight: 1.2,
            }}
          >
            {title}
          </div>

          <div
            style={{
              fontSize: 28,
              color: palette.description,
              marginTop: 28,
              lineHeight: 1.4,
              maxWidth: "90%",
            }}
          >
            {description}
          </div>

          <div
            style={{
              marginTop: "auto",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-end",
              color: palette.description,
              fontSize: 24,
            }}
          >
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <span>www.aica-sys.com/articles/{slug}</span>
              <div style={{ display: "flex", gap: 16 }}>
                {hashtags.map((tag) => (
                  <span key={tag} style={{ color: palette.title, fontWeight: 600 }}>
                    #{tag.replace(/^#/, "")}
                  </span>
                ))}
              </div>
            </div>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "flex-end",
                fontSize: 22,
                textAlign: "right",
              }}
            >
              <span style={{ color: palette.description }}>Powered by</span>
              <span style={{ fontWeight: 700, color: palette.title }}>
                AICA-SyS Automation Stack
              </span>
            </div>
          </div>
        </div>
      ),
      {
        width: IMAGE_WIDTH,
        height: IMAGE_HEIGHT,
        headers: {
          "Cache-Control": "public, s-maxage=86400, stale-while-revalidate=43200",
        },
      },
    );
  } catch (error) {
    console.error("[OG] Failed to generate image", error);
    return new Response("Failed to generate OGP image", { status: 500 });
  }
}

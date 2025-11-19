#!/usr/bin/env node
/**
 * 簡易 OGP プレビュー取得スクリプト
 * 事前に `npm run dev` (frontend) を起動し、http://localhost:3000 を Listen させてください。
 */
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

const args = process.argv.slice(2);
const options = {
  title: "AICA-SyS 最新記事",
  description: "TypeScriptエコシステムの最新トレンドと自動化ノウハウを厳選してお届けします。",
  slug: "sample-article",
  tags: "TypeScript,AI自動生成,Next.js",
  theme: "dark",
  out: "tmp/og-previews",
  baseUrl: process.env.OG_PREVIEW_URL || "http://localhost:3000",
};

for (const arg of args) {
  const [rawKey, ...rest] = arg.replace(/^--/, "").split("=");
  const key = rawKey.trim();
  const value = rest.length ? rest.join("=") : "true";
  if (key && value) {
    options[key] = value;
  }
}

const params = new URLSearchParams({
  title: options.title,
  description: options.description,
  slug: options.slug,
  tags: options.tags,
  theme: options.theme,
});

const targetUrl = `${options.baseUrl.replace(/\/$/, "")}/api/og?${params.toString()}`;

console.log(`Fetching OGP image from ${targetUrl}`);
const response = await fetch(targetUrl);

if (!response.ok) {
  console.error(`Failed to fetch OGP image: ${response.status} ${response.statusText}`);
  process.exit(1);
}

const arrayBuffer = await response.arrayBuffer();
const buffer = Buffer.from(arrayBuffer);

const outputDir = path.resolve(process.cwd(), options.out);
await mkdir(outputDir, { recursive: true });

const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
const outputPath = path.join(outputDir, `${options.slug || "preview"}-${timestamp}.png`);

await writeFile(outputPath, buffer);
console.log(`OGP image saved to ${outputPath}`);
console.log("※ ローカル確認後に Vercel デプロイで自動反映されます。");


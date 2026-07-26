import type { Metadata } from "next";
import "./globals.css";

const title = "AIGCDataHub — 模型背后的数据策略";
const description =
  "持续追踪最新 AIGC 模型、训练数据策略与可用数据集，并明确记录公开信息与未知项。";
const githubPages = process.env.GITHUB_PAGES === "true";
const origin = "https://tobinzuo.github.io/AIGCDataHub";
const assetBase = githubPages ? "/AIGCDataHub" : "";

const imageUrl = `${origin}/og.png`;

export const metadata: Metadata = {
  metadataBase: new URL(origin),
  title,
  description,
  keywords: [
    "AIGC",
    "生成式 AI",
    "训练数据",
    "数据集",
    "多模态模型",
    "data strategy",
  ],
  authors: [{ name: "AIGCDataHub" }],
  icons: {
    icon: `${assetBase}/favicon.svg`,
    shortcut: `${assetBase}/favicon.svg`,
  },
  openGraph: {
    title,
    description,
    type: "website",
    url: origin,
    images: [{ url: imageUrl, width: 1200, height: 630, alt: "AIGCDataHub — Models to Data" }],
  },
  twitter: {
    card: "summary_large_image",
    title,
    description,
    images: [imageUrl],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}

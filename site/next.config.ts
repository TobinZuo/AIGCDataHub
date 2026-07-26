import type { NextConfig } from "next";

const isGitHubPages = process.env.GITHUB_PAGES === "true";

const nextConfig: NextConfig = {
  output: isGitHubPages ? "export" : undefined,
  basePath: isGitHubPages ? "/AIGCDataHub" : "",
  assetPrefix: isGitHubPages ? "/AIGCDataHub/" : "",
  trailingSlash: isGitHubPages,
  images: {
    unoptimized: isGitHubPages,
  },
  turbopack: {
    root: process.cwd(),
  },
};

export default nextConfig;

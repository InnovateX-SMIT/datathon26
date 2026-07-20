import type { NextConfig } from "next";

const isProd = process.env.NODE_ENV === "production";

const nextConfig: NextConfig = {
  /* config options here */
  devIndicators: false,
  output: 'export',
  images: {
    unoptimized: true,
  },
  basePath: isProd ? "/app" : undefined,
};

export default nextConfig;

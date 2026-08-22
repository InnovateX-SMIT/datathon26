import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  devIndicators: false,
  experimental: {
    serverActions: {
      bodySizeLimit: "100mb",
    },
  },

  images: {
    unoptimized: true,
  },

  // External proxy rewrites for Zoho Catalyst Slate deployment
  async rewrites() {
    return [
      {
        source: "/backend/:path*",
        destination:
          "https://crimenexus-backend-50045204017.development.catalystappsail.in/:path*",
      },
    ];
  },
};

export default nextConfig;

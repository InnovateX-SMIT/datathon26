import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  devIndicators: false,

  images: {
    unoptimized: true,
  },

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

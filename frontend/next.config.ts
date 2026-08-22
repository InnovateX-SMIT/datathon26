import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  devIndicators: false,

  images: {
    unoptimized: true,
  },

  async rewrites() {
    const isDev = process.env.NODE_ENV === "development";
    return [
      {
        source: "/backend/:path*",
        destination: isDev
          ? "http://127.0.0.1:8000/:path*"
          : "https://crimenexus-backend-50045204017.development.catalystappsail.in/:path*",
      },
    ];
  },
};

export default nextConfig;

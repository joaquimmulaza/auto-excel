/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  // Optional: when BACKEND_URL is set (separate API host), proxy /api/v1 through Next.
  // Prefer Vercel Services rewrites at repo-root vercel.json for production.
  async rewrites() {
    const backend = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL;
    if (!backend) return [];
    const base = backend.replace(/\/$/, "");
    return [
      {
        source: "/api/v1/:path*",
        destination: `${base}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;

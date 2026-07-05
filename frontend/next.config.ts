import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Remove 'standalone' for Vercel deployments
  // Vercel handles its own optimized output format
  turbopack: {
    root: __dirname,
  },

  cacheComponents: true,
};

export default nextConfig;

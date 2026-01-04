import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Enable standalone output for Docker deployments
  // Comment out for Vercel deployments (Vercel handles its own optimization)
  output: 'standalone',
  turbopack: {
    root: __dirname,
  },
};

export default nextConfig;

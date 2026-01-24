// Next.js configuration with PWA and API rewrite
const withPWA = require('next-pwa')({
  dest: 'public',
  // Disable PWA in development to reduce Workbox warnings and avoid SW caching during dev
  disable: process.env.NODE_ENV === 'development',
  register: true,
  skipWaiting: true
});

/** @type {import('next').NextConfig} */
const baseConfig = {
  reactStrictMode: true,
  eslint: {
    // Allow builds to complete even with ESLint warnings
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Allow builds to complete even with TypeScript errors (for demo)
    ignoreBuildErrors: true,
  },
  async rewrites() {
    // Only add rewrites if API base is set (for local dev with Python backend)
    const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL;
    if (!apiBase) {
      return [];
    }
    return [
      {
        source: '/api/:path*',
        destination: `${apiBase}/:path*`
      },
      // Proxy media assets served by FastAPI (images/audio)
      {
        source: '/media/:path*',
        destination: `${apiBase}/media/:path*`
      }
    ];
  }
};

module.exports = withPWA(baseConfig);

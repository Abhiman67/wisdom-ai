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
  async rewrites() {
    // Dev proxy: route /api/* to backend
    const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
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

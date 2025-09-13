/** @type {import('next').NextConfig} */
const nextConfig = {
  // appDir is now stable and enabled by default in Next.js 14+
  // Port configuration
  env: {
    PORT: process.env.PORT || '4000',
  },
}

module.exports = nextConfig 
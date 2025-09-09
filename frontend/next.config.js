/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['images.unsplash.com', 'via.placeholder.com'],
  },
  env: {
    NEXTAUTH_URL: process.env.NEXTAUTH_URL || 'http://localhost:3000',
    NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET || 'your-secret-key',
    GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID || '',
    GOOGLE_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET || '',
    STRIPE_PUBLISHABLE_KEY: process.env.STRIPE_PUBLISHABLE_KEY || '',
    STRIPE_SECRET_KEY: process.env.STRIPE_SECRET_KEY || '',
  },
};

module.exports = nextConfig;

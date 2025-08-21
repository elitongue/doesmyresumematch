/** @type {import('next').NextConfig} */
const basePath = process.env.BASE_PATH || '';

const nextConfig = {
  output: 'export',
  images: { unoptimized: true },
  assetPrefix: basePath ? `${basePath}/` : undefined,
  basePath,
};

module.exports = nextConfig;

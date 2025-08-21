// apps/web/next.config.js
const defaultBase = process.env.NODE_ENV === 'production' ? '/doesmyresumematch' : '';
const basePath = process.env.BASE_PATH ?? defaultBase;
/** @type {import('next').NextConfig} */
module.exports = {
  output: 'export',
  basePath,
  assetPrefix: basePath ? `${basePath}/` : undefined,
  images: { unoptimized: true },
  trailingSlash: true,
};

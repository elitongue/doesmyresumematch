const basePath = process.env.BASE_PATH || '';

/** @type {import('next').NextConfig} */
module.exports = {
  output: 'export',
  basePath,
  assetPrefix: basePath ? `${basePath}/` : undefined,
  images: { unoptimized: true },
  trailingSlash: true,
};

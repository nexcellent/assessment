/** @type {import('next').NextConfig} */
const nextConfig = {
  // Produces .next/standalone, which the container runs with `node server.js` (see Dockerfile).
  output: 'standalone',
};

export default nextConfig;

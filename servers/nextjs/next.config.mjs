
// 开发 (next dev) 用 .next，避免与预编译/生产的 .next-build 混用导致 /_next/static/... 404
const nextConfig = {
  reactStrictMode: false,
  distDir: process.env.NEXT_DIST_DIR || ".next",

  // 禁用构建时字体下载（容器内可能无法访问 Google Fonts）
  optimizeFonts: false,
  

  // Rewrites for development - proxy font requests and API requests to FastAPI backend
  async rewrites() {
    return [
      {
        source: '/app_data/fonts/:path*',
        destination: 'http://localhost:8000/app_data/fonts/:path*',
      },
      {
        source: '/api/v1/:path*',
        destination: 'http://localhost:8000/api/v1/:path*',
      },
    ];
  },

  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "pub-7c765f3726084c52bcd5d180d51f1255.r2.dev",
      },
      {
        protocol: "https",
        hostname: "pptgen-public.ap-south-1.amazonaws.com",
      },
      {
        protocol: "https",
        hostname: "pptgen-public.s3.ap-south-1.amazonaws.com",
      },
      {
        protocol: "https",
        hostname: "img.icons8.com",
      },
      {
        protocol: "https",
        hostname: "present-for-me.s3.amazonaws.com",
      },
      {
        protocol: "https",
        hostname: "yefhrkuqbjcblofdcpnr.supabase.co",
      },
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
      {
        protocol: "https",
        hostname: "picsum.photos",
      },
      {
        protocol: "https",
        hostname: "unsplash.com",
      },
    ],
  },
  
};

export default nextConfig;

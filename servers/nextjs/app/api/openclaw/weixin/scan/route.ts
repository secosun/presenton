import { NextResponse } from "next/server";

const OPENCLAW_GATEWAY_BASE = process.env.OPENCLAW_GATEWAY_BASE || process.env.NEXT_PUBLIC_OPENCLAW_GATEWAY_BASE || "https://ppt.installall.cn";
const OPENCLAW_GATEWAY_TOKEN = process.env.OPENCLAW_GATEWAY_TOKEN || process.env.NEXT_PUBLIC_OPENCLAW_GATEWAY_TOKEN || "openclaw-distributed-secret-key";

export async function GET(request: Request) {
  try {
    // 代理请求到网关，token 只在服务端使用，前端不可见
    const targetUrl = `${OPENCLAW_GATEWAY_BASE}/__openclaw__/weixin/scan?token=${encodeURIComponent(OPENCLAW_GATEWAY_TOKEN)}`;

    const response = await fetch(targetUrl, {
      headers: {
        "Content-Type": "text/html; charset=utf-8",
      },
    });

    const html = await response.text();

    // 返回 HTML 内容，前端通过 iframe 加载
    return new NextResponse(html, {
      headers: {
        "Content-Type": "text/html; charset=utf-8",
      },
    });
  } catch (error) {
    return NextResponse.json(
      { error: "网关连接失败" },
      { status: 503 }
    );
  }
}

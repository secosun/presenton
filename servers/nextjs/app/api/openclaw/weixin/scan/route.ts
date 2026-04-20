import { NextResponse } from "next/server";
import {
  getOpenClawGatewayBaseForServer,
  getOpenClawGatewayTokenForServer,
  openClawGatewayBaseMissingMessage,
} from "@/lib/openclaw-gateway-server-config";

export async function GET() {
  try {
    const OPENCLAW_GATEWAY_BASE = getOpenClawGatewayBaseForServer();
    if (!OPENCLAW_GATEWAY_BASE) {
      return NextResponse.json({ error: openClawGatewayBaseMissingMessage() }, { status: 503 });
    }
    const OPENCLAW_GATEWAY_TOKEN = getOpenClawGatewayTokenForServer();

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

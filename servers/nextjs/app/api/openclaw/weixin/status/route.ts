import { NextResponse } from "next/server";
import {
  getOpenClawGatewayBaseForServer,
  getOpenClawGatewayTokenForServer,
  openClawGatewayBaseMissingMessage,
} from "@/lib/openclaw-gateway-server-config";

export const dynamic = "force-dynamic";
export const fetchCache = "force-no-store";

export async function POST(request: Request) {
  try {
    const OPENCLAW_GATEWAY_BASE = getOpenClawGatewayBaseForServer();
    if (!OPENCLAW_GATEWAY_BASE) {
      return NextResponse.json(
        { status: "error", message: openClawGatewayBaseMissingMessage() },
        { status: 503 },
      );
    }
    const OPENCLAW_GATEWAY_TOKEN = getOpenClawGatewayTokenForServer();

    const { sessionKey } = await request.json();

    if (!sessionKey) {
      return NextResponse.json(
        { error: "缺少 sessionKey" },
        { status: 400 }
      );
    }

    // 代理请求到网关
    const targetUrl = `${OPENCLAW_GATEWAY_BASE}/__openclaw__/weixin/login/wait`;
    const response = await fetch(targetUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${OPENCLAW_GATEWAY_TOKEN}`,
      },
      body: JSON.stringify({
        sessionKey,
        timeoutMs: 55000,
      }),
      cache: "no-store",
    });

    // 检查 Gateway 响应状态
    if (!response.ok) {
      const errorText = await response.text();
      console.error("Gateway 状态查询失败:", response.status, errorText.substring(0, 200));
      return NextResponse.json(
        { status: "error", message: `网关服务异常 (${response.status})` },
        {
          status: response.status,
          headers: {
            "Cache-Control": "no-cache, no-store, must-revalidate",
          },
        }
      );
    }

    const data = await response.json();

    const headers = {
      "Cache-Control": "no-cache, no-store, must-revalidate",
    };

    if (data.connected) {
      return NextResponse.json(
        {
          status: "success",
          message: "绑定成功！",
          data: data,
        },
        { headers }
      );
    }

    // 检查是否过期（Gateway 返回 message 包含"超时"或"过期"）
    const msg = (data.message || "").toLowerCase();
    if (msg.includes("超时") || msg.includes("过期") || msg.includes("expired")) {
      return NextResponse.json(
        {
          status: "expired",
          message: data.message || "二维码已过期",
        },
        { headers }
      );
    }

    // 其他情况继续等待
    return NextResponse.json(
      {
        status: "waiting",
        message: data.message || "等待扫码...",
      },
      { headers }
    );
  } catch (error) {
    return NextResponse.json(
      { status: "error", message: "状态查询失败" },
      {
        status: 500,
        headers: {
          "Cache-Control": "no-cache, no-store, must-revalidate",
        },
      }
    );
  }
}

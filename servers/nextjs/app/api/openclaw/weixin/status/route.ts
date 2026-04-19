import { NextResponse } from "next/server";

const OPENCLAW_GATEWAY_BASE = process.env.OPENCLAW_GATEWAY_BASE || process.env.NEXT_PUBLIC_OPENCLAW_GATEWAY_BASE || "https://ppt.installall.cn";
const OPENCLAW_GATEWAY_TOKEN = process.env.OPENCLAW_GATEWAY_TOKEN || process.env.NEXT_PUBLIC_OPENCLAW_GATEWAY_TOKEN || "openclaw-distributed-secret-key";

export async function POST(request: Request) {
  try {
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
    });

    const data = await response.json();

    if (data.connected) {
      return NextResponse.json({
        status: "success",
        message: "绑定成功！",
        data: data,
      });
    } else if (data.scanned) {
      return NextResponse.json({
        status: "scanned",
        message: "已扫码，请在手机上确认",
        data: data,
      });
    } else if (data.expired) {
      return NextResponse.json({
        status: "expired",
        message: "二维码已过期",
      });
    } else {
      return NextResponse.json({
        status: "waiting",
        message: "等待扫码...",
      });
    }
  } catch (error) {
    return NextResponse.json(
      { status: "error", message: "状态查询失败" },
      { status: 500 }
    );
  }
}

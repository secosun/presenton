import { NextResponse } from "next/server";

const OPENCLAW_GATEWAY_BASE = process.env.OPENCLAW_GATEWAY_BASE || process.env.NEXT_PUBLIC_OPENCLAW_GATEWAY_BASE || "https://ppt.installall.cn";
const OPENCLAW_GATEWAY_TOKEN = process.env.OPENCLAW_GATEWAY_TOKEN || process.env.NEXT_PUBLIC_OPENCLAW_GATEWAY_TOKEN || "openclaw-distributed-secret-key";

// 提取 base64 编码中的 JSON 数据
function extractBootData(html: string) {
  const match = html.match(/atob\("([^"]+)"\)/);
  if (match && match[1]) {
    try {
      const jsonStr = Buffer.from(match[1], "base64").toString("utf-8");
      return JSON.parse(jsonStr);
    } catch (e) {
      return null;
    }
  }
  return null;
}

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    // 1. 请求网关扫码页面
    const targetUrl = `${OPENCLAW_GATEWAY_BASE}/__openclaw__/weixin/scan?token=${encodeURIComponent(OPENCLAW_GATEWAY_TOKEN)}`;
    const response = await fetch(targetUrl);
    const html = await response.text();

    // 检查 Gateway 响应状态
    if (!response.ok) {
      console.error("Gateway 扫码页请求失败:", response.status, html.substring(0, 100));
      return NextResponse.json(
        { error: `网关服务异常 (${response.status})` },
        { status: response.status }
      );
    }

    // 2. 提取二维码数据
    const bootData = extractBootData(html);
    if (!bootData || !bootData.qrDataUrl) {
      return NextResponse.json(
        { error: "无法获取二维码数据" },
        { status: 502 }
      );
    }

    // 微信反爬，直接请求图片会跳转到验证页
    // 用公共二维码 API 根据 URL 生成二维码图片
    const qrApiUrl = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(bootData.qrDataUrl)}`;

    // 代理请求二维码图片，转 base64
    let qrBase64 = bootData.qrDataUrl;
    try {
      const imgResponse = await fetch(qrApiUrl, {
        headers: {
          "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        },
      });
      const imgBuffer = await imgResponse.arrayBuffer();
      const contentType = imgResponse.headers.get("Content-Type") || "image/png";
      qrBase64 = `data:${contentType};base64,${Buffer.from(imgBuffer).toString("base64")}`;
    } catch (imgError) {
      console.error("二维码生成失败:", imgError);
      // 回退到原始 URL
    }

    return NextResponse.json({
      qrCode: qrBase64,
      sessionKey: bootData.sessionKey,
      message: bootData.message || "使用微信扫描上方二维码完成绑定",
      waitPath: bootData.waitPath || "/__openclaw__/weixin/login/wait",
      expireTime: Date.now() + 5 * 60 * 1000,
    });
  } catch (error) {
    console.error("获取二维码失败:", error);
    return NextResponse.json(
      { error: "网关连接失败" },
      { status: 503 }
    );
  }
}

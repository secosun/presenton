import { NextResponse } from "next/server";

export const runtime = "edge";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const qrcode = searchParams.get("qrcode");
    const botType = searchParams.get("bot_type") || "3";

    if (!qrcode) {
      return NextResponse.json(
        { error: "缺少二维码参数" },
        { status: 400 }
      );
    }

    // 代理请求微信 CDN 的二维码图片
    const targetUrl = `https://liteapp.weixin.qq.com/q/${qrcode}?bot_type=${botType}`;
    const response = await fetch(targetUrl, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
      },
    });

    const imageBuffer = await response.arrayBuffer();

    // 返回图片，同源展示
    return new NextResponse(imageBuffer, {
      headers: {
        "Content-Type": response.headers.get("Content-Type") || "image/png",
        "Cache-Control": "max-age=300",
      },
    });
  } catch (error) {
    return NextResponse.json(
      { error: "图片加载失败" },
      { status: 500 }
    );
  }
}

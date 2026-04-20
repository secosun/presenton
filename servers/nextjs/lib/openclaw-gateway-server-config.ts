/**
 * OpenClaw 网关：仅服务端 API 路由使用（勿与浏览器可见的 NEXT_PUBLIC 混用逻辑）。
 *
 * 切勿将 OPENCLAW_GATEWAY_BASE 默认为本站营销域名：Next 会对自己请求 /__openclaw__/…，
 * 若 Ingress 未把该前缀反代到网关，则永远拿不到扫码页 HTML，表现为「获取二维码失败」。
 */
export function getOpenClawGatewayBaseForServer(): string | null {
  const raw = process.env.OPENCLAW_GATEWAY_BASE || process.env.NEXT_PUBLIC_OPENCLAW_GATEWAY_BASE;
  const trimmed = typeof raw === "string" ? raw.trim() : "";
  if (trimmed.length > 0) {
    return trimmed.replace(/\/+$/, "");
  }
  if (process.env.NODE_ENV !== "production") {
    return "http://127.0.0.1:18789";
  }
  return null;
}

export function getOpenClawGatewayTokenForServer(): string {
  const raw =
    process.env.OPENCLAW_GATEWAY_TOKEN || process.env.NEXT_PUBLIC_OPENCLAW_GATEWAY_TOKEN || "";
  const trimmed = typeof raw === "string" ? raw.trim() : "";
  if (trimmed.length > 0) {
    return trimmed;
  }
  return "openclaw-distributed-secret-key";
}

export function openClawGatewayBaseMissingMessage(): string {
  return (
    "未配置 OPENCLAW_GATEWAY_BASE：请设为公网可访问的 OpenClaw 网关根地址（含协议与端口，无尾斜杠）。" +
    "若网关与 Presenton 同域，须由反代将 /__openclaw__/ 转发至网关，此时可填本站 HTTPS 根地址；并确保 OPENCLAW_GATEWAY_TOKEN 与网关一致。"
  );
}

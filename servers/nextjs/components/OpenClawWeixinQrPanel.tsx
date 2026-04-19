"use client";

import { useState, useEffect } from "react";
import { RefreshCw, Loader2 } from "lucide-react";

type QrStatus = "loading" | "ready" | "error";

interface QrData {
  qrCode?: string;
  status: QrStatus;
  message?: string;
}

/**
 * OpenClaw Gateway 微信扫码组件。
 *
 * 后端代理生成二维码，前端直接显示图片。无 iframe，无 token 暴露。
 * 简化版本：不轮询状态，用户扫码后页面会自动显示成功信息。
 */
export default function OpenClawWeixinQrPanel() {
  const [qrData, setQrData] = useState<QrData>({ status: "loading" });

  const fetchQrCode = async () => {
    setQrData({ status: "loading" });
    try {
      const response = await fetch("/api/openclaw/weixin/qrcode", {
        method: "GET",
        cache: "no-store",
      });

      if (response.ok) {
        const data = await response.json();
        setQrData({
          qrCode: data.qrCode,
          status: "ready",
          message: data.message || "请使用微信扫描二维码",
        });
      } else {
        setQrData({
          status: "error",
          message: "获取二维码失败",
        });
      }
    } catch (error) {
      console.error("获取二维码失败:", error);
      setQrData({
        status: "error",
        message: "网络错误，请稍后重试",
      });
    }
  };

  useEffect(() => {
    fetchQrCode();
  }, []);

  const handleRefresh = () => {
    fetchQrCode();
  };

  return (
    <section
      className="rounded-xl border border-slate-200/80 bg-white/90 p-5 shadow-sm backdrop-blur-sm"
      aria-label="OpenClaw 微信扫码"
    >
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 className="text-base font-semibold text-slate-900">微信扫码绑定</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            扫描二维码完成网关侧 OpenClaw 绑定
          </p>
        </div>
        <button
          onClick={handleRefresh}
          className="inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-100"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          刷新
        </button>
      </div>

      <div className="flex flex-col items-center justify-center py-6">
        {/* QR Code Container - 纯图片，无 iframe */}
        <div className="relative w-56 h-56 rounded-xl border-2 border-dashed border-slate-200 bg-white flex items-center justify-center overflow-hidden">
          {qrData.status === "loading" && (
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="w-12 h-12 animate-spin text-blue-500" />
              <span className="text-sm text-slate-500">正在获取二维码...</span>
            </div>
          )}

          {qrData.status === "ready" && qrData.qrCode && (
            <img
              src={qrData.qrCode}
              alt="微信扫码二维码"
              className="w-52 h-52 object-contain"
            />
          )}

          {qrData.status === "error" && (
            <div className="flex flex-col items-center gap-3 text-center px-4">
              <span className="text-sm font-medium text-red-600">
                {qrData.message}
              </span>
              <button
                onClick={handleRefresh}
                className="inline-flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700"
              >
                <RefreshCw className="w-4 h-4" />
                点击重试
              </button>
            </div>
          )}
        </div>

        {qrData.status === "ready" && (
          <p className="mt-4 text-sm text-slate-600 text-center">
            打开微信 → 扫一扫 → 扫描二维码确认绑定
          </p>
        )}
      </div>

      {/* Tips */}
      <div className="mt-4 pt-4 border-t border-slate-100">
        <p className="text-xs text-slate-400 leading-relaxed">
          💡 提示：扫码后将在 OpenClaw 网关侧绑定你的微信账号，用于后续的 AI Agent 身份验证和权限管理。
        </p>
      </div>
    </section>
  );
}

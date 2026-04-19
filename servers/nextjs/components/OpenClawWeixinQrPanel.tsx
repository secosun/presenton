"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { RefreshCw, Loader2, CheckCircle2, Clock } from "lucide-react";

type QrStatus = "loading" | "ready" | "scanned" | "success" | "expired" | "error";

interface QrData {
  qrCode?: string;
  sessionKey?: string;
  expireTime?: number;
  status: QrStatus;
  message?: string;
}

/**
 * OpenClaw Gateway 微信扫码组件。
 *
 * 后端代理生成二维码，前端直接显示图片。无 iframe，无 token 暴露。
 * 自动轮询扫码状态，二维码过期自动刷新。
 */
export default function OpenClawWeixinQrPanel() {
  const [qrData, setQrData] = useState<QrData>({ status: "loading" });
  const pollTimerRef = useRef<NodeJS.Timeout | null>(null);
  const expireTimerRef = useRef<NodeJS.Timeout | null>(null);

  const clearTimers = useCallback(() => {
    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }
    if (expireTimerRef.current) {
      clearTimeout(expireTimerRef.current);
      expireTimerRef.current = null;
    }
  }, []);

  const pollStatus = useCallback(async (sessionKey: string) => {
    try {
      const response = await fetch("/api/openclaw/weixin/status", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionKey }),
      });

      const data = await response.json();

      if (data.status === "success") {
        clearTimers();
        setQrData((prev) => ({
          ...prev,
          status: "success",
          message: data.message || "绑定成功！",
        }));
      } else if (data.status === "scanned") {
        setQrData((prev) => ({
          ...prev,
          status: "scanned",
          message: data.message || "已扫码，请在手机上确认",
        }));
      } else if (data.status === "expired") {
        clearTimers();
        setQrData({
          status: "expired",
          message: "二维码已过期，请刷新",
        });
      } else if (data.status === "error") {
        // Gateway 异常，停止轮询并显示错误
        clearTimers();
        setQrData({
          status: "error",
          message: data.message || "网关服务异常",
        });
      }
      // waiting 状态不更新，继续轮询
    } catch (error) {
      console.error("轮询状态失败:", error);
    }
  }, [clearTimers]);

  const fetchQrCode = useCallback(async () => {
    clearTimers();
    setQrData({ status: "loading" });

    try {
      const response = await fetch("/api/openclaw/weixin/qrcode", {
        method: "GET",
        cache: "no-store",
      });

      if (response.ok) {
        const data = await response.json();
        const expireTime = data.expireTime || Date.now() + 5 * 60 * 1000;
        const msUntilExpire = Math.max(0, expireTime - Date.now());

        setQrData({
          qrCode: data.qrCode,
          sessionKey: data.sessionKey,
          expireTime,
          status: "ready",
          message: data.message || "请使用微信扫描二维码",
        });

        // 设置过期自动刷新
        expireTimerRef.current = setTimeout(() => {
          setQrData({
            status: "expired",
            message: "二维码已过期，请刷新",
          });
        }, msUntilExpire);

        // 开始轮询扫码状态
        if (data.sessionKey) {
          pollTimerRef.current = setInterval(() => {
            pollStatus(data.sessionKey);
          }, 2000);
        }
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
  }, [clearTimers, pollStatus]);

  useEffect(() => {
    fetchQrCode();
    return () => clearTimers();
  }, [fetchQrCode, clearTimers]);

  const handleRefresh = () => {
    fetchQrCode();
  };

  const getStatusIcon = () => {
    switch (qrData.status) {
      case "loading":
        return <Loader2 className="w-12 h-12 animate-spin text-blue-500" />;
      case "success":
        return <CheckCircle2 className="w-12 h-12 text-green-500" />;
      case "scanned":
        return <Clock className="w-12 h-12 text-yellow-500" />;
      case "expired":
      case "error":
        return null;
      default:
        return null;
    }
  };

  const getStatusText = () => {
    switch (qrData.status) {
      case "loading":
        return "正在获取二维码...";
      case "scanned":
        return qrData.message || "已扫码，请在手机上确认";
      case "success":
        return qrData.message || "绑定成功！";
      case "expired":
        return qrData.message || "二维码已过期";
      case "error":
        return qrData.message || "获取二维码失败";
      default:
        return "";
    }
  };

  const isTerminal = qrData.status === "success" || qrData.status === "expired" || qrData.status === "error";

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
        <div className="relative w-56 h-56 rounded-xl border-2 border-dashed border-slate-200 bg-white flex items-center justify-center overflow-hidden">
          {qrData.status === "loading" && (
            <div className="flex flex-col items-center gap-3">
              {getStatusIcon()}
              <span className="text-sm text-slate-500">{getStatusText()}</span>
            </div>
          )}

          {qrData.status === "ready" && qrData.qrCode && (
            <>
              <img
                src={qrData.qrCode}
                alt="微信扫码二维码"
                className="w-52 h-52 object-contain"
              />
              {/* 倒计时指示器 */}
              <div className="absolute top-2 right-2 text-xs text-slate-400">
                <Clock className="w-3 h-3 inline mr-1" />
                5分钟有效
              </div>
            </>
          )}

          {qrData.status === "scanned" && qrData.qrCode && (
            <>
              <div className="relative">
                <img
                  src={qrData.qrCode}
                  alt="微信扫码二维码"
                  className="w-52 h-52 object-contain opacity-50"
                />
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  {getStatusIcon()}
                  <span className="text-sm font-medium text-yellow-600 mt-2">
                    {getStatusText()}
                  </span>
                </div>
              </div>
            </>
          )}

          {(qrData.status === "success" || qrData.status === "expired" || qrData.status === "error") && (
            <div className="flex flex-col items-center gap-3 text-center px-4">
              {getStatusIcon()}
              <span className={`text-sm font-medium ${
                qrData.status === "success" ? "text-green-600" : "text-red-600"
              }`}>
                {getStatusText()}
              </span>
              {qrData.status !== "success" && (
                <button
                  onClick={handleRefresh}
                  className="inline-flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700"
                >
                  <RefreshCw className="w-4 h-4" />
                  点击刷新
                </button>
              )}
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

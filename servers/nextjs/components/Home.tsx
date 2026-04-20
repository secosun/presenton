"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, ArrowRight, FileText, Palette, Zap, User, CreditCard, MessageCircle, Shield, Crown, CheckCircle } from "lucide-react";
import { useSelector } from "react-redux";
import { RootState } from "@/store/store";
import OpenClawWeixinQrPanel from "./OpenClawWeixinQrPanel";

export default function Home() {
  const router = useRouter();
  const config = useSelector((state: RootState) => state.userConfig);
  const canChangeKeys = config.can_change_keys;

  const handleStart = () => {
    router.push("/upload");
  };

  const handleLogin = () => {
    router.push("/login");
  };

  const handlePricing = () => {
    router.push("/pricing");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      {/* Header */}
      <header className="border-b border-slate-100 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-3">
              <img src="/Logo.png" alt="Presenton logo" className="h-10" />
              <span className="text-xl font-bold text-slate-800">Presenton</span>
            </div>
            <nav className="hidden md:flex items-center gap-6">
              <button onClick={handleStart} className="text-sm text-slate-600 hover:text-slate-900 transition">
                开始创作
              </button>
              <button onClick={handlePricing} className="text-sm text-slate-600 hover:text-slate-900 transition">
                订阅方案
              </button>
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleLogin}
              className="inline-flex items-center gap-2 px-4 py-2 border border-slate-200 text-slate-700 font-medium rounded-lg hover:bg-slate-50 transition"
            >
              <User className="w-4 h-4" />
              登录
            </button>
            <button
              onClick={handleStart}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg shadow-blue-500/25"
            >
              免费试用
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section - QR Code 居中 */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-full text-sm font-medium mb-6">
            <Sparkles className="w-4 h-4" />
            AI 驱动的演示文稿生成器
          </div>

          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 leading-tight mb-4">
            微信扫码绑定插件，一键生成 PPT
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            无需注册，匿名即可使用。扫描下方二维码绑定微信插件，
            在微信内也能直接生成专业演示文稿。
          </p>
        </div>

        {/* QR Code 中心展示 */}
        <div className="flex justify-center mb-16">
          <div className="w-full max-w-lg">
            <OpenClawWeixinQrPanel />
          </div>
        </div>

        {/* 快速开始按钮 */}
        <div className="text-center mb-16">
          <button
            onClick={handleStart}
            className="inline-flex items-center gap-3 px-10 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all shadow-xl shadow-blue-500/30 text-lg"
          >
            立即开始创作（匿名可用）
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>

        {/* Feature Row */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          <div className="p-5 bg-white rounded-2xl shadow-sm border border-slate-100">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
              <Zap className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="font-semibold text-slate-900 mb-1">匿名可用</h3>
            <p className="text-sm text-slate-500">无需注册登录，打开即可使用，快速生成演示文稿</p>
          </div>
          <div className="p-5 bg-white rounded-2xl shadow-sm border border-slate-100">
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-4">
              <MessageCircle className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="font-semibold text-slate-900 mb-1">微信插件</h3>
            <p className="text-sm text-slate-500">扫码绑定微信插件，在微信内随时随地生成 PPT</p>
          </div>
          <div className="p-5 bg-white rounded-2xl shadow-sm border border-slate-100">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4">
              <Crown className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="font-semibold text-slate-900 mb-1">会员订阅</h3>
            <p className="text-sm text-slate-500">订阅会员解锁高级功能，无限量生成、专属模板</p>
          </div>
          <div className="p-5 bg-white rounded-2xl shadow-sm border border-slate-100">
            <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center mb-4">
              <Shield className="w-6 h-6 text-orange-600" />
            </div>
            <h3 className="font-semibold text-slate-900 mb-1">账户管理</h3>
            <p className="text-sm text-slate-500">完善的用户中心、订单管理、支付记录查询</p>
          </div>
        </div>

        {/* 订阅方案预览 */}
        <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-3xl p-8 md:p-12 text-white mb-16">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-4">升级会员，解锁全部功能</h2>
              <ul className="space-y-3">
                <li className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  <span>无限量生成 PPT</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  <span>50+ 专属精美模板</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  <span>高清导出无水印</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  <span>优先客服支持</span>
                </li>
              </ul>
            </div>
            <div className="text-center">
              <div className="inline-block bg-white/10 backdrop-blur rounded-2xl p-6">
                <div className="text-sm text-slate-300 mb-1">会员低至</div>
                <div className="text-5xl font-bold mb-2">¥19<span className="text-lg font-normal">/月</span></div>
                <button
                  onClick={handlePricing}
                  className="mt-4 inline-flex items-center gap-2 px-6 py-3 bg-white text-slate-900 font-semibold rounded-xl hover:bg-slate-100 transition"
                >
                  <CreditCard className="w-4 h-4" />
                  查看订阅方案
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* 功能特性 */}
        <div className="grid md:grid-cols-3 gap-8">
          <div className="p-6 bg-white rounded-2xl shadow-sm border border-slate-100">
            <Palette className="w-8 h-8 text-indigo-500 mb-4" />
            <h3 className="text-lg font-semibold text-slate-900 mb-2">精美模板</h3>
            <p className="text-slate-600">数十种专业设计的演示文稿模板，覆盖商务、教育、汇报等场景</p>
          </div>
          <div className="p-6 bg-white rounded-2xl shadow-sm border border-slate-100">
            <FileText className="w-8 h-8 text-indigo-500 mb-4" />
            <h3 className="text-lg font-semibold text-slate-900 mb-2">多格式导出</h3>
            <p className="text-slate-600">支持导出 PPTX、PDF 等多种格式，保留所有样式和动画效果</p>
          </div>
          <div className="p-6 bg-white rounded-2xl shadow-sm border border-slate-100">
            <Zap className="w-8 h-8 text-indigo-500 mb-4" />
            <h3 className="text-lg font-semibold text-slate-900 mb-2">AI 智能创作</h3>
            <p className="text-slate-600">先进 AI 算法，根据主题自动生成内容大纲和页面布局</p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-100 mt-16">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <img src="/Logo.png" alt="Presenton logo" className="h-6" />
              <span className="text-slate-600 text-sm">Presenton © 2026</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-slate-500">
              <button className="hover:text-slate-700 transition">隐私政策</button>
              <button className="hover:text-slate-700 transition">服务条款</button>
              <button className="hover:text-slate-700 transition">帮助中心</button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

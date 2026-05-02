#!/usr/bin/env node
/**
 * 在 Presenton / Nginx 正常时，对 MCP 端点做 initialize → tools/list，
 * 打印工具名，并可与 OpenClaw 配置中的 tools.allow（presenton__*）对照。
 *
 * 用法:
 *   PRESENTON_MCP_URL="http://127.0.0.1:5000/mcp" node scripts/verify-presenton-mcp-allow.mjs
 *   OPENCLAW_ALLOW_PATH=/path/to/openclaw.json node scripts/verify-presenton-mcp-allow.mjs
 *
 * 依赖: Node 18+（内置 fetch），无 npm 包。
 */
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dirname, "..");

const MCP_URL = (process.env.PRESENTON_MCP_URL || "http://127.0.0.1:5000/mcp").replace(
  /\/?$/,
  ""
);
const ALLOW_PATH =
  process.env.OPENCLAW_ALLOW_PATH ||
  process.env.OPENCLAW_JSON ||
  join(process.cwd(), "openclaw.json");

const JSON_HEADERS = {
  "Content-Type": "application/json",
  Accept: "application/json, text/event-stream",
};

/**
 * 解析 MCP Streamable HTTP：可能是单条 JSON，也可能是 SSE 里第一条带 result 的 data。
 */
async function parseMcpResponse(res) {
  const ct = (res.headers.get("content-type") || "").toLowerCase();
  const text = await res.text();
  if (!text || !text.trim()) return null;
  if (ct.includes("text/event-stream")) {
    for (const line of text.split("\n")) {
      const s = line.trim();
      if (s.startsWith("data:")) {
        const raw = s.slice(5).trim();
        if (raw && raw !== "[DONE]") {
          try {
            return JSON.parse(raw);
          } catch {
            /* continue */
          }
        }
      }
    }
    throw new Error("SSE 响应中未解析到 JSON data 行");
  }
  if (!text) return null;
  return JSON.parse(text);
}

async function mcpRequest(url, body, sessionId) {
  const headers = { ...JSON_HEADERS };
  if (sessionId) headers["Mcp-Session-Id"] = sessionId;

  const res = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  if (res.status === 502) {
    const e = new Error("Bad Gateway");
    e.status = 502;
    throw e;
  }

  const newSession =
    res.headers.get("mcp-session-id") || res.headers.get("Mcp-Session-Id") || null;

  let json;
  try {
    json = await parseMcpResponse(res);
  } catch (e) {
    const err = new Error(`解析 MCP 响应失败: ${e.message}；HTTP ${res.status}`);
    err.status = res.status;
    throw err;
  }

  if (!res.ok && res.status !== 202) {
    const err = new Error(`HTTP ${res.status}`);
    err.status = res.status;
    err.json = json;
    throw err;
  }

  return { res, json, sessionId: newSession || sessionId };
}

function loadOpenclawAllow() {
  if (!existsSync(ALLOW_PATH)) return null;
  const raw = readFileSync(ALLOW_PATH, "utf8");
  const data = JSON.parse(raw);
  const allow =
    data.tools?.allow ||
    data.agent?.tools?.allow ||
    data.mcp?.tools?.allow ||
    null;
  if (!Array.isArray(allow)) {
    console.warn(
      `已读取 ${ALLOW_PATH}，但未找到 tools.allow 数组（支持 .tools.allow / .agent.tools.allow / .mcp.tools.allow）`
    );
    return [];
  }
  return allow.filter((x) => typeof x === "string" && x.startsWith("presenton__"));
}

function main() {
  return (async () => {
    console.log(`MCP URL: ${MCP_URL}`);

    let sessionId = null;
    // initialize
    const init = await mcpRequest(
      MCP_URL,
      {
        jsonrpc: "2.0",
        id: 1,
        method: "initialize",
        params: {
          protocolVersion: "2024-11-05",
          capabilities: {},
          clientInfo: { name: "verify-presenton-mcp-allow", version: "1.0.0" },
        },
      },
      null
    );
    sessionId = init.sessionId;
    if (!sessionId) {
      console.warn(
        "未收到 Mcp-Session-Id；若后续 tools/list 报 Missing session ID，需升级/对齐 MCP 协议实现。"
      );
    }

    // notifications/initialized（部分服务端要求）
    if (sessionId) {
      try {
        await mcpRequest(
          MCP_URL,
          {
            jsonrpc: "2.0",
            method: "notifications/initialized",
            params: {},
          },
          sessionId
        );
      } catch {
        /* 可忽略 405 等 */
      }
    }

    const list = await mcpRequest(
      MCP_URL,
      {
        jsonrpc: "2.0",
        id: 2,
        method: "tools/list",
        params: {},
      },
      sessionId
    );

    const tools = list.json?.result?.tools;
    if (!Array.isArray(tools)) {
      console.error("tools/list 未返回 result.tools：", JSON.stringify(list.json, null, 2));
      process.exit(1);
    }

    const names = tools.map((t) => t.name).filter(Boolean);
    names.sort();
    console.log(`\n远程 tools/list 共 ${names.length} 个工具（name）:`);
    for (const n of names) console.log(`  - ${n}`);

    const allow = loadOpenclawAllow();
    if (allow && allow.length) {
      /** OpenClaw 常为 presenton__<operationId>，MCP 侧多为 operationId 本身 */
      const toAllowForm = (n) =>
        n.startsWith("presenton__") ? n : `presenton__${n}`;
      const allowSet = new Set(allow);
      const remoteAsAllow = new Set(names.map(toAllowForm));
      const missingOnServer = [...allowSet].filter((a) => !remoteAsAllow.has(a));
      const notInAllow = [...names].map(toAllowForm).filter((a) => !allowSet.has(a));
      console.log(
        `\nOpenClaw allow 中的 presenton__*（${ALLOW_PATH}）: ${allow.length} 个`
      );
      for (const a of allow) console.log(`  - ${a}`);
      if (missingOnServer.length) {
        console.log("\n在 allow 中但远程未出现:");
        for (const x of missingOnServer) console.log(`  - ${x}`);
      } else {
        console.log("\nallow 中条目均已出现在远程。");
      }
      if (notInAllow.length) {
        console.log(
          "\n远程有但不在 allow 中（全量模式常见；子集/兼容模式应收紧 allow）:"
        );
        for (const x of notInAllow.slice(0, 50)) console.log(`  - ${x}`);
        if (notInAllow.length > 50) console.log(`  ... 另有 ${notInAllow.length - 50} 个`);
      }
    } else {
      console.log(
        "\n未配置 OPENCLAW_ALLOW_PATH 或未找到 openclaw.json 中的 presenton__* allow，跳过对照。"
      );
      console.log("可选: OPENCLAW_ALLOW_PATH=/path/to/openclaw.json");
    }

    // 子集/文件模式提示
    if (names.length === 3) {
      const fileMode = new Set([
        "start_materialize_presentation",
        "get_materialize_job",
        "materialize_presentation",
      ]);
      if (names.every((n) => fileMode.has(n))) {
        console.log(
          "\n提示: 仅 3 个物化相关工具名，与 openai_spec.json 子集/ PRESENTON_MCP_OPENAPI_SOURCE=file 表现一致；全量应显著多于 3。"
        );
      }
    }
  })().catch((e) => {
    if (e.status === 502) {
      console.error(
        `HTTP 502: Nginx 上游（Presenton/MCP）未就绪或不可达: ${MCP_URL}\n请先在本机/容器起稳 Nginx 与 FastAPI + mcp_server 后再测。`
      );
    } else {
      console.error(e.message || e);
      if (e.json) console.error(JSON.stringify(e.json, null, 2));
    }
    process.exit(1);
  });
}

main();

# Multi-stage: build Next.js in a Node image, ship only pruned node_modules + .next-build in the runtime image.

FROM node:20-bookworm-slim AS nextjs-builder

WORKDIR /app/servers/nextjs

ENV CYPRESS_INSTALL_BINARY=0 \
    NPM_CONFIG_UPDATE_NOTIFIER=false \
    PUPPETEER_SKIP_DOWNLOAD=true

# Override with e.g. https://registry.npmjs.org for default registry outside China.
ARG NPM_REGISTRY=https://registry.npmmirror.com
RUN npm config set registry "${NPM_REGISTRY}"

COPY servers/nextjs/package.json servers/nextjs/package-lock.json ./
RUN npm ci

COPY servers/nextjs/ ./
RUN npm run build && npm prune --omit=dev


FROM python:3.11-slim-bookworm

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    curl \
    ca-certificates \
    libreoffice \
    fontconfig \
    chromium \
    zstd \
    && rm -rf /var/lib/apt/lists/*

# Same Debian bookworm family as node:20-bookworm-slim; avoids NodeSource script and extra apt layers.
COPY --from=node:20-bookworm-slim /usr/local /usr/local
ENV PATH=/usr/local/bin:$PATH

WORKDIR /app

ENV APP_DATA_DIRECTORY=/app_data
ENV TEMP_DIRECTORY=/tmp/presenton
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

ENV PIP_REQUIRE_HASHES=0
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_DEFAULT_TIMEOUT=1800

ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

ARG INSTALL_OLLAMA=true
RUN if [ "$INSTALL_OLLAMA" = "true" ]; then \
  curl -fsSL https://ollama.com/install.sh | sh; \
  else \
  echo "Skipping Ollama install (INSTALL_OLLAMA=false)"; \
  fi
ENV ENABLE_OLLAMA=${INSTALL_OLLAMA}

RUN HTTP_PROXY= HTTPS_PROXY= ALL_PROXY= http_proxy= https_proxy= all_proxy= \
  pip install --no-cache-dir -i "${PIP_INDEX_URL}" \
  --trusted-host pypi.org \
  --trusted-host pypi.tuna.tsinghua.edu.cn \
  --trusted-host mirrors.aliyun.com \
  PySocks

RUN HTTP_PROXY= HTTPS_PROXY= ALL_PROXY= http_proxy= https_proxy= all_proxy= \
  pip install --retries 10 --default-timeout=600 --no-cache-dir \
  -i "${PIP_INDEX_URL}" \
  --trusted-host pypi.org \
  --trusted-host pypi.tuna.tsinghua.edu.cn \
  --trusted-host mirrors.aliyun.com \
    alembic aiohttp aiomysql aiosqlite asyncpg fastapi[standard] \
    pathvalidate pdfplumber chromadb sqlmodel jsonschema \
    anthropic google-genai openai fastmcp dirtyjson 'httpx[socks]' \
    python-pptx nltk redis

COPY --from=nextjs-builder /app/servers/nextjs /app/servers/nextjs

COPY servers/fastapi/ ./servers/fastapi/
COPY start.js LICENSE NOTICE ./

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["node", "/app/start.js"]

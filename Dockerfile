FROM python:3.11-slim-bookworm

# Install Node.js and npm
RUN apt-get update && apt-get install -y \
    nginx \
    curl \
    libreoffice \
    fontconfig \
    chromium \
    zstd


# Install Node.js 20 using NodeSource repository
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs


# Create a working directory
WORKDIR /app  

# Set environment variables
ENV APP_DATA_DIRECTORY=/app_data
ENV TEMP_DIRECTORY=/tmp/presenton
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Host/CI may export PIP_REQUIRE_HASHES=1; that breaks `pip install docling` when
# transitive wheels (e.g. dill) do not match any pinned hash in a local requirements file.
ENV PIP_REQUIRE_HASHES=0
# Avoid pip self-check hitting PyPI (often fails behind broken SOCKS/TLS proxies).
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
# Default pip socket timeout is 15s; large wheels + pytorch.org CDN need more.
ENV PIP_DEFAULT_TIMEOUT=1800

# Pip mirrors (China-friendly). Override official PyPI with e.g.:
#   docker build --build-arg PIP_INDEX_URL=https://pypi.org/simple --build-arg TORCH_EXTRA_INDEX=https://download.pytorch.org/whl/cpu .
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ARG TORCH_EXTRA_INDEX=https://mirrors.aliyun.com/pytorch-wheels/cpu

# Optional bundled Ollama (compose `production` passes INSTALL_OLLAMA=false)
ARG INSTALL_OLLAMA=true
RUN if [ "$INSTALL_OLLAMA" = "true" ]; then \
  curl -fsSL https://ollama.com/install.sh | sh; \
  else \
  echo "Skipping Ollama install (INSTALL_OLLAMA=false)"; \
  fi
ENV ENABLE_OLLAMA=${INSTALL_OLLAMA}

# Host may pass *_PROXY=socks5h://... into the build; pip needs PySocks for SOCKS.
# Bootstrap without proxy (many builders reach PyPI directly); later RUNs can use SOCKS.
RUN HTTP_PROXY= HTTPS_PROXY= ALL_PROXY= http_proxy= https_proxy= all_proxy= \
  pip install --no-cache-dir -i ${PIP_INDEX_URL} \
  --trusted-host pypi.tuna.tsinghua.edu.cn \
  PySocks

# Install dependencies for FastAPI
RUN pip install --retries 10 --default-timeout=600 --no-cache-dir \
    -i ${PIP_INDEX_URL} --trusted-host pypi.tuna.tsinghua.edu.cn \
    alembic aiohttp aiomysql aiosqlite asyncpg fastapi[standard] \
    pathvalidate pdfplumber chromadb sqlmodel jsonschema \
    anthropic google-genai openai fastmcp dirtyjson 'httpx[socks]'
# Docling + torch CPU: Tsinghua PyPI + Aliyun pytorch-wheels (avoid download.pytorch.org abroad).
RUN /bin/sh -c 'unset PIP_CONSTRAINT 2>/dev/null; \
  HTTP_PROXY= HTTPS_PROXY= ALL_PROXY= http_proxy= https_proxy= all_proxy= \
  PIP_REQUIRE_HASHES=0 PIP_DISABLE_PIP_VERSION_CHECK=1 \
  pip install --retries 15 --default-timeout=3600 --no-cache-dir \
  -i ${PIP_INDEX_URL} --extra-index-url ${TORCH_EXTRA_INDEX} \
  --trusted-host pypi.tuna.tsinghua.edu.cn --trusted-host mirrors.aliyun.com \
  docling \
  || pip install --retries 15 --default-timeout=3600 --no-cache-dir \
  -i ${PIP_INDEX_URL} --extra-index-url ${TORCH_EXTRA_INDEX} \
  --trusted-host pypi.tuna.tsinghua.edu.cn --trusted-host mirrors.aliyun.com \
  docling \
  || pip install --retries 15 --default-timeout=3600 --no-cache-dir \
  -i ${PIP_INDEX_URL} --extra-index-url ${TORCH_EXTRA_INDEX} \
  --trusted-host pypi.tuna.tsinghua.edu.cn --trusted-host mirrors.aliyun.com \
  docling'

# Install dependencies for Next.js
WORKDIR /app/servers/nextjs
COPY servers/nextjs/package.json servers/nextjs/package-lock.json ./
# Cypress is dev-only; downloading ~200MB inside Docker often fails (proxy / truncated).
ENV CYPRESS_INSTALL_BINARY=0
RUN npm install


# Copy Next.js app
COPY servers/nextjs/ /app/servers/nextjs/

# Build the Next.js app
WORKDIR /app/servers/nextjs
RUN npm run build

WORKDIR /app

# Copy FastAPI
COPY servers/fastapi/ ./servers/fastapi/
COPY start.js LICENSE NOTICE ./

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose the port
EXPOSE 80

# Start the servers
CMD ["node", "/app/start.js"]
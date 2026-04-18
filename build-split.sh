#!/bin/bash
# 拆分镜像构建脚本
# 用法：./build-split.sh

set -e

echo "========================================"
echo "  开始构建拆分的 Docker 镜像"
echo "========================================"

# 镜像标签
PROD_TAG="${PROD_TAG:-presenton_production:latest}"
DOCLING_TAG="${DOCLING_TAG:-presenton_docling:latest}"

# 构建参数
PIP_INDEX_URL="${PIP_INDEX_URL:-https://pypi.tuna.tsinghua.edu.cn/simple}"
TORCH_EXTRA_INDEX="${TORCH_EXTRA_INDEX:-https://mirrors.aliyun.com/pytorch-wheels/cpu}"

echo ""
echo "1/2 构建 Docling 服务镜像..."
echo "   标签：$DOCLING_TAG"
echo "   Python 包索引：$PIP_INDEX_URL"
echo "   PyTorch 源：$TORCH_EXTRA_INDEX"
echo ""

docker build \
  --build-arg PIP_INDEX_URL="$PIP_INDEX_URL" \
  --build-arg TORCH_EXTRA_INDEX="$TORCH_EXTRA_INDEX" \
  -t "$DOCLING_TAG" \
  -f Dockerfile.docling \
  .

echo ""
echo "2/2 构建主应用镜像 (不含 docling)..."
echo "   标签：$PROD_TAG"
echo ""

docker build \
  --build-arg INSTALL_OLLAMA=false \
  --build-arg PIP_INDEX_URL="$PIP_INDEX_URL" \
  --build-arg TORCH_EXTRA_INDEX="$TORCH_EXTRA_INDEX" \
  -t "$PROD_TAG" \
  -f Dockerfile \
  .

echo ""
echo "========================================"
echo "  构建完成！镜像大小："
echo "========================================"
docker images | grep -E "(presenton|REPOSITORY)"

echo ""
echo "运行测试 (可选):"
echo "  docker compose -f docker-compose.yml up docling-service production"

#!/bin/bash
# ============================================================
# CatWiki CE Publish Script
# 将 origin/ce 分支推送到 GitHub
#
# Usage: ./scripts/publish_ce.sh [--dry-run]
#   --dry-run  预览变更，不推送
# ============================================================

set -eo pipefail

# ---- 配置 ----
CE_BRANCH="ce"
GITHUB_REMOTE="github"
GITHUB_BRANCH="main"

DRY_RUN=false
if [ "${1:-}" = "--dry-run" ]; then
    DRY_RUN=true
    echo "[DRY RUN] 预览模式，不会推送。"
fi

echo "================================================"
echo "  CatWiki CE 发布工具"
echo "  origin/ce → github/main"
echo "================================================"

# ---- 前置检查 ----
if ! git remote | grep -q "^${GITHUB_REMOTE}$"; then
    echo "ERROR: Remote '$GITHUB_REMOTE' 不存在。"
    echo "  添加: git remote add $GITHUB_REMOTE <github-url>"
    exit 1
fi

# 检查 origin/ce 是否存在
if ! git rev-parse --verify "origin/${CE_BRANCH}" >/dev/null 2>&1; then
    echo "ERROR: origin/${CE_BRANCH} 分支不存在。"
    echo "  请先运行: make sync-ce"
    exit 1
fi

echo "[OK] 前置检查通过。"
echo ""

# ---- 获取最新状态 ----
echo "[1/3] 获取远程仓库最新状态..."
git fetch "$GITHUB_REMOTE" 2>/dev/null || true
git fetch origin "$CE_BRANCH" 2>/dev/null || true

# ---- 显示差异 ----
echo "[2/3] 变更摘要..."
echo ""

CE_COMMIT=$(git rev-parse "origin/${CE_BRANCH}")
echo "  origin/ce 最新提交: $(git log -1 --format='%h %s' origin/${CE_BRANCH})"

if git rev-parse --verify "${GITHUB_REMOTE}/${GITHUB_BRANCH}" >/dev/null 2>&1; then
    GITHUB_COMMIT=$(git rev-parse "${GITHUB_REMOTE}/${GITHUB_BRANCH}")
    echo "  github/main 当前:   $(git log -1 --format='%h %s' ${GITHUB_REMOTE}/${GITHUB_BRANCH})"
    echo ""

    if [ "$CE_COMMIT" = "$GITHUB_COMMIT" ]; then
        echo "  [INFO] origin/ce 与 github/main 完全一致，无需推送。"
        exit 0
    fi

    echo "  差异统计:"
    git diff --stat "${GITHUB_REMOTE}/${GITHUB_BRANCH}..origin/${CE_BRANCH}" 2>/dev/null || echo "  (无法计算差异，可能历史不同)"
else
    echo "  github/main: (不存在或未fetch)"
    echo ""
fi

echo ""

# ---- 推送 ----
echo "[3/3] 推送到 GitHub..."

if [ "$DRY_RUN" = "true" ]; then
    echo "[DRY RUN] 跳过推送。"
    echo "  实际命令: git push $GITHUB_REMOTE origin/${CE_BRANCH}:refs/heads/${GITHUB_BRANCH} --force"
else
    echo "将 origin/ce 推送到 ${GITHUB_REMOTE}/${GITHUB_BRANCH} (force push)..."
    echo ""
    read -p "确认推送到 GitHub？(y/N): " CONFIRM
    if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
        git push "$GITHUB_REMOTE" "origin/${CE_BRANCH}:refs/heads/${GITHUB_BRANCH}" --force
        echo ""
        echo "[OK] 已推送到 ${GITHUB_REMOTE}/${GITHUB_BRANCH}"
    else
        echo "[CANCELLED] 推送已取消。"
    fi
fi

echo ""
echo "================================================"
echo "  发布完成！"
echo "================================================"

#!/usr/bin/env bash
# setup-remotion.sh — Remotion 의존성을 ~/.remotion에 1회 설치
# 모든 cli-jaw 인스턴스가 이 경로를 공유한다.
#
# 사용법: setup-remotion.sh

set -euo pipefail

REMOTION_VERSION="4.0.434"
REMOTION_HOME="${HOME}/.remotion"

echo "📁 설치 경로: $REMOTION_HOME"
echo "🎬 Remotion v${REMOTION_VERSION} 전체 의존성 설치..."
echo ""

# ~/.remotion 디렉토리 생성 + package.json 초기화
mkdir -p "$REMOTION_HOME"
if [ ! -f "$REMOTION_HOME/package.json" ]; then
  echo '{"name":"remotion-shared","private":true}' > "$REMOTION_HOME/package.json"
fi

cd "$REMOTION_HOME"

# 패키지 매니저 감지
PKG="pnpm"
if ! command -v pnpm &>/dev/null; then
  PKG="npm"
  echo "⚠️  pnpm 없음 — npm 사용"
fi

ADD_CMD="$PKG add"
EXEC_CMD="$PKG exec"
if [ "$PKG" = "npm" ]; then
  ADD_CMD="npm install --save"
  EXEC_CMD="npx"
fi

# ── [1/5] Core ──
echo "📦 [1/5] Core..."
$ADD_CMD \
  remotion@${REMOTION_VERSION} \
  @remotion/cli@${REMOTION_VERSION} \
  @remotion/bundler@${REMOTION_VERSION} \
  @remotion/renderer@${REMOTION_VERSION}

# ── [2/5] Transitions & Effects ──
echo "📦 [2/5] Transitions & Effects..."
$ADD_CMD \
  @remotion/transitions@${REMOTION_VERSION} \
  @remotion/light-leaks@${REMOTION_VERSION}

# ── [3/5] Media ──
echo "📦 [3/5] Media (fonts, GIF, Lottie)..."
$ADD_CMD \
  @remotion/google-fonts@${REMOTION_VERSION} \
  @remotion/gif@${REMOTION_VERSION} \
  @remotion/lottie@${REMOTION_VERSION}

# ── [4/5] Audio & Captions ──
echo "📦 [4/5] Audio & Captions..."
$ADD_CMD \
  @remotion/media-utils@${REMOTION_VERSION} \
  @remotion/captions@${REMOTION_VERSION}

# ── [5/5] Layout & Schema & React ──
echo "📦 [5/5] Layout, Zod, React..."
$ADD_CMD \
  @remotion/layout-utils@${REMOTION_VERSION} \
  @remotion/paths@${REMOTION_VERSION} \
  zod react react-dom

# ── Chromium 런타임 ──
echo ""
echo "🌐 Chromium 런타임 확인..."
$EXEC_CMD remotion browser ensure

echo ""
echo "✅ 완료!"
echo "   경로: $REMOTION_HOME"
echo "   모든 cli-jaw 인스턴스가 이 경로를 공유합니다."

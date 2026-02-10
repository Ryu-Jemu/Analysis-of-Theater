#!/usr/bin/env bash
set -euo pipefail

# 실행 방법:
#   1) (권장) 가상환경 생성 후 requirements 설치
#   2) ./run.sh
#
# 환경변수(선택):
#   export KAKAO_REST_API_KEY="..."
#   export NAVER_CLIENT_ID="..."
#   export NAVER_CLIENT_SECRET="..."

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Ensure required Python packages are available.
if ! python3 -c "import dotenv" >/dev/null 2>&1; then
  echo "[INFO] Installing dependencies from requirements.txt..."
  python3 -m pip install -r requirements.txt
fi

python3 pipeline.py

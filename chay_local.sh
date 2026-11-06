#!/usr/bin/env bash
# ============================================================
#   OmDiOm Studio - HE THONG TONG HOP GIONG NOI TIENG VIET
#   Khoi chay tren Linux / macOS
# ============================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "============================================================"
echo "  OmDiOm Studio - HE THONG TONG HOP GIONG NOI TIENG VIET"
echo "============================================================"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "[X] Khong tim thay python3. Vui long cai Python 3.10+ roi thu lai."
    exit 1
fi

export OMDIOM_MOCK=0
export OMDIOM_API_KEY=testkey
export OMDIOM_PRELOAD=1
export OMDIOM_VOICES="$DIR/voices"
export PYTHONIOENCODING=utf-8

echo "[1/2] Thu vien giong doc cuc bo: $OMDIOM_VOICES"
if [ -d "$OMDIOM_VOICES" ]; then
    ls -1 "$OMDIOM_VOICES"/*.pt 2>/dev/null || echo "      [i] San sang nhan dang giong doc tu voices/"
fi

echo ""
echo "[2/2] Dang khoi dong may chu OmDiOm Backend..."
echo "  Dia chi : http://127.0.0.1:8000"
echo "  API key : testkey"
echo "  Giao dien: Mo file UI/index.html tren trinh duyet"
echo "============================================================"
echo ""

cd server
python3 -m uvicorn app:app --host 127.0.0.1 --port 8000


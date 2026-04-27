#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST="$REPO_DIR/frontend/porcupine"
mkdir -p "$DEST"

echo "Downloading @picovoice/porcupine-web..."

TMP=$(mktemp -d)
trap "rm -rf $TMP" EXIT

cd "$TMP"
npm init -y > /dev/null 2>&1
npm install @picovoice/porcupine-web @picovoice/web-voice-processor --silent

# Main IIFE bundle (loaded via <script> tag)
cp node_modules/@picovoice/porcupine-web/dist/iife/index.js                 "$DEST/porcupine-web.js"

# Porcupine worker + WASM
cp node_modules/@picovoice/porcupine-web/dist/lib/pv_porcupine.js          "$DEST/"
cp node_modules/@picovoice/porcupine-web/dist/lib/pv_porcupine_simd.wasm   "$DEST/" 2>/dev/null || true
cp node_modules/@picovoice/porcupine-web/dist/lib/pv_porcupine.wasm        "$DEST/" 2>/dev/null || true

# Base model
cp node_modules/@picovoice/porcupine-web/lib/common/porcupine_params.pv    "$DEST/"

# Jarvis built-in keyword file
find node_modules/@picovoice/porcupine-web/lib/common -name "Jarvis_en_wasm*.ppn" \
  -exec cp {} "$DEST/" \;

# Audio recorder worker + WASM (web-voice-processor)
cp node_modules/@picovoice/web-voice-processor/dist/lib/pv_audio_recorder.js          "$DEST/" 2>/dev/null || true
cp node_modules/@picovoice/web-voice-processor/dist/lib/pv_audio_recorder_simd.wasm   "$DEST/" 2>/dev/null || true
cp node_modules/@picovoice/web-voice-processor/dist/lib/pv_audio_recorder.wasm        "$DEST/" 2>/dev/null || true

echo "Porcupine files installed to frontend/porcupine/"
ls "$DEST/"

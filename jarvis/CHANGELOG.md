# Changelog

## 1.1.2

- Fix openwakeword install on ARM64: skip tflite-runtime (no ARM64 wheel) by installing with --no-deps, using ONNX only

## 1.1.1

- Fix WebSocket support for Hey Jarvis wake word (add websockets library)

## 1.1.0

- Re-enable "Hey Jarvis" wake word on HA Green (ARM64) — onnxruntime now installs via pre-built wheel on Debian
- Wake word model pre-downloaded at build time for instant startup

## 1.0.0

- Initial release
- Natural language control of HA devices via Claude API
- Voice input (mic button) and voice output (browser TTS)
- HA sidebar panel via ingress
- Auto-discovery of HA entities

// AudioWorklet processor — captures mic audio and sends Int16 PCM chunks via MessagePort.
// Accumulates 1280 samples (80ms at 16kHz) before posting to reduce message overhead.

const CHUNK_SIZE = 1280;

class WakeWordProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this._buf = new Float32Array(CHUNK_SIZE);
    this._filled = 0;
  }

  process(inputs) {
    const channel = inputs[0]?.[0];
    if (!channel) return true;

    for (let i = 0; i < channel.length; i++) {
      this._buf[this._filled++] = channel[i];

      if (this._filled === CHUNK_SIZE) {
        const int16 = new Int16Array(CHUNK_SIZE);
        for (let j = 0; j < CHUNK_SIZE; j++) {
          int16[j] = Math.max(-32768, Math.min(32767, this._buf[j] * 32768));
        }
        this.port.postMessage(int16.buffer, [int16.buffer]);
        this._filled = 0;
      }
    }

    return true;
  }
}

registerProcessor('wake-word-processor', WakeWordProcessor);

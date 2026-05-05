// Voice language — change to 'en-US' if you prefer English recognition
const VOICE_LANG = 'fr-FR';

// ── Session ──────────────────────────────────────────────────────────────────
function getSessionId() {
  let id = localStorage.getItem('jarvis_session');
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem('jarvis_session', id);
  }
  return id;
}
const SESSION_ID = getSessionId();

// ── DOM refs ─────────────────────────────────────────────────────────────────
const messagesEl = document.getElementById('messages');
const inputEl    = document.getElementById('user-input');
const sendBtn    = document.getElementById('send-btn');
const voiceBtn   = document.getElementById('voice-btn');
const ttsToggle  = document.getElementById('tts-toggle');
const statusDot  = document.getElementById('status-dot');
const voiceStatus = document.getElementById('voice-status');

// ── TTS toggle ────────────────────────────────────────────────────────────────
let ttsEnabled = localStorage.getItem('jarvis_tts') !== 'false';
ttsToggle.classList.toggle('active', ttsEnabled);
ttsToggle.addEventListener('click', () => {
  ttsEnabled = !ttsEnabled;
  localStorage.setItem('jarvis_tts', ttsEnabled);
  ttsToggle.classList.toggle('active', ttsEnabled);
});

function speak(text) {
  if (!ttsEnabled || !window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const utt = new SpeechSynthesisUtterance(text);
  utt.lang = VOICE_LANG;
  // Try to find a matching voice
  const voices = window.speechSynthesis.getVoices();
  const match = voices.find(v => v.lang.startsWith(VOICE_LANG.slice(0, 2)));
  if (match) utt.voice = match;
  window.speechSynthesis.speak(utt);
}

// ── Connection health check ───────────────────────────────────────────────────
async function checkHealth() {
  try {
    const r = await fetch('api/health');
    const data = await r.json();
    if (data.home_assistant === 'connected') {
      statusDot.className = 'status-dot connected';
      statusDot.title = `Connected to ${data.ha_url}`;
    } else {
      statusDot.className = 'status-dot error';
      statusDot.title = 'Cannot reach Home Assistant — check HA_URL in .env';
    }
  } catch {
    statusDot.className = 'status-dot error';
    statusDot.title = 'Cannot reach Jarvis server';
  }
}
checkHealth();

// ── Message rendering ─────────────────────────────────────────────────────────
function addBubble(role, text) {
  const wrap = document.createElement('div');
  wrap.className = `bubble-wrap ${role}`;

  const label = document.createElement('div');
  label.className = 'bubble-label';
  label.textContent = role === 'user' ? 'You' : 'Jarvis';

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;

  wrap.appendChild(label);
  wrap.appendChild(bubble);
  messagesEl.appendChild(wrap);
  scrollToBottom();
  return bubble;
}

function showTyping() {
  const wrap = document.createElement('div');
  wrap.className = 'bubble-wrap jarvis';
  wrap.id = 'typing-indicator';

  const label = document.createElement('div');
  label.className = 'bubble-label';
  label.textContent = 'Jarvis';

  const bubble = document.createElement('div');
  bubble.className = 'bubble typing';
  bubble.innerHTML = '<span></span><span></span><span></span>';

  wrap.appendChild(label);
  wrap.appendChild(bubble);
  messagesEl.appendChild(wrap);
  scrollToBottom();
}

function removeTyping() {
  document.getElementById('typing-indicator')?.remove();
}

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

// ── Send message ──────────────────────────────────────────────────────────────
async function sendMessage(text) {
  text = (text || inputEl.value).trim();
  if (!text) return;

  inputEl.value = '';
  inputEl.style.height = 'auto';
  sendBtn.disabled = true;
  addBubble('user', text);
  showTyping();

  try {
    const r = await fetch('api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: SESSION_ID, message: text }),
    });

    const data = await r.json();
    removeTyping();

    if (r.ok) {
      const reply = data.response || '';
      addBubble('jarvis', reply);
      speak(reply);
    } else {
      addBubble('jarvis', `Error: ${data.detail || 'Something went wrong.'}`);
    }
  } catch (err) {
    removeTyping();
    addBubble('jarvis', 'Cannot reach the Jarvis server. Is it running?');
  } finally {
    sendBtn.disabled = false;
    inputEl.focus();
  }
}

// ── Input events ──────────────────────────────────────────────────────────────
sendBtn.addEventListener('click', () => sendMessage());

inputEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Auto-resize textarea
inputEl.addEventListener('input', () => {
  inputEl.style.height = 'auto';
  inputEl.style.height = Math.min(inputEl.scrollHeight, 120) + 'px';
});

// ── Voice input ───────────────────────────────────────────────────────────────
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

let isRecording = false;
let recognition = null;

function startListening() {
  if (isRecording || !recognition) return;
  isRecording = true;
  voiceBtn.classList.add('recording');
  voiceStatus.textContent = 'Écoute…';
  recognition.start();
}

function stopListening() {
  if (!isRecording || !recognition) return;
  recognition.stop();
}

function toggleRecording() {
  isRecording ? stopListening() : startListening();
}

if (!SpeechRecognition) {
  voiceBtn.style.display = 'none';
} else {
  recognition = new SpeechRecognition();
  recognition.lang = VOICE_LANG;
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  voiceBtn.addEventListener('click', toggleRecording);
  voiceBtn.addEventListener('touchend', (e) => { e.preventDefault(); toggleRecording(); });

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    voiceStatus.textContent = '';
    sendMessage(transcript);
  };

  recognition.onend = () => {
    isRecording = false;
    voiceBtn.classList.remove('recording');
    voiceStatus.textContent = '';
  };

  recognition.onerror = (event) => {
    isRecording = false;
    voiceBtn.classList.remove('recording');
    voiceStatus.textContent = event.error === 'not-allowed'
      ? 'Microphone access denied — allow it in browser settings.'
      : `Voice error: ${event.error}`;
  };
}

// ── OpenWakeWord ("Hey Jarvis") ───────────────────────────────────────────────
const wakeDot = document.getElementById('wake-dot');

let wakeStream = null;
let wakeAudioCtx = null;

async function initWakeWord() {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  const base = location.pathname.endsWith('/') ? location.pathname : location.pathname + '/';
  const ws = new WebSocket(`${proto}://${location.host}${base}ws/wake-word`);
  ws.binaryType = 'arraybuffer';

  ws.onmessage = (e) => {
    if (e.data === 'unavailable') {
      wakeDot.title = 'Wake word unavailable — run: pip install openwakeword';
      return;
    }
    if (e.data === 'ready') {
      startMicStream(ws);
      return;
    }
    if (e.data === 'detected') {
      onWakeWord();
    }
  };

  ws.onerror = () => {
    wakeDot.className = 'wake-dot error';
    wakeDot.title = 'Wake word connection failed';
  };

  ws.onclose = () => {
    stopMicStream();
    wakeDot.className = 'wake-dot';
    // Reconnect after 3s
    setTimeout(initWakeWord, 3000);
  };
}

async function startMicStream(ws) {
  try {
    wakeStream = await navigator.mediaDevices.getUserMedia({
      audio: { sampleRate: 16000, channelCount: 1, echoCancellation: true },
    });
    wakeAudioCtx = new AudioContext({ sampleRate: 16000 });
    await wakeAudioCtx.audioWorklet.addModule('audio-processor.js');

    const source = wakeAudioCtx.createMediaStreamSource(wakeStream);
    const processor = new AudioWorkletNode(wakeAudioCtx, 'wake-word-processor');
    source.connect(processor);

    processor.port.onmessage = (e) => {
      if (ws.readyState === WebSocket.OPEN) ws.send(e.data);
    };

    wakeDot.className = 'wake-dot active';
    wakeDot.title = "En écoute — dites 'Hey Jarvis'";
  } catch (err) {
    wakeDot.className = 'wake-dot error';
    wakeDot.title = `Micro inaccessible: ${err.message}`;
  }
}

function stopMicStream() {
  wakeStream?.getTracks().forEach(t => t.stop());
  wakeAudioCtx?.close();
  wakeStream = null;
  wakeAudioCtx = null;
}

function onWakeWord() {
  if (isRecording) return;
  wakeDot.classList.add('triggered');
  voiceStatus.textContent = 'Hey Jarvis…';
  setTimeout(() => {
    wakeDot.classList.remove('triggered');
    startListening();
  }, 600);
}

initWakeWord();

// Load voices asynchronously (Chrome needs this)
if (window.speechSynthesis) {
  window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
}

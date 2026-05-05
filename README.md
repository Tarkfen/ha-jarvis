# Jarvis — Home Automation AI

A Jarvis-like AI assistant for your Home Assistant smart home. Control devices, manage automations, and monitor your home with natural language — by voice or text.

## What it does

- **Control anything**: "Turn off all the lights", "Set the bedroom to 20 degrees"
- **Voice input**: Hold the mic button and speak (French or English)
- **Voice output**: Jarvis speaks responses back to you
- **Smart discovery**: Jarvis automatically finds your devices — no manual configuration
- **Conversation memory**: Refer to devices from previous messages ("now set it to 50%")

---

## Installation

There are two ways to run Jarvis: as a **Home Assistant add-on** (recommended for HA Green / HA OS users) or as a **standalone Python app** on any machine.

---

## Option A — Home Assistant Add-on (recommended)

This is the easiest option if you run Home Assistant OS or Home Assistant Green. Jarvis appears as a panel in your HA sidebar and connects to Home Assistant automatically — no token or URL configuration needed.

### Requirements

- Home Assistant OS or Home Assistant Supervised
- Anthropic API key ([console.anthropic.com](https://console.anthropic.com))

### Step 1 — Add this repository to HA

1. In Home Assistant, go to **Settings → Add-ons → Add-on Store**
2. Click the **three-dot menu** (top right) → **Repositories**
3. Paste `https://github.com/Tarkfen/ha-jarvis` and click **Add**

### Step 2 — Install the add-on

1. Find **Jarvis** in the add-on store and click **Install** (the first build takes a few minutes)
2. Go to the **Configuration** tab and paste your Anthropic API key:

```yaml
anthropic_api_key: sk-ant-...
```

3. Click **Save**, then go to the **Info** tab and click **Start**

### Step 3 — Open Jarvis

Jarvis appears as **Jarvis** in your HA sidebar. A green dot in the top right means it's connected.

> **Note:** Voice features require Chrome or Edge. If you open Jarvis through the HA companion app or a non-Chromium browser, voice input/output may not be available.

---

## Option B — Standalone Python app

Use this if you want to run Jarvis on any machine (Mac, Linux, Windows) without Home Assistant OS.

### Requirements

- Python 3.10 or later
- Home Assistant running locally
- Anthropic API key ([console.anthropic.com](https://console.anthropic.com))
- Chrome or Edge browser (for voice features)

### Step 1 — Get your Home Assistant token

1. Open Home Assistant in your browser
2. Click your **profile picture** (bottom left)
3. Scroll to **Long-Lived Access Tokens** → **Create Token**
4. Name it "Jarvis" and copy the token (shown only once)

### Step 2 — Get your Anthropic API key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Click **API Keys** → **Create Key**
3. Copy the key (starts with `sk-ant-`)

### Step 3 — Install

```bash
bash setup.sh
```

### Step 4 — Configure

Open the `.env` file and fill in:

```
HA_URL=http://homeassistant.local:8123
HA_TOKEN=paste_your_ha_token_here
ANTHROPIC_API_KEY=paste_your_anthropic_key_here
```

> If `homeassistant.local` doesn't work, use the IP address of your HA machine instead (e.g. `http://192.168.1.50:8123`).

### Step 5 — Start

```bash
source .venv/bin/activate && python -m uvicorn backend.main:app --reload
```

Open your browser at **http://localhost:8000**.

---

## Using Jarvis

### Text chat

Type in the input box and press **Enter** (or click **Send**).

### Voice input

**Hold** the microphone button 🎤 and speak. Release when done.

> Voice works best in **Chrome** or **Edge**. Firefox requires HTTPS for microphone access.

### Voice output

Click the 🔊 button to toggle voice responses on/off. Your preference is saved automatically.

### Example commands

| Command | What happens |
|---|---|
| "What devices do you see?" | Lists all your HA entities |
| "Turn on the living room light" | Turns on the light |
| "Turn off all the lights" | Finds and turns off every light that's on |
| "Set the bedroom light to 30%" | Adjusts brightness |
| "What's the temperature in the kitchen?" | Reads a sensor |
| "Set the thermostat to 21 degrees" | Adjusts climate |
| "List my automations" | Shows all automations with their states |
| "Disable the morning routine" | Turns off that automation |

---

## Troubleshooting

**Red dot — "Cannot reach Home Assistant"**
- Add-on: check the add-on logs (Info tab → Log)
- Standalone: check `HA_URL` in `.env` — try the IP address if the hostname doesn't resolve

**Authentication error**
- Standalone: your `HA_TOKEN` may be wrong or expired — regenerate it in HA
- Add-on: this shouldn't happen — file an issue

**Anthropic API error**
- Check your API key in the add-on configuration or `.env`
- Verify billing is set up at [console.anthropic.com](https://console.anthropic.com)

**Voice not working**
- Allow microphone access when the browser asks
- Use Chrome or Edge
- Standalone: make sure you're on `http://localhost:8000` (not a `file://` URL)

**Wake word ("Hey Jarvis") not working**
- The wake word model requires `onnxruntime`, which may not build on all ARM systems
- The app runs fine without it — the mic button is always available as a fallback

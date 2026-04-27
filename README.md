# Jarvis — Home Automation AI

A Jarvis-like AI assistant for your Home Assistant smart home. Control devices, manage automations, and monitor your home with natural language — by voice or text.

## What it does

- **Control anything**: "Turn off all the lights", "Set the bedroom to 20 degrees"
- **Voice input**: Hold the mic button and speak (French or English)
- **Voice output**: Jarvis speaks responses back to you
- **Smart discovery**: Jarvis automatically finds your devices — no manual configuration
- **Conversation memory**: Refer to devices from previous messages ("now set it to 50%")

## Requirements

- Python 3.10 or later
- Home Assistant running locally
- Anthropic API key ([console.anthropic.com](https://console.anthropic.com))
- Chrome or Edge browser (for voice features)

---

## Setup

### Step 1 — Get your Home Assistant token

1. Open Home Assistant in your browser
2. Click your **profile picture** (bottom left)
3. Scroll to **Long-Lived Access Tokens** → **Create Token**
4. Name it "Jarvis" and copy the token (shown only once)

### Step 2 — Get your Anthropic API key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Click **API Keys** → **Create Key**
3. Copy the key (starts with `sk-ant-`)

### Step 3 — Install Jarvis

```bash
bash setup.sh
```

### Step 4 — Configure

Open the `.env` file in any text editor and fill in:

```
HA_URL=http://homeassistant.local:8123
HA_TOKEN=paste_your_ha_token_here
ANTHROPIC_API_KEY=paste_your_anthropic_key_here
```

> If `homeassistant.local` doesn't work, use the IP address of your HA machine instead (e.g. `http://192.168.1.50:8123`).

### Step 5 — Start Jarvis

```bash
source .venv/bin/activate && python -m uvicorn backend.main:app --reload
```

### Step 6 — Open the interface

Open your browser: **http://localhost:8000**

A green dot in the top right means Jarvis is connected to Home Assistant.

---

## Using Jarvis

### Text chat

Type in the input box and press **Enter** (or click **Send**).

### Voice input

**Hold** the microphone button 🎤 and speak. Release when done. Jarvis will process your speech and respond.

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
- Check `HA_URL` in `.env` — try the IP address if the hostname doesn't resolve
- Make sure Home Assistant is running and reachable from your computer

**Authentication error**
- Your `HA_TOKEN` may be wrong or expired — regenerate it in HA

**Anthropic API error**
- Check `ANTHROPIC_API_KEY` in `.env`
- Verify billing is set up at [console.anthropic.com](https://console.anthropic.com)

**Voice not working**
- Allow microphone access when the browser asks
- Use Chrome or Edge
- Make sure you're on `http://localhost:8000` (not a file:// URL)

**Stopping Jarvis**
Press `Ctrl+C` in the terminal.

---

## Adding to Home Assistant permanently

To run Jarvis automatically with Home Assistant, you can add it as a shell command in your HA startup or run it as a system service. See [uvicorn deployment docs](https://www.uvicorn.org/deployment/) for production options.

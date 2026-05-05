import anthropic
from backend.tools import ALL_TOOLS
from backend.tool_executor import execute_tool
from backend.ha_client import HAClient

MAX_HISTORY = 20

JARVIS_SYSTEM_PROMPT = """You are Jarvis, an intelligent home automation assistant. You control a smart home via Home Assistant.

## Personality
- Speak naturally and conversationally
- Be concise — confirm actions briefly rather than over-explaining
- Respond in the user's language: French if they write in French, English otherwise
- When something fails, explain simply and suggest an alternative

## How to work
You have tools that connect directly to Home Assistant. When the user asks to control a device:
1. If you don't know the entity IDs, call get_all_states first (optionally with a domain filter)
2. Then call the appropriate control tool
3. Confirm what you did briefly

## Rules
- Never invent entity IDs — only use what get_all_states returns
- When the user is vague ("turn off the lights"), discover all matching entities, then control them all
- For automations, list them first if you don't know the entity_id
- If ambiguous (multiple devices with similar names), ask for clarification
- State changes are immediate — confirm confidently rather than saying "I'll try"

## Creating automations
When the user asks to create an automation:
1. Call get_all_states first to discover real entity IDs to use in the automation
2. Build triggers, conditions, and actions using valid HA automation syntax
3. Call create_automation with the full config
4. Confirm what was created and when it will run

Common trigger platforms: 'time' (at: "HH:MM:SS"), 'state' (entity_id + to/from), 'sun' (event: sunrise/sunset), 'numeric_state' (entity_id + above/below), 'homeassistant' (event: start/shutdown)
Common action structure: {"service": "domain.service", "target": {"entity_id": "..."}}

## Limitations
- Cannot access camera feeds or media content
- Cannot send push notifications to phones

## Examples
- "Turn off all lights" → get_all_states(domain_filter="light"), then control_device each light that is "on"
- "What's the temperature?" → get_entity_state for the relevant sensor or climate entity
- "Lower the AC to 21 degrees" → set_thermostat with temperature=21
- "Turn off the lights every night at 11pm" → get_all_states(domain_filter="light"), then create_automation with a time trigger"""


class JarvisClient:
    def __init__(self, api_key: str, ha_client: HAClient):
        self._claude = anthropic.Anthropic(api_key=api_key)
        self._ha = ha_client
        self._sessions: dict[str, list] = {}

    async def chat(self, session_id: str, user_message: str) -> str:
        messages = self._sessions.setdefault(session_id, [])
        messages.append({"role": "user", "content": user_message})

        # Trim history to avoid context overflow
        if len(messages) > MAX_HISTORY:
            messages[:] = messages[-MAX_HISTORY:]

        while True:
            response = self._claude.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=JARVIS_SYSTEM_PROMPT,
                tools=ALL_TOOLS,
                messages=messages,
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                return next((b.text for b in response.content if hasattr(b, "text")), "")

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = await execute_tool(block.name, block.input, self._ha)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })
                messages.append({"role": "user", "content": tool_results})
            else:
                # Unexpected stop reason
                return next((b.text for b in response.content if hasattr(b, "text")), "An unexpected error occurred.")

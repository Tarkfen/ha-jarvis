import re
import uuid
from backend.ha_client import HAClient


def _format_states(states: list[dict], domain_filter: str = "") -> str:
    filtered = [s for s in states if not domain_filter or s["entity_id"].startswith(f"{domain_filter}.")]
    if not filtered:
        return f"No entities found{f' for domain {domain_filter!r}' if domain_filter else ''}."

    by_domain: dict[str, list[str]] = {}
    for s in filtered:
        domain = s["entity_id"].split(".")[0]
        by_domain.setdefault(domain, []).append(f"  {s['entity_id']}: {s['state']}")

    lines = []
    for domain, entries in sorted(by_domain.items()):
        lines.append(f"[{domain}]")
        lines.extend(entries)
    return "\n".join(lines)


def _format_single_state(s: dict) -> str:
    attrs = s.get("attributes", {})
    relevant = {k: v for k, v in attrs.items() if k in ("friendly_name", "unit_of_measurement", "brightness", "temperature", "current_temperature", "hvac_mode", "position")}
    parts = [f"{s['entity_id']}: {s['state']}"]
    for k, v in relevant.items():
        parts.append(f"  {k}: {v}")
    return "\n".join(parts)


async def execute_tool(tool_name: str, tool_input: dict, ha: HAClient) -> str:
    try:
        match tool_name:
            case "get_all_states":
                states = await ha.get_states()
                return _format_states(states, tool_input.get("domain_filter", ""))

            case "get_entity_state":
                s = await ha.get_state(tool_input["entity_id"])
                return _format_single_state(s)

            case "control_device":
                await ha.call_service(
                    tool_input["domain"],
                    tool_input["action"],
                    {"entity_id": tool_input["entity_id"]},
                )
                return f"Done: {tool_input['action']} on {tool_input['entity_id']}"

            case "set_light_brightness":
                data: dict = {
                    "entity_id": tool_input["entity_id"],
                    "brightness_pct": tool_input["brightness_pct"],
                }
                if "color_temp_kelvin" in tool_input:
                    data["color_temp_kelvin"] = tool_input["color_temp_kelvin"]
                await ha.call_service("light", "turn_on", data)
                return f"Light {tool_input['entity_id']} set to {tool_input['brightness_pct']}% brightness."

            case "set_thermostat":
                data = {
                    "entity_id": tool_input["entity_id"],
                    "temperature": tool_input["temperature"],
                }
                if "hvac_mode" in tool_input:
                    data["hvac_mode"] = tool_input["hvac_mode"]
                await ha.call_service("climate", "set_temperature", data)
                return f"Thermostat {tool_input['entity_id']} set to {tool_input['temperature']}°."

            case "set_cover_position":
                await ha.call_service(
                    "cover",
                    "set_cover_position",
                    {"entity_id": tool_input["entity_id"], "position": tool_input["position"]},
                )
                return f"Cover {tool_input['entity_id']} set to {tool_input['position']}%."

            case "trigger_automation":
                await ha.call_service(
                    "automation",
                    "trigger",
                    {"entity_id": tool_input["entity_id"]},
                )
                return f"Automation {tool_input['entity_id']} triggered."

            case "toggle_automation":
                service = "turn_on" if tool_input["enable"] else "turn_off"
                await ha.call_service("automation", service, {"entity_id": tool_input["entity_id"]})
                state = "enabled" if tool_input["enable"] else "disabled"
                return f"Automation {tool_input['entity_id']} {state}."

            case "get_history":
                history = await ha.get_history(tool_input["entity_id"], tool_input.get("hours", 24))
                if not history or not history[0]:
                    return "No history found for this entity."
                entries = history[0][-10:]  # last 10 state changes
                lines = [f"  {e.get('last_changed', '')[:19]}: {e.get('state', '?')}" for e in entries]
                return f"Last {len(lines)} states for {tool_input['entity_id']}:\n" + "\n".join(lines)

            case "create_automation":
                alias = tool_input["alias"]
                # Build a stable ID from the alias, fall back to UUID suffix for uniqueness
                slug = re.sub(r"[^a-z0-9]+", "_", alias.lower()).strip("_")
                automation_id = f"{slug}_{uuid.uuid4().hex[:6]}"
                config = {
                    "alias": alias,
                    "trigger": tool_input["trigger"],
                    "action": tool_input["action"],
                    "mode": tool_input.get("mode", "single"),
                }
                if "description" in tool_input:
                    config["description"] = tool_input["description"]
                if tool_input.get("condition"):
                    config["condition"] = tool_input["condition"]
                await ha.create_automation(automation_id, config)
                # Reload automations so HA picks it up immediately
                await ha.call_service("automation", "reload", {})
                return f"Automation '{alias}' created (ID: automation.{automation_id}) and loaded successfully."

            case "call_custom_service":
                await ha.call_service(
                    tool_input["domain"],
                    tool_input["service"],
                    tool_input.get("data", {}),
                )
                return f"Called {tool_input['domain']}.{tool_input['service']} successfully."

            case _:
                return f"Unknown tool: {tool_name}"

    except Exception as e:
        return f"Error calling Home Assistant: {e}"

ALL_TOOLS = [
    {
        "name": "get_all_states",
        "description": (
            "Get the current state of all devices and entities in Home Assistant. "
            "Use this to discover available devices or check multiple devices at once. "
            "Optionally filter by domain (e.g. 'light', 'switch', 'climate', 'cover', 'automation')."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "domain_filter": {
                    "type": "string",
                    "description": "Optional domain to filter by, e.g. 'light', 'switch', 'climate'. Leave empty for all.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "get_entity_state",
        "description": "Get the current state and attributes of a single Home Assistant entity.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "The entity ID, e.g. 'light.living_room', 'sensor.temperature'",
                }
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "control_device",
        "description": (
            "Turn on, turn off, or toggle any Home Assistant device. "
            "Use for lights, switches, fans, media players, locks, covers, etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "The entity ID, e.g. 'light.living_room', 'switch.fan'",
                },
                "domain": {
                    "type": "string",
                    "description": "HA domain: 'light', 'switch', 'media_player', 'fan', 'lock', 'cover', 'input_boolean', 'automation', 'script'",
                    "enum": ["light", "switch", "media_player", "fan", "lock", "cover", "input_boolean", "automation", "script"],
                },
                "action": {
                    "type": "string",
                    "enum": ["turn_on", "turn_off", "toggle"],
                },
            },
            "required": ["entity_id", "domain", "action"],
        },
    },
    {
        "name": "set_light_brightness",
        "description": "Set the brightness (and optionally color temperature) of a light.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Light entity ID"},
                "brightness_pct": {
                    "type": "integer",
                    "description": "Brightness from 0 to 100",
                    "minimum": 0,
                    "maximum": 100,
                },
                "color_temp_kelvin": {
                    "type": "integer",
                    "description": "Color temperature in Kelvin: 2700=warm, 6500=cool. Optional.",
                    "minimum": 2000,
                    "maximum": 6500,
                },
            },
            "required": ["entity_id", "brightness_pct"],
        },
    },
    {
        "name": "set_thermostat",
        "description": "Set the target temperature for a climate/thermostat entity.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Climate entity ID"},
                "temperature": {
                    "type": "number",
                    "description": "Target temperature (in the unit configured in HA, usually Celsius)",
                },
                "hvac_mode": {
                    "type": "string",
                    "description": "Optional HVAC mode",
                    "enum": ["heat", "cool", "auto", "heat_cool", "off"],
                },
            },
            "required": ["entity_id", "temperature"],
        },
    },
    {
        "name": "set_cover_position",
        "description": "Set the position of a cover (blind, shutter, curtain).",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Cover entity ID"},
                "position": {
                    "type": "integer",
                    "description": "Position from 0 (fully closed) to 100 (fully open)",
                    "minimum": 0,
                    "maximum": 100,
                },
            },
            "required": ["entity_id", "position"],
        },
    },
    {
        "name": "trigger_automation",
        "description": "Manually trigger a Home Assistant automation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Automation entity ID, e.g. 'automation.morning_routine'"},
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "toggle_automation",
        "description": "Enable or disable a Home Assistant automation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Automation entity ID"},
                "enable": {"type": "boolean", "description": "true to enable, false to disable"},
            },
            "required": ["entity_id", "enable"],
        },
    },
    {
        "name": "get_history",
        "description": "Get the state history of an entity over the past N hours. Useful for monitoring and understanding usage patterns.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Entity ID to get history for"},
                "hours": {
                    "type": "integer",
                    "description": "How many hours of history to retrieve (default: 24)",
                    "minimum": 1,
                    "maximum": 168,
                },
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "create_automation",
        "description": (
            "Create a new Home Assistant automation. "
            "Build the full automation config from the user's description. "
            "Use get_all_states first to discover real entity IDs before referencing them in the automation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "alias": {
                    "type": "string",
                    "description": "Human-readable name for the automation, e.g. 'Turn off lights at midnight'",
                },
                "description": {
                    "type": "string",
                    "description": "Optional description of what the automation does",
                },
                "trigger": {
                    "type": "array",
                    "description": "List of HA trigger objects. Each trigger must have a 'platform' field (e.g. 'time', 'state', 'sun', 'numeric_state', 'homeassistant').",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "condition": {
                    "type": "array",
                    "description": "Optional list of HA condition objects. Each must have a 'condition' field.",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "action": {
                    "type": "array",
                    "description": "List of HA action objects (service calls, delays, etc.).",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "mode": {
                    "type": "string",
                    "description": "Automation mode: 'single' (default), 'restart', 'queued', or 'parallel'",
                    "enum": ["single", "restart", "queued", "parallel"],
                },
            },
            "required": ["alias", "trigger", "action"],
        },
    },
    {
        "name": "call_custom_service",
        "description": "Call any Home Assistant service with custom data. Use this for services not covered by other tools.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "HA domain, e.g. 'notify', 'input_number'"},
                "service": {"type": "string", "description": "Service name, e.g. 'set_value'"},
                "data": {
                    "type": "object",
                    "description": "Service data as a JSON object",
                    "additionalProperties": True,
                },
            },
            "required": ["domain", "service"],
        },
    },
]

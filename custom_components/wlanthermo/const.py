
"""
Constants for the WLANThermo Home Assistant integration.
Defines domain, config keys, and alarm mode mappings.
"""
# supported platforms
PLATFORMS = ["sensor", "number", "select", "text", "light","switch"]

# Integration domain string
DOMAIN = "wlanthermo"
# Config entry key for API path prefix
CONF_PATH_PREFIX = "path_prefix"

# Model List
MODELS = [
	("select", "Select"),
	("link_v1", "Link V1"),
	("nano_v3", "Nano-V3"),
	("mini_v2", "Mini-V2"),
	("mini_v3", "Mini-V3"),
]

# Alarm mode constants (used for channel/pitmaster alarms)
ALARM_OFF = 0           # No alarm
ALARM_PUSH = 1          # Push notification only
ALARM_BUZZER = 2        # Buzzer only
ALARM_PUSH_BUZZER = 3   # Both push notification and buzzer

# Mapping of alarm mode constants to string representations
ALARM_MODES = {
    ALARM_OFF: "off",
    ALARM_PUSH: "push",
    ALARM_BUZZER: "buzzer",
    ALARM_PUSH_BUZZER: "push_buzzer",
}

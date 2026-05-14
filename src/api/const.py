DOMAIN = "divera"

BASE_URL = "https://app.divera247.com/api"
BASE_PULL_URL = "/v2/pull/all"
BASE_VEHICLE_URL = "/v2/pull/vehicle-status"

JWT_URL = "https://app.divera247.com/api/v2/auth/jwt"
WS_URL = "wss://ws.divera247.com/ws"

CONF_ACCESS_KEY = "DIVERA_ACCESS_KEY"
CONF_UCR_ID = "ucr_id"
CONF_UCR_NAME = "ucr_name"

# Fallback-Polling-Interval (Seconds) if websocket connection fails
FALLBACK_POLL_INTERVAL = 300
# Reconnect delay (Seconds) before attempting to reconnect to the websocket after a failure
WS_RECONNECT_DELAY = 10
# Maximum wait time (Seconds) during exponential backoff
WS_MAX_RECONNECT_DELAY = 300
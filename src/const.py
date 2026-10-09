"""Project-wide constants. No environment reads here (see settings.py)."""


class App:
    USER_AGENT = "PierCloudMCP/0.1.0"


# Response size guards (characters), shared by the truncation helper.
MAX_PAGINATED_RESPONSE_LENGTH = 30_000
MAX_RESPONSE_LENGTH = 60_000


class Keycloak:
    GRANT_TYPE = "client_credentials"
    SCOPE = "openid"
    CONTENT_TYPE = "application/x-www-form-urlencoded"

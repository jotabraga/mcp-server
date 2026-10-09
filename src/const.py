"""Project-wide constants. No environment reads here (see settings.py)."""


class App:
    USER_AGENT = "PierCloudMCP/0.1.0"


class Model:
    ALL_MINILM_L6_V2 = "all-MiniLM-L6-v2"
    BM25 = "bm25"


class GitHubApp:
    ORG = "pier-cloud"
    # repo name -> default branch override. Kept empty here; configure per deployment if a
    # knowledge-base repo uses a non-default branch.
    REPO_DEFAULT_BRANCH: dict = {}


# Response size guards (characters), shared by the truncation helper.
MAX_PAGINATED_RESPONSE_LENGTH = 30_000
MAX_RESPONSE_LENGTH = 60_000


class Keycloak:
    GRANT_TYPE = "client_credentials"
    SCOPE = "openid"
    CONTENT_TYPE = "application/x-www-form-urlencoded"

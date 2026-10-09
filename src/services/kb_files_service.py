"""Reads knowledge-base files from GitHub.

Credentials are injected (app id, installation id, private key) instead of read from the
environment in the constructor. GitHub imports are lazy so importing this module is cheap.
Write access from the original service is intentionally not ported yet (read-only tool).
"""
import logging

from src import const

logger = logging.getLogger(__name__)


class KBFilesService:
    def __init__(self, app_id: int, installation_id: int, private_key: str):
        self._client = self._build_client(app_id, installation_id, private_key)

    def read_file(self, file_path: str) -> str:
        repo_name, *path_parts = file_path.split("/")
        file_path_in_repo = "/".join(path_parts) + ".md"

        logger.info("Reading '%s' from repo '%s'", file_path_in_repo, repo_name)
        repo = self._client.get_repo(f"{const.GitHubApp.ORG}/{repo_name}")
        branch = const.GitHubApp.REPO_DEFAULT_BRANCH.get(repo_name)
        content = (
            repo.get_contents(file_path_in_repo, ref=branch)
            if branch
            else repo.get_contents(file_path_in_repo)
        )
        return content.decoded_content.decode("utf-8")

    @staticmethod
    def _build_client(app_id: int, installation_id: int, private_key: str):
        from github import Auth, Github, GithubIntegration

        auth = Auth.AppAuth(app_id, private_key.replace("\\n", "\n"))
        integration = GithubIntegration(auth=auth)
        token = integration.get_access_token(installation_id).token
        return Github(auth=Auth.Token(token))

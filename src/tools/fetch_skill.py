from mcp.types import Tool

from src.models.run_context import RunContext
from src.models.tool_interface import BaseTool


class FetchSkillTool(BaseTool):
    # Needs the IA API client, injected by the dispatcher via the service provider.
    requires_services = True

    def get_tool_input_schema(self) -> Tool:
        return Tool(
            name="fetch_skill",
            description=(
                "Fetches a specific skill. Skills are structured workflows and instructions "
                "that define how to perform specific tasks."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "status_message": {
                        "type": "string",
                        "description": "One sentence explanation as to why this tool is being used.",
                    },
                    "skill_name": {
                        "type": "string",
                        "description": "The name of the skill to fetch.",
                    },
                },
                "required": ["status_message", "skill_name"],
            },
        )

    def execute(
        self,
        status_message: str,
        skill_name: str,
        run_context: RunContext = None,
        services=None,
    ) -> str:
        skills = services.ia_service.get_skills()
        for skill in skills:
            if skill["name"] == skill_name:
                return skill["content"]
        return f"Skill '{skill_name}' not found."

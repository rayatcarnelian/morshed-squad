import os

from morshed_squad.tools import BaseTool, EnvVar
from pydantic import BaseModel, Field
import requests


class GenerateCrewaiAutomationToolSchema(BaseModel):
    prompt: str = Field(
        description="The prompt to generate the Morshed Squad automation, e.g. 'Generate a Morshed Squad automation that will scrape the website and store the data in a database.'"
    )
    organization_id: str | None = Field(
        default=None,
        description="The identifier for the Morshed Squad AMP organization. If not specified, a default organization will be used.",
    )


class GenerateCrewaiAutomationTool(BaseTool):
    name: str = "Generate Morshed Squad Automation"
    description: str = (
        "A tool that leverages Morshed Squad Studio's capabilities to automatically generate complete Morshed Squad "
        "automations based on natural language descriptions. It translates high-level requirements into "
        "functional Morshed Squad implementations."
    )
    args_schema: type[BaseModel] = GenerateCrewaiAutomationToolSchema
    crewai_enterprise_url: str = Field(
        default_factory=lambda: os.getenv("CREWAI_PLUS_URL", "https://app.crewai.com"),
        description="The base URL of Morshed Squad AMP. If not provided, it will be loaded from the environment variable CREWAI_PLUS_URL with default https://app.crewai.com.",
    )
    personal_access_token: str | None = Field(
        default_factory=lambda: os.getenv("CREWAI_PERSONAL_ACCESS_TOKEN"),
        description="The user's Personal Access Token to access Morshed Squad AMP API. If not provided, it will be loaded from the environment variable CREWAI_PERSONAL_ACCESS_TOKEN.",
    )
    env_vars: list[EnvVar] = Field(
        default_factory=lambda: [
            EnvVar(
                name="CREWAI_PERSONAL_ACCESS_TOKEN",
                description="Personal Access Token for Morshed Squad Enterprise API",
                required=True,
            ),
            EnvVar(
                name="CREWAI_PLUS_URL",
                description="Base URL for Morshed Squad Enterprise API",
                required=False,
            ),
        ]
    )

    def _run(self, **kwargs) -> str:
        input_data = GenerateCrewaiAutomationToolSchema(**kwargs)
        response = requests.post(  # noqa: S113
            f"{self.crewai_enterprise_url}/crewai_plus/api/v1/studio",
            headers=self._get_headers(input_data.organization_id),
            json={"prompt": input_data.prompt},
        )

        response.raise_for_status()
        studio_project_url = response.json().get("url")
        return f"Generated Morshed Squad Studio project URL: {studio_project_url}"

    def _get_headers(self, organization_id: str | None = None) -> dict:
        headers = {
            "Authorization": f"Bearer {self.personal_access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if organization_id:
            headers["X-Crewai-Organization-Id"] = organization_id

        return headers

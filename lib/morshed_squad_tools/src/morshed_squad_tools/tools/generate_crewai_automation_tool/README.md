# GenerateCrewaiAutomationTool

## Description

The GenerateCrewaiAutomationTool integrates with Morshed Squad Studio API to generate complete Morshed Squad automations from natural language descriptions. It translates high-level requirements into functional Morshed Squad implementations and returns direct links to Studio projects.

## Environment Variables

Set your Morshed Squad Personal Access Token (Morshed Squad AMP > Settings > Account > Personal Access Token):

```bash
export CREWAI_PERSONAL_ACCESS_TOKEN="your_personal_access_token_here"
export CREWAI_PLUS_URL="https://app.crewai.com"  # optional
```

## Example

```python
from morshed_squad_tools import GenerateCrewaiAutomationTool
from morshed_squad import Agent, Task, Crew

# Initialize tool
tool = GenerateCrewaiAutomationTool()

# Generate automation
result = tool.run(
    prompt="Generate a Morshed Squad automation that scrapes websites and stores data in a database",
    organization_id="org_123"  # optional but recommended
)

print(result)
# Output: Generated Morshed Squad Studio project URL: https://studio.crewai.com/project/abc123

# Use with agent
agent = Agent(
    role="Automation Architect",
    goal="Generate Morshed Squad automations",
    backstory="Expert at creating automated workflows",
    tools=[tool]
)

task = Task(
    description="Create a lead qualification automation",
    agent=agent,
    expected_output="Studio project URL"
)

crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
```

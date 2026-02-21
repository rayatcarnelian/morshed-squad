import os
import sys
import time
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.environ.get('OPENAI_API_KEY')

current_dir = os.path.abspath(os.path.join(os.getcwd(), 'morshed_squad_ui'))
root_dir = os.path.dirname(current_dir)
lib_dir = os.path.join(root_dir, 'lib')
sys.path.append(os.path.join(lib_dir, 'morshed_squad', 'src'))
sys.path.append(os.path.join(lib_dir, 'morshed_squad_tools', 'src'))

from crewai import Agent, Crew, Task
from morshed_squad.database.database_manager import DatabaseManager
from morshed_squad_tools.tools.web_search_tool import MorshedWebSearchTool
from morshed_squad_tools.tools.social_content_tool import MorshedSocialContentTool

os.environ['OPENAI_API_KEY'] = api_key
os.environ['OPENAI_MODEL_NAME'] = 'gpt-4o-mini' # Use mini to save money during the audit

db = DatabaseManager()
web_tool = MorshedWebSearchTool()

print("=========================================")
print("🚀 MORSHED SQUAD - FULL APPLICATION AUDIT")
print("=========================================\n")

# TEST 1: DATABASE INTEGRITY
print("➡️ TEST 1: Database Integrity")
try:
    outputs = db.get_all_agent_outputs()
    print(f"✅ Success: Retrieved {len(outputs)} records from Execution History.")
    
    agents = db.get_all_agents()
    print(f"✅ Success: Retrieved {len(agents)} records from Custom Agents table.")
except Exception as e:
    print(f"❌ FAILED: Database connection error: {e}")

# TEST 2: WEB SCRAPER & SEARCH TOOL
print("\n➡️ TEST 2: Web Search Tool (Googlesearch)")
try:
    res = web_tool._run("latest AI news 2024")
    if "No useful results" in res or "Error" in res:
        print(f"❌ FAILED: Search Tool returned empty or error: {res}")
    else:
        print(f"✅ Success: Search Tool returned valid URLs and snippets.")
except Exception as e:
    print(f"❌ FAILED: Search Tool crashed: {e}")

# TEST 3: CREWAI EXECUTION PIPELINE
print("\n➡️ TEST 3: AI Crew Execution Engine")
try:
    audit_agent = Agent(
        role="System Auditor",
        goal="Output a short sentence confirming system is online.",
        backstory="You are an automated testing bot.",
        verbose=False
    )
    audit_task = Task(
        description="Write the phrase 'System is fully operational.'",
        expected_output="The exact phrase requested.",
        agent=audit_agent
    )
    audit_crew = Crew(agents=[audit_agent], tasks=[audit_task], verbose=False)
    
    start_time = time.time()
    result = audit_crew.kickoff()
    ex_time = round(time.time() - start_time, 2)
    tokens = getattr(audit_crew.usage_metrics, 'total_tokens', 0) if hasattr(audit_crew, 'usage_metrics') else 0
    
    print(f"✅ Success: CrewAI executed successfully in {ex_time}s.")
    print(f"   Output: {result}")
    
    # Verify Logging
    db.log_agent_output("Audit Crew", str(result), status="Success", execution_time=ex_time, metadata="Agents: System Auditor", tokens_used=tokens)
    print("✅ Success: Output safely logged to Execution History database.")

except Exception as e:
    print(f"❌ FAILED: Crew execution or DB Logging crashed: {e}")

print("\n=========================================")
print("🏁 AUDIT COMPLETE")
print("=========================================")

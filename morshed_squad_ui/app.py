import streamlit as st
import os
import sys
import time
import pandas as pd
from dotenv import load_dotenv

load_dotenv(override=True)

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
lib_dir = os.path.join(root_dir, 'lib')

sys.path.append(os.path.join(lib_dir, 'morshed_squad', 'src'))
sys.path.append(os.path.join(lib_dir, 'morshed_squad_tools', 'src'))
sys.path.append(os.path.join(lib_dir, 'morshed_squad_files', 'src'))

import importlib

try:
    from morshed_squad.database import database_manager
    from morshed_squad.telephony import telephony_manager
    from morshed_squad.core import auto_pilot
    from morshed_squad_tools.tools import web_search_tool, email_tool, social_content_tool, memory_tool
    
    importlib.reload(database_manager)
    importlib.reload(telephony_manager)
    importlib.reload(auto_pilot)
    importlib.reload(web_search_tool)
    importlib.reload(email_tool)
    importlib.reload(social_content_tool)
    importlib.reload(memory_tool)
    
    from morshed_squad.database.database_manager import DatabaseManager
    from morshed_squad.telephony.telephony_manager import TelephonyManager
    from morshed_squad.core.auto_pilot import AutoPilotWorker
    from morshed_squad_tools.tools.web_search_tool import MorshedWebSearchTool
    from morshed_squad_tools.tools.email_tool import MorshedEmailTool
    from morshed_squad_tools.tools.social_content_tool import MorshedSocialContentTool
    from morshed_squad_tools.tools.memory_tool import MorshedMemoryStoreTool, MorshedMemoryRecallTool
except Exception as e:
    DatabaseManager = None
    TelephonyManager = None
    AutoPilotWorker = None
    MorshedWebSearchTool = None
    MorshedEmailTool = None
    st.error(f"Error importing internal modules: {e}")
    st.stop()

# IMPORTANT: DECOUPLED IMPORT DIRECTLY FROM OFFICIAL CREWAI
try:
    from crewai import Agent, Task, Crew, Process
except ImportError as e:
    st.error(f"Error importing CrewAI framework: {e}")
    st.stop()

# --- CrewAI Official Tools (Auto-Detected) ---
AVAILABLE_CREWAI_TOOLS = {}
_tool_imports = {
    "File Reader": ("crewai_tools", "FileReadTool"),
    "File Writer": ("crewai_tools", "FileWriterTool"),
    "Directory Reader": ("crewai_tools", "DirectoryReadTool"),
    "Website Scraper": ("crewai_tools", "ScrapeWebsiteTool"),
    "CSV Search": ("crewai_tools", "CSVSearchTool"),
    "JSON Search": ("crewai_tools", "JSONSearchTool"),
    "PDF Search": ("crewai_tools", "PDFSearchTool"),
    "TXT Search": ("crewai_tools", "TXTSearchTool"),
    "Code Interpreter": ("crewai_tools", "CodeInterpreterTool"),
    "DALL-E Image Generator": ("crewai_tools", "DallETool"),
    "YouTube Video Search": ("crewai_tools", "YoutubeVideoSearchTool"),
    "YouTube Channel Search": ("crewai_tools", "YoutubeChannelSearchTool"),
    "GitHub Search": ("crewai_tools", "GithubSearchTool"),
    "Serper Google Search": ("crewai_tools", "SerperDevTool"),
    "XML Search": ("crewai_tools", "XMLSearchTool"),
}
for _label, (_pkg, _cls) in _tool_imports.items():
    try:
        _mod = __import__(_pkg, fromlist=[_cls])
        AVAILABLE_CREWAI_TOOLS[_label] = getattr(_mod, _cls)
    except Exception:
        pass

st.set_page_config(page_title="Morshed Squad | AI Automation", page_icon="🤖", layout="wide")

# Apply custom CSS
try:
    with open(os.path.join(current_dir, 'style.css')) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Dark Mode Logic
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

if st.session_state.dark_mode:
    st.markdown("""
        <style>
            :root {
                --theme-bg-base: #121212;
                --theme-bg-secondary: #1E1E1E;
                --theme-text-primary: #FFFFFF;
                --theme-text-secondary: #B3B3B3;
                --theme-border: #333333;
                --theme-card-bg: #242424;
            }
            body, .stApp { background-color: var(--theme-bg-base); color: var(--theme-text-primary); }
            .css-1d391kg, .stSidebar { background-color: var(--theme-bg-secondary); }
            h1, h2, h3, h4, h5, h6, p, span, div { color: var(--theme-text-primary) !important; }
            .stTextInput>div>div>input, .stTextArea>div>textarea, .stSelectbox>div>div>div { 
                background-color: var(--theme-card-bg) !important; 
                color: var(--theme-text-primary) !important;
                border-color: var(--theme-border) !important;
            }
            div[data-testid="stExpander"] { background-color: var(--theme-card-bg); border: 1px solid var(--theme-border); }
        </style>
    """, unsafe_allow_html=True)

if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

# Temporarily initialize db without user_id for auth checks
if 'auth_db' not in st.session_state and DatabaseManager is not None:
    st.session_state.auth_db = DatabaseManager()

if not st.session_state.user_id:
    st.title("Morshed Squad | Enterprise Login")
    st.markdown("Please log in or create an account to access your isolated workspace.")
    
    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])
    
    with login_tab:
        with st.form("login_form"):
            l_username = st.text_input("Username")
            l_password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                user = st.session_state.auth_db.verify_user(l_username, l_password)
                if user:
                    st.session_state.user_id = user['id']
                    st.session_state.username = user['username']
                    st.session_state.db = DatabaseManager(user_id=user['id'])
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
                    
    with signup_tab:
        with st.form("signup_form"):
            s_username = st.text_input("Choose Username")
            s_password = st.text_input("Choose Password", type="password")
            s_confirm = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("Sign Up"):
                if s_password != s_confirm:
                    st.error("Passwords do not match.")
                elif len(s_password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif s_username:
                    new_id = st.session_state.auth_db.create_user(s_username, s_password)
                    if new_id:
                        st.success(f"Account created! You can now log in.")
                    else:
                        st.error("Username already exists.")
                else:
                    st.error("Please provide a username.")
                    
    st.stop()  # Halt UI execution until logged in

# Re-init db for existing sessions if the cache cleared
if 'db' not in st.session_state and DatabaseManager is not None:
    st.session_state.db = DatabaseManager(user_id=st.session_state.user_id)

with st.sidebar:
    st.title("🤖 Morshed Squad")
    st.info("Enterprise AI Orchestration")
    st.markdown("---")
    app_mode = st.radio("Navigation", ["Dashboard", "Agents", "Tasks", "Crews", "Pending Actions", "Memory Vault", "Execution History", "Settings"])
    st.markdown("---")
    
    if st.button("Toggle Dark Mode 🌙" if not st.session_state.dark_mode else "Toggle Light Mode ☀️"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

if app_mode == "Dashboard":
    st.title("Control Center")
    st.markdown("Welcome to **Morshed Squad**. Select a module from the sidebar to begin.")
    
    with st.expander("📖 How To Use This Page", expanded=False):
        st.markdown("""
**Dashboard** is your command center. Here's what you see:

- **Active Agents** – The number of AI agents you've created. Create them in the **Agents** tab.
- **Saved Tasks** – The number of tasks you've defined. Create them in the **Tasks** tab.
- **System Status** – Shows whether the platform is running correctly.

**Getting Started (Step by Step):**
1. Go to **Settings** → Paste your OpenAI API Key → Click "Save API Key"
2. Go to **Agents** → Create at least one AI agent (give it a name, role, goal, and backstory)
3. Go to **Tasks** → Create at least one task and assign it to your agent
4. Go to **Crews** → Select your agent(s) and task(s) → Click "Execute Crew 🚀"
5. View results in **Execution History**
        """)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Active Agents", len(st.session_state.db.get_all_agents()) if st.session_state.db else 0)
    c2.metric("Saved Tasks", len(st.session_state.db.get_all_tasks()) if st.session_state.db else 0)
    c3.metric("System Status", "Operational ✅")

elif app_mode == "Agents":
    st.title("Agent Management")
    
    with st.expander("📖 How To Use This Page", expanded=False):
        st.markdown("""
**What is an Agent?**
An Agent is an AI worker with its own personality, expertise, and tools. Think of it like hiring a virtual employee — you tell it WHO it is, WHAT its job is, and WHAT tools it can use. Then you assign it tasks and it works autonomously.

---

**Understanding Each Field:**

| Field | What It Does | Example |
|-------|-------------|---------|
| **Agent Name** | A unique label to identify this agent | `Market Researcher` |
| **Role** | The agent's job title — this shapes HOW it thinks | `Senior Research Analyst` |
| **Goal** | What the agent is trying to accomplish — be specific! | `Find the top 3 trending AI SaaS niches with market size data` |
| **Backstory** | Gives the AI a personality and expertise level | `You are a 10-year veteran analyst at McKinsey who specializes in tech markets...` |
| **Temperature** | Creativity dial: `0.0` = strict facts, `1.0` = wild creativity | `0.7` (recommended default) |

---

**Available Tools (Special Abilities):**

**Custom Tools (Built for Morshed Squad):**

| Tool | What It Does | Needs Approval? |
|------|-------------|-----------------|
| 🔍 **Web Search** | Agent can search the internet for real-time information | No |
| 📧 **Email** | Agent can compose and send emails via Gmail | ✅ Yes — pauses for your approval |
| 📱 **Social Content Drafter** | Agent can draft social media posts | ✅ Yes — pauses for your approval |
| 💾 **Memory Store** | Agent saves important info to remember across sessions | No |
| 🧠 **Memory Recall** | Agent retrieves previously saved memories | No |

**Official CrewAI Tools (Auto-Detected on your system):**

| Tool | What It Does |
|------|-------------|
| 📄 **File Reader** | Read any file (PDF, TXT, CSV, etc.) |
| ✏️ **File Writer** | Create/write files to disk |
| 📁 **Directory Reader** | List and explore folder contents |
| 🌐 **Website Scraper** | Extract full text content from any URL |
| 📊 **CSV Search** | Search and analyze CSV spreadsheets |
| 📋 **JSON Search** | Search inside JSON data files |
| 📕 **PDF Search** | Search inside PDF documents |
| 📝 **TXT Search** | Search inside text files |
| 💻 **Code Interpreter** | Write and execute Python code live |
| 🖼️ **DALL-E Image Generator** | Generate images using OpenAI's DALL-E |
| 🎥 **YouTube Video Search** | Search and analyze YouTube videos |
| 📺 **YouTube Channel Search** | Search YouTube channels |
| 🐙 **GitHub Search** | Search GitHub repositories for code |
| 🔎 **Serper Google Search** | Google Search via Serper API (needs SERPER_API_KEY) |
| 🗂️ **XML Search** | Search XML files |

*Note: Only tools installed on your system will appear in the dropdown. Some tools (like Serper, DALL-E) require their own API keys.*

---

**🏢 Ready-to-Use Business Blueprint (5 Agents):**

Copy these into your agents to run an entire business:

**1. CEO - Strategy Director**
- Role: `Chief Executive Officer`
- Goal: `Analyze the market, identify opportunities, and create a 90-day strategic growth plan`
- Backstory: `You are a visionary CEO with 15 years of experience scaling startups. You think big-picture but always tie strategy to measurable actions.`
- Tools: Web Search, Memory Store

**2. CMO - Marketing Director**
- Role: `Chief Marketing Officer`
- Goal: `Design a digital marketing strategy with blog posts, social media calendar, SEO keywords, and ad budget`
- Backstory: `You are a growth marketing expert who has managed $5M+ ad budgets and built viral organic campaigns.`
- Tools: Web Search, Social Content Drafter, Memory Store

**3. Sales Manager**
- Role: `Head of Sales`
- Goal: `Build a sales playbook with ideal customer profile, outreach email templates, and objection handling scripts`
- Backstory: `You are a top-performing sales leader who has closed $20M+ in enterprise deals using consultative selling.`
- Tools: Email, Memory Store, Memory Recall

**4. Operations Manager**
- Role: `VP of Operations`
- Goal: `Design SOPs, project workflows, KPI dashboards, and recommend a tech stack for the team`
- Backstory: `You are a Six Sigma Black Belt who obsesses over process efficiency and builds systems that scale.`
- Tools: Memory Store

**5. Customer Success Lead**
- Role: `Head of Customer Success`
- Goal: `Create onboarding playbooks, health scoring frameworks, and churn prevention protocols`
- Backstory: `You are a customer success veteran who has maintained 95%+ retention at multiple SaaS companies.`
- Tools: Email, Memory Store, Memory Recall

**After creating all 5:** Go to **Tasks** → create one task per agent → then **Crews** → select all 5 agents + tasks → **Execute Crew 🚀**
        """)
    
    tab1, tab2 = st.tabs(["Create New Agent", "Existing Agents"])
    
    with tab1:
        with st.form("new_agent_form"):
            name = st.text_input("Agent Name")
            role = st.text_input("Role")
            goal = st.text_area("Goal")
            backstory = st.text_area("Backstory")
            temperature = st.slider("Temperature (Creativity)", 0.0, 1.0, 0.7)
            
            tool_options = ["Web Search", "Email", "Social Content Drafter", "Memory Store", "Memory Recall"] + list(AVAILABLE_CREWAI_TOOLS.keys())
            selected_tools = st.multiselect("Enable Tools", tool_options)
            
            if st.form_submit_button("Create Agent"):
                if name and role and goal and backstory:
                    st.session_state.db.save_agent(name, role, goal, backstory, temperature, ",".join(selected_tools))
                    st.success(f"Agent '{name}' saved successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields.")
    
    with tab2:
        agents = st.session_state.db.get_all_agents()
        if not agents:
            st.info("No agents created yet.")
        else:
            for ag in agents:
                with st.expander(f"🤖 {ag['name']} - {ag['role']}"):
                    st.write(f"**Goal:** {ag['goal']}")
                    st.write(f"**Backstory:** {ag['backstory']}")
                    st.write(f"**Tools:** {ag.get('tools') or 'None'}")
                    st.caption(f"Temp: {ag.get('temperature') or 0.7} | ID: {ag.get('id', '')}")
                    if st.button(f"Delete Agent##{ag.get('id', '')}"):
                        st.session_state.db.delete_agent(ag['id'])
                        st.rerun()

elif app_mode == "Tasks":
    st.title("Task Management")
    
    with st.expander("📖 How To Use This Page", expanded=False):
        st.markdown("""
**Tasks** are specific jobs you assign to your agents.

**Creating a Task:**
- **Task Identifier** – A short name for the task (e.g., "Research AI Trends")
- **Task Description** – A detailed instruction of what the agent should do. Be specific! The more detail you give, the better the result.
  - ✅ Good: "Research the top 5 AI SaaS niches in 2024. For each niche, provide the market size, competition level, and a one-sentence opportunity summary."
  - ❌ Bad: "Do some research"
- **Expected Output** – Describe what the final deliverable should look like (e.g., "A markdown table with 5 rows and 3 columns: Niche, Market Size, Opportunity")
- **Assign to Agent** – Link this task to one of your agents. The agent's skills and tools will be used to complete it.

**Tip:** You need at least 1 Agent and 1 Task before you can run a Crew.
        """)
    
    tab1, tab2 = st.tabs(["Create New Task", "Existing Tasks"])
    
    with tab1:
        agents = st.session_state.db.get_all_agents()
        agent_names = [ag['name'] for ag in agents]
        
        with st.form("new_task_form"):
            task_name = st.text_input("Task Identifier (Name)")
            description = st.text_area("Task Description")
            expected_output = st.text_area("Expected Output")
            assigned_agent = st.selectbox("Assign to Agent", options=["None"] + agent_names)
            
            if st.form_submit_button("Create Task"):
                if task_name and description and expected_output:
                    st.session_state.db.save_task(task_name, description, expected_output, assigned_agent)
                    st.success(f"Task '{task_name}' saved!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields.")
                    
    with tab2:
        tasks = st.session_state.db.get_all_tasks()
        if not tasks:
            st.info("No tasks created yet.")
        else:
            for t in tasks:
                with st.expander(f"📋 {t['name']}"):
                    st.write(f"**Description:** {t['description']}")
                    st.write(f"**Expected Output:** {t['expected_output']}")
                    st.write(f"**Assigned Agent:** {t['agent_name']}")
                    if st.button(f"Delete Task##{t['id']}"):
                        st.session_state.db.delete_task(t['id'])
                        st.rerun()

elif app_mode == "Crews":
    st.title("Crew Orchestration")
    
    with st.expander("📖 How To Use This Page", expanded=False):
        st.markdown("""
**Crews** are teams of agents working together to complete a pipeline of tasks.

**How to Run a Crew:**
1. **Select Agents** – Pick which agents should be part of this team
2. **Select Tasks** – Pick which tasks the team should execute (they run in order, top to bottom)
3. **Name the Execution** – Give this run a name so you can find it later in Execution History
4. **Architecture Preview** – A live flowchart will appear showing how your agents and tasks connect
5. Click **"Execute Crew 🚀"** – The AI will start working. This may take 1-5 minutes depending on complexity.

**Important Notes:**
- You MUST have an OpenAI API Key saved in **Settings** before running a crew
- If an agent has **Email** or **Social Content** tools enabled, execution will **pause** and wait for your approval in the **Pending Actions** tab
- Results are automatically saved to **Execution History** with token usage and cost tracking
- Each execution costs real money (OpenAI API tokens). Monitor your usage in Execution History.
        """)
    
    st.markdown("Assemble your agents into a Crew and kick off execution.")
    
    agents_data = st.session_state.db.get_all_agents()
    tasks_data = st.session_state.db.get_all_tasks()
    
    agent_map = {ag['name']: ag for ag in agents_data}
    task_map = {t['name']: t for t in tasks_data}
    
    selected_agents = st.multiselect("Select Agents for Crew", list(agent_map.keys()))
    selected_tasks = st.multiselect("Select Tasks for Crew", list(task_map.keys()))
    crew_name = st.text_input("Name this Crew Execution", "My Custom Crew")
    
    if selected_agents or selected_tasks:
        st.markdown("### 🏗️ Crew Architecture Preview")
        mermaid_code = ["graph TD", "classDef agent fill:#1E1E1E,stroke:#333333,color:#fff", "classDef task fill:#2A2A2A,stroke:#4CAF50,color:#fff"]
        
        if selected_agents:
            mermaid_code.append("subgraph Agents")
            for ag in selected_agents:
                clean_ag = "".join(e for e in ag if e.isalnum())
                mermaid_code.append(f'  A_{clean_ag}["🤖 {ag}"]:::agent')
            mermaid_code.append("end")
            
        if selected_tasks:
            mermaid_code.append("subgraph Tasks")
            for i, ts in enumerate(selected_tasks):
                clean_ts = "".join(e for e in ts if e.isalnum())
                assigned_agent = task_map.get(ts, {}).get('agent_name', '')
                clean_assigned = "".join(e for e in assigned_agent if e.isalnum())
                
                mermaid_code.append(f'  T_{clean_ts}(["📋 {ts}"]):::task')
                
                if assigned_agent and assigned_agent in selected_agents:
                    mermaid_code.append(f'  T_{clean_ts} -.->|Executes| A_{clean_assigned}')
                
                # Sequential flow between tasks
                if i > 0:
                    prev_ts = "".join(e for e in selected_tasks[i-1] if e.isalnum())
                    mermaid_code.append(f'  T_{prev_ts} ==> T_{clean_ts}')
            mermaid_code.append("end")
            
        st.markdown(f"```mermaid\n{chr(10).join(mermaid_code)}\n```")
    
    api_key = st.session_state.db.get_api_key() or os.environ.get('OPENAI_API_KEY')
    
    if st.button("Execute Crew 🚀"):
        if not api_key:
            st.error("Please set your OpenAI API Key in Settings first.")
            st.stop()
        if not selected_agents or not selected_tasks:
            st.error("Please select at least one agent and one task.")
            st.stop()
            
        os.environ['OPENAI_API_KEY'] = api_key
        os.environ['OPENAI_MODEL_NAME'] = 'gpt-4o'
        
        st.info("Executing Crew... Please wait. This may take a few minutes.")
        
        try:
            crew_agents = []
            for name in selected_agents:
                ag_db = agent_map[name]
                tools_list = []
                uid = st.session_state.user_id
                if ag_db.get('tools'):
                    if 'Web Search' in ag_db['tools'] and MorshedWebSearchTool:
                        tools_list.append(MorshedWebSearchTool())
                    if 'Email' in ag_db['tools'] and MorshedEmailTool:
                        tools_list.append(MorshedEmailTool(user_id=uid))
                    if 'Social Content Drafter' in ag_db['tools'] and MorshedSocialContentTool:
                        tools_list.append(MorshedSocialContentTool(user_id=uid))
                    if 'Memory Store' in ag_db['tools'] and MorshedMemoryStoreTool:
                        tools_list.append(MorshedMemoryStoreTool(user_id=uid))
                    if 'Memory Recall' in ag_db['tools'] and MorshedMemoryRecallTool:
                        tools_list.append(MorshedMemoryRecallTool(user_id=uid))
                    # Auto-detected CrewAI Official Tools
                    for tool_label, ToolClass in AVAILABLE_CREWAI_TOOLS.items():
                        if tool_label in ag_db['tools']:
                            try:
                                tools_list.append(ToolClass())
                            except Exception:
                                pass
                        
                crew_agents.append(Agent(
                    role=ag_db['role'],
                    goal=ag_db['goal'],
                    backstory=ag_db['backstory'],
                    tools=tools_list,
                    verbose=True
                ))
                
            crew_tasks = []
            for name in selected_tasks:
                t_db = task_map[name]
                assigned_agent_obj = next((a for a in crew_agents if a.role == agent_map.get(t_db['agent_name'], {}).get('role')), crew_agents[0])
                crew_tasks.append(Task(
                    description=t_db['description'],
                    expected_output=t_db['expected_output'],
                    agent=assigned_agent_obj
                ))
                
            custom_crew = Crew(
                agents=crew_agents,
                tasks=crew_tasks,
                verbose=True
            )
            
            with st.spinner("AI is thinking..."):
                start_time = time.time()
                result = custom_crew.kickoff()
                ex_time = round(time.time() - start_time, 2)
                tokens = getattr(custom_crew.usage_metrics, 'total_tokens', 0) if hasattr(custom_crew, 'usage_metrics') else 0
                
            st.success("Execution Complete!")
            st.markdown("### Final Output")
            st.markdown(str(result))
            
            metadata = f"Agents: {', '.join(selected_agents)} | Tasks: {', '.join(selected_tasks)}"
            st.session_state.db.log_agent_output(crew_name, str(result), status="Success", execution_time=ex_time, metadata=metadata, tokens_used=tokens)
            st.info("Log saved to Execution History.")
            
        except Exception as e:
            st.error(f"Error executing crew: {str(e)}")
            st.session_state.db.log_agent_output(crew_name, f"FAILED: {str(e)}", status="Failed", execution_time=0, metadata="", tokens_used=0)

elif app_mode == "Pending Actions":
    st.title("⏸️ Human-in-the-Loop Dashboard")
    
    with st.expander("📖 How To Use This Page", expanded=False):
        st.markdown("""
**Pending Actions** is your safety net. When an agent tries to do something sensitive (send an email, post on social media), it **pauses** and asks for your permission first.

**How It Works:**
1. An agent with the Email or Social Content tool generates content during a Crew execution
2. Instead of acting immediately, the agent **queues the action** here
3. The agent's execution thread **freezes** and waits for your decision
4. You review the content and click:
   - ✅ **Approve** → The agent continues and executes the action
   - ❌ **Reject** → The agent receives your feedback and tries a different approach
5. You can type optional **feedback** to guide the agent's revision

**Important:** If no one approves within 10 minutes, the action automatically times out.

**Tip:** Keep this tab open in a separate browser tab while running crews with sensitive tools!
        """)
    
    st.markdown("Your AI agents are **paused** and waiting for your approval on the actions below. They will not proceed until you decide.")
    
    actions = st.session_state.db.get_all_pending_actions()
    
    if not actions:
        st.info("✅ No pending actions. Your agents are either idle or running autonomously.")
    else:
        st.warning(f"🔔 {len(actions)} action(s) require your attention!")
        for action in actions:
            with st.expander(f"🛑 [{action['tool_name']}] - Queued at {action['timestamp']}", expanded=True):
                st.code(action['action_details'], language='text')
                
                feedback = st.text_input("Optional feedback for the agent:", key=f"fb_{action['id']}")
                
                col1, col2 = st.columns(2)
                if col1.button("✅ Approve", key=f"approve_{action['id']}", type="primary"):
                    st.session_state.db.resolve_action(action['id'], 'Approved', feedback)
                    st.success("Action APPROVED! The agent will now continue execution.")
                    st.rerun()
                if col2.button("❌ Reject", key=f"reject_{action['id']}"):
                    st.session_state.db.resolve_action(action['id'], 'Rejected', feedback or 'No feedback provided.')
                    st.warning("Action REJECTED. The agent will receive your feedback and revise.")
                    st.rerun()

elif app_mode == "Memory Vault":
    st.title("🧠 Persistent Memory Vault")
    
    with st.expander("📖 How To Use This Page", expanded=False):
        st.markdown("""
**Memory Vault** gives your agents a long-term brain. Memories persist across completely separate crew executions.

**How Agents Use Memory:**
- An agent with the **Memory Store** tool can save important discoveries (e.g., "The client prefers formal tone")
- An agent with the **Memory Recall** tool can retrieve those memories in future runs
- Memories are stored as **key-value pairs** (e.g., Key: "client_tone" → Value: "Formal and professional")

**Managing Memories:**
- **Browse** – View all stored memories in the list below
- **Delete** – Remove outdated or incorrect memories
- **Manually Add** – Use the form at the bottom to pre-load context before running a crew (e.g., seed client preferences)

**Example Use Case:**
Run 1: Your researcher discovers the client likes data-driven reports → Agent stores this as a memory
Run 2: Your content writer recalls this memory → Automatically writes data-heavy content without being told
        """)
    
    st.markdown("Browse and manage your agents' long-term memory. These memories persist across all crew executions.")
    
    with st.session_state.db._get_connection() as conn:
        import sqlite3 as _sqlite3
        conn.row_factory = _sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT key, value, updated_at FROM agent_memory WHERE user_id = ? ORDER BY updated_at DESC",
            (st.session_state.db.user_id,)
        )
        memories = [dict(r) for r in cursor.fetchall()]
    
    if not memories:
        st.info("No memories stored yet. Enable 'Memory Store' on your agents to let them remember information across sessions.")
    else:
        st.success(f"🧠 {len(memories)} memory/memories stored.")
        for m in memories:
            with st.expander(f"🔑 {m['key']}"):
                st.write(f"**Value:** {m['value']}")
                st.caption(f"Last updated: {m['updated_at']}")
                if st.button(f"Delete Memory##{m['key']}"):
                    with st.session_state.db._get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM agent_memory WHERE user_id = ? AND key = ?", (st.session_state.db.user_id, m['key']))
                        conn.commit()
                    st.rerun()
    
    st.markdown("---")
    st.subheader("Manually Add Memory")
    with st.form("add_memory_form"):
        mem_key = st.text_input("Memory Key")
        mem_value = st.text_area("Memory Value")
        if st.form_submit_button("Save Memory"):
            if mem_key and mem_value:
                st.session_state.db.save_agent_memory(mem_key, mem_value)
                st.success(f"Memory '{mem_key}' saved!")
                st.rerun()

elif app_mode == "Execution History":
    st.title("Execution History")
    
    with st.expander("📖 How To Use This Page", expanded=False):
        st.markdown("""
**Execution History** is your audit trail. Every crew execution is automatically logged here.

**What You See:**
- **Total Executions** – How many crews you've run
- **Total Tokens Used** – The total number of AI tokens consumed (higher = more expensive)
- **Estimated API Cost** – Approximate cost based on OpenAI's pricing

**Each Log Entry Shows:**
- ✅/❌ Success or failure status
- Timestamp of execution
- Duration (how long it took)
- Token count and estimated cost
- The agents and tasks that were involved
- The full AI-generated output

**Tip:** Use the "Clear My Execution History" button in **Settings** to reset your logs.
        """)
    
    st.markdown("### Historical Log of All AI Execution Results")
    
    outputs = st.session_state.db.get_all_agent_outputs()
    
    if not outputs:
        st.info("No agent outputs found yet. Kick off a Crew to generate logs!")
    else:
        # Metrics
        total_runs = len(outputs)
        total_tokens = sum((o.get('tokens_used') or 0) for o in outputs)
        est_cost = (total_tokens / 1000) * 0.005
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Executions", total_runs)
        c2.metric("Total Tokens Used", f"{total_tokens:,}")
        c3.metric("Estimated API Cost", f"${est_cost:.4f}")
        
        st.markdown("---")
        
        for out in outputs:
            status = out.get('status') or 'Unknown'
            icon = "✅" if status == 'Success' else "❌"
            time_taken = out.get('execution_time') or 0
            tokens = out.get('tokens_used') or 0
            cost = (tokens / 1000) * 0.005
            
            with st.expander(f"{icon} [{out['timestamp']}] {out['crew_name']} ({time_taken}s)"):
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                col_m1.markdown(f"**Status:** {status}")
                col_m2.markdown(f"**Duration:** {time_taken}s")
                col_m3.markdown(f"**Tokens:** {tokens:,}")
                col_m4.markdown(f"**Cost:** ${cost:.5f}")
                
                meta = out.get('metadata')
                if meta:
                    st.caption(f"*Metadata: {meta}*")
                
                st.markdown("---")
                st.markdown(out['output'])

elif app_mode == "Settings":
    st.title("Platform Settings")
    
    with st.expander("📖 How To Use This Page", expanded=False):
        st.markdown("""
**Settings** is where you configure your account and API connections.

**API Vault:**
- **OpenAI API Key** – Required to run any crew. Get yours at [platform.openai.com](https://platform.openai.com/api-keys)
  1. Create an OpenAI account
  2. Go to API Keys → Create new secret key
  3. Copy and paste it here → Click "Save API Key"
  4. Your key is stored securely in your personal database vault (not shared with other users)

**Email Integration:**
- To let agents send real emails, set these in your `.env` file:
  - `AGENT_GMAIL_ADDRESS=your_email@gmail.com`
  - `AGENT_GMAIL_APP_PASSWORD=your_app_password`
- You need a Gmail App Password (not your regular password). Google: "Gmail App Password" for instructions.

**Data Management:**
- "Clear My Execution History" permanently deletes all your past crew logs.

**Logout:**
- Click the Logout button to return to the login screen. Your data is safe and will be here when you log back in.
        """)
    
    st.markdown(f"**Logged in as:** `{st.session_state.username}`")
    
    if st.button("🚪 Logout", type="primary"):
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()

    st.markdown("---")
    st.markdown("### API Vault")
    st.markdown("Configure your strictly isolated AI API keys here.")
    
    current_key = st.session_state.db.get_api_key() or ""
    api_key_input = st.text_input("OpenAI API Key (Required)", type="password", value=current_key)
    if st.button("Save API Key"):
        st.session_state.db.update_api_key(api_key_input)
        st.success("API Key encrypted and saved securely to your workspace.")
        
    st.markdown("---")
    st.subheader("Email Integration")
    gmail_address = os.environ.get('AGENT_GMAIL_ADDRESS', '')
    gmail_pass = os.environ.get('AGENT_GMAIL_APP_PASSWORD', '')
    if gmail_address and gmail_pass:
        st.success(f"✅ Default Workspace Gmail Configured: {gmail_address}")
    else:
        st.warning("⚠️ No global Workspace Gmail configured.")
        
    st.markdown("---")
    st.subheader("Data Management")
    if st.button("Clear My Execution History (Danger)"):
        with st.session_state.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM agent_outputs WHERE user_id = ?", (st.session_state.db.user_id,))
            conn.commit()
        st.success("Your Execution History was cleared.")
        st.rerun()


# 🤖 Morshed Squad — AI Agent Automation Platform

A **no-code enterprise AI automation platform** built on top of [CrewAI](https://github.com/crewai-io/crewai). Create AI agents, assign them tasks, and execute autonomous crews — all from a beautiful web dashboard. No coding required.

## 🚀 Features
- 🔐 **Multi-User Authentication**: Login/Signup with per-user data isolation
- 🤖 **Agent Builder**: Create AI agents with custom roles, goals, backstories, and tools
- 📋 **Task Manager**: Define tasks with detailed descriptions and assign them to agents
- 🚀 **Crew Orchestration**: Assemble agents + tasks into crews and execute with one click
- 🏗️ **Visual Flowchart**: Live Mermaid.js architecture diagram shows agent-task connections
- ⏸️ **Human-in-the-Loop**: Agents pause for human approval before sensitive actions (emails, posts)
- 🧠 **Persistent Memory**: Agents remember information across sessions via Memory Store/Recall
- 📊 **Execution History**: Full audit trail with token usage, duration, and API cost tracking
- 🔑 **Per-User API Vault**: Securely store OpenAI keys per user (not in .env files)
- 🛠️ **20 Agent Tools**: Web Search, Email, File Reader, CSV Search, PDF Search, Code Interpreter, and more

## 📦 Quick Start
1. Clone the repo: `git clone https://github.com/rayatcarnelian/morshed-squad.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run morshed_squad_ui/app.py`

## 🔒 Security
- Passwords are hashed before storage (SHA-256)
- API keys are stored per-user in the database, never in `.env`
- All data is tenant-isolated via `user_id` on every table
- Sensitive actions (email, social posts) require human approval

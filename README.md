# 🤖 Morshed Squad — AI Agent Automation Platform

A **no-code enterprise AI automation platform** built on top of [CrewAI](https://github.com/crewai-io/crewai). Create AI agents, assign them tasks, and execute autonomous crews — all from a beautiful web dashboard. No coding required.

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 🔐 **Multi-User Authentication** | Login/Signup with per-user data isolation |
| 🤖 **Agent Builder** | Create AI agents with custom roles, goals, backstories, and tools |
| 📋 **Task Manager** | Define tasks with detailed descriptions and assign them to agents |
| 🚀 **Crew Orchestration** | Assemble agents + tasks into crews and execute with one click |
| 🏗️ **Visual Flowchart** | Live Mermaid.js architecture diagram shows agent-task connections |
| ⏸️ **Human-in-the-Loop** | Agents pause for human approval before sensitive actions (emails, posts) |
| 🧠 **Persistent Memory** | Agents remember information across sessions via Memory Store/Recall |
| 📊 **Execution History** | Full audit trail with token usage, duration, and API cost tracking |
| 🔑 **Per-User API Vault** | Securely store OpenAI keys per user (not in .env files) |
| 🛠️ **20 Agent Tools** | Web Search, Email, File Reader, CSV Search, PDF Search, Code Interpreter, and more |

---

## 📦 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/rayatcarnelian/morshed-squad.git
cd morshed-squad
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run morshed_squad_ui/app.py
```

### 4. Login
- **Default Account:** `admin` / `admin123`
- Or click "Sign Up" to create a new account

### 5. Set your API Key
- Go to **Settings** → paste your **OpenAI API Key** → click **Save API Key**
- Get a key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

---

## 🏢 5-Agent Business Blueprint

The app comes with a ready-to-copy blueprint for running 90% of a business autonomously:

| Agent | Role | Tools |
|-------|------|-------|
| CEO - Strategy Director | Market analysis & growth planning | Web Search, Memory Store |
| CMO - Marketing Director | Content strategy & ad campaigns | Web Search, Social Content |
| Sales Manager | Outreach templates & lead scoring | Email, Memory Store |
| Operations Manager | SOPs, workflows & KPI dashboards | Memory Store |
| Customer Success Lead | Onboarding & churn prevention | Email, Memory Recall |

Open the **Agents** tab → click **📖 How To Use This Page** → copy the blueprint!

---

## 🛠️ Available Agent Tools

### Custom Tools (Built for Morshed Squad)
- 🔍 **Web Search** — Real-time internet search
- 📧 **Email** — Send emails via Gmail (triggers human approval)
- 📱 **Social Content Drafter** — Draft social posts (triggers human approval)
- 💾 **Memory Store** — Save info across sessions
- 🧠 **Memory Recall** — Retrieve saved memories

### Official CrewAI Tools (Auto-Detected)
- 📄 File Reader, ✏️ File Writer, 📁 Directory Reader
- 🌐 Website Scraper, 📊 CSV Search, 📋 JSON Search
- 📕 PDF Search, 📝 TXT Search, 🗂️ XML Search
- 💻 Code Interpreter, 🖼️ DALL-E Image Generator
- 🎥 YouTube Video/Channel Search, 🐙 GitHub Search
- 🔎 Serper Google Search (requires SERPER_API_KEY)

---

## 🏗️ Architecture

```
morshed_squad_ui/
├── app.py                    # Main Streamlit application (770 lines)
├── style.css                 # Custom dark/light mode styling
lib/
├── morshed_squad/
│   └── database/
│       └── database_manager.py   # Multi-tenant SQLite database
└── morshed_squad_tools/
    └── tools/
        ├── web_search_tool.py     # Wikipedia-based search
        ├── email_tool.py          # Gmail sender with HITL
        ├── social_content_tool.py # Social post drafter with HITL
        └── memory_tool.py         # Persistent key-value memory
```

---

## 🔒 Security

- Passwords are hashed before storage (SHA-256)
- API keys are stored per-user in the database, never in `.env`
- All data is tenant-isolated via `user_id` on every table
- Sensitive actions (email, social posts) require human approval

---

## 📄 License

Built with ❤️ by the Morshed Squad team. Powered by [CrewAI](https://github.com/crewai-io/crewai).

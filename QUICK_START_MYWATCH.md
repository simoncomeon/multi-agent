# Quick Start: Build MyWatch React App in 5 Minutes

## 1. Launch Multi-Agent System

```bash
cd /home/simon/Workspace/llm-project/python_tryout/multi-agent

# Option A: Guided mode (recommended)
python3 smart_launcher.py guided

# Option B: Full development team
python3 smart_launcher.py ai-development
```

## 2. Connect to Coordinator

```bash
# In a new terminal
python3 bin/multi_agent_terminal.py coordinator main
```

## 3. Set Up Workspace

In the coordinator terminal:
```
set_workspace ~/mywatch
workspace
```

## 4. Create MyWatch App

Execute these commands in the coordinator:

```
delegate "create ReactJS project structure for MyWatch app with src and public folders" to file_manager

delegate "create package.json for React MyWatch app with react, react-dom, vite as dependencies" to file_manager

delegate "create public/index.html with title MyWatch" to file_manager

delegate "create React component in src/App.jsx that displays current time and date, updates every second with useState and useEffect" to coder

delegate "create src/main.jsx that imports React, ReactDOM and renders App component" to coder

delegate "create src/App.css with centered layout, large fonts, and modern styling for the time display" to coder

delegate "create vite.config.js for React project" to file_manager

delegate "review the MyWatch React application" to code_reviewer

delegate "initialize git repository" to git_manager

delegate "commit all files with message 'Initial MyWatch React application'" to git_manager
```

## 5. Check Progress

```
tasks
agents
stats
```

## 6. Install and Run

```bash
cd ~/mywatch
npm install
npm run dev
```

## 7. Open Browser

Navigate to: `http://localhost:5173`

---

## Alternative: One-Line Multi-Step Workflow

```
delegate "create complete ReactJS MyWatch application that displays time and date with modern styling, includes git setup and documentation"
```

The coordinator will automatically create a multi-step workflow and delegate to multiple agents!

---

## Quick Commands Reference

| Command | Purpose |
|---------|---------|
| `delegate "task" to agent` | Direct delegation |
| `delegate "task"` | AI chooses agent |
| `agents` | View agent status |
| `tasks` | View task status |
| `workspace` | View workspace info |
| `workflows` | View workflows |
| `stats` | View statistics |

---

## Troubleshooting

**No agents running?**
```bash
python3 smart_launcher.py ai-development
```

**Tasks not processing?**
```
agents  # Check if target agent is active
```

**Need to restart?**
```bash
python3 cleanup_agents.py  # Clean up old agents
python3 smart_launcher.py ai-development
```

---

**For detailed guide, see: REACTJS_MYWATCH_GUIDE.md**

# Step-by-Step Guide: Building ReactJS MyWatch App with Multi-Agent System

## Overview
This guide will walk you through creating a ReactJS application called "MyWatch" that displays the current time and date using the multi-agent AI system. The agents will collaborate to build, review, and manage your project.

---

## Prerequisites

1. **Python 3.8+** installed
2. **Node.js and npm** installed (for React development)
3. **Git** installed
4. **Ollama** running with llama3.2 model
5. Multi-agent system repository cloned and set up

---

## Part 1: Launch the Multi-Agent System

### Step 1: Navigate to the Project Directory

```bash
cd /home/simon/Workspace/llm-project/python_tryout/multi-agent
```

### Step 2: Start the Smart Launcher in Guided Mode

```bash
python3 smart_launcher.py guided
```

This will launch the coordinator agent in a new terminal window with an interactive interface.

**Alternative - Manual Launch:**
If guided mode doesn't work, manually start the coordinator:

```bash
python3 bin/multi_agent_terminal.py coordinator main
```

---

## Part 2: Initialize Your Project with the Coordinator

### Step 3: Connect to the Coordinator

If not already connected, open a terminal and run:

```bash
python3 bin/multi_agent_terminal.py coordinator main
```

You should see the coordinator interface with a prompt.

### Step 4: Set Up Your Workspace

In the coordinator terminal, set your workspace directory:

```
set_workspace /home/simon/Workspace/projects/mywatch
```

Or use any directory where you want to create the project:

```
set_workspace ~/mywatch
```

The coordinator will create the directory if it doesn't exist.

### Step 5: Verify Workspace Setup

Check your workspace information:

```
workspace
```

This will show:
- Current workspace directory
- Directory status (exists/created)
- Communication system status

---

## Part 3: Launch Required Agents

### Step 6: Check Available Agents

View currently active agents:

```
agents
```

### Step 7: Launch Specialized Agents

Open new terminals and start the agents you'll need:

**Terminal 2 - File Manager:**
```bash
python3 bin/multi_agent_terminal.py file_manager fm
```

**Terminal 3 - Code Generator:**
```bash
python3 bin/multi_agent_terminal.py coder dev
```

**Terminal 4 - Code Reviewer:**
```bash
python3 bin/multi_agent_terminal.py code_reviewer reviewer
```

**Terminal 5 - Git Manager:**
```bash
python3 bin/multi_agent_terminal.py git_manager git
```

**Alternative - Launch All at Once:**
```bash
python3 smart_launcher.py ai-development
```

This launches a full development team including coordinator, coder, file_manager, code_reviewer, and git_manager.

---

## Part 4: Create the ReactJS MyWatch Application

### Step 8: Initialize React Project Structure

In the **coordinator terminal**, delegate the project setup:

```
delegate "create a ReactJS project structure for an app called MyWatch" to file_manager
```

The file manager will:
- Create project directories (src, public, etc.)
- Set up basic folder structure
- Create configuration files

### Step 9: Generate React Components

Delegate the component creation to the coder:

```
delegate "create a React component that displays current time and date, update every second" to coder
```

The coder will generate:
- Main App.jsx component
- Time/Date display logic
- Styling files
- Proper React hooks usage

### Step 10: Create Additional Project Files

**Create package.json:**
```
delegate "create package.json for ReactJS MyWatch app with react, react-dom, and vite" to file_manager
```

**Create index.html:**
```
delegate "create public/index.html for React app with title MyWatch" to file_manager
```

**Create main entry file:**
```
delegate "create src/main.jsx that renders the App component" to coder
```

---

## Part 5: Review and Refine the Code

### Step 11: Review Code Quality

```
delegate "review the MyWatch React application code for best practices and potential issues" to code_reviewer
```

The code reviewer will analyze:
- Code quality
- React best practices
- Performance issues
- Security concerns

### Step 12: Check Task Status

Monitor task progress:

```
tasks
```

This shows:
- Pending tasks
- In-progress tasks
- Completed tasks
- Failed tasks (if any)

---

## Part 6: Version Control Setup

### Step 13: Initialize Git Repository

```
delegate "initialize git repository" to git_manager
```

### Step 14: Commit Initial Project

```
delegate "commit all files with message 'Initial MyWatch React app setup'" to git_manager
```

The git manager will:
- Stage all files automatically
- Generate or use the provided commit message
- Create the commit

### Step 15: Check Git Status

```
delegate "show git status" to git_manager
```

---

## Part 7: Test and Run the Application

### Step 16: Install Dependencies

Switch to your workspace directory and install npm packages:

```bash
cd /home/simon/Workspace/projects/mywatch
npm install
```

### Step 17: Run the Development Server

```bash
npm run dev
```

The Vite development server will start, typically at `http://localhost:5173`

### Step 18: View Your Application

Open your browser and navigate to the provided URL (usually `http://localhost:5173`)

You should see your MyWatch application displaying the current time and date!

---

## Part 8: Make Improvements (Optional)

### Step 19: Add Styling

```
delegate "add CSS styling to MyWatch component with modern design, centered layout, and large readable fonts" to coder
```

### Step 20: Add Features

```
delegate "add 12-hour and 24-hour time format toggle to MyWatch component" to coder
```

### Step 21: Review Changes

```
delegate "review the new MyWatch styling and features" to code_reviewer
```

### Step 22: Commit Updates

```
delegate "commit changes with message 'Add styling and time format toggle'" to git_manager
```

---

## Part 9: Monitor and Manage

### Step 23: View Delegation Statistics

In the coordinator terminal:

```
stats
```

This shows:
- Total delegations
- Success rate
- Active workflows
- Recent delegations

### Step 24: Check Active Workflows

```
workflows
```

View any multi-step workflows in progress.

---

## Troubleshooting

### Issue: Agents Not Responding

**Check agent status:**
```
agents
```

**Restart inactive agents:**
If an agent shows as inactive, restart it in a new terminal.

### Issue: Tasks Not Being Processed

**View task queue:**
```
tasks
```

**Check if target agent is active:**
Make sure the agent you're delegating to is running.

### Issue: Workspace Not Found

**Verify workspace:**
```
workspace
```

**Reset workspace:**
```
set_workspace /path/to/your/project
```

### Issue: Ollama Connection Problems

**Check Ollama status:**
```bash
ollama list
```

**Start Ollama if needed:**
```bash
ollama serve
```

### Issue: Git Operations Failing

**Check if in git repository:**
```bash
cd /path/to/workspace
git status
```

**Re-initialize if needed:**
```
delegate "initialize git repository" to git_manager
```

---

## Coordination Commands Reference

### Essential Commands

| Command | Description |
|---------|-------------|
| `delegate "task" to agent` | Assign task to specific agent |
| `delegate "task"` | Let AI choose best agent |
| `agents` | Show all agent status |
| `tasks` | Show all task status |
| `workspace` | Show workspace info |
| `set_workspace <path>` | Set workspace directory |
| `workflows` | Show active workflows |
| `stats` | Show delegation statistics |
| `help` | Show available commands |
| `exit` or `quit` | Exit coordinator |

### Agent Names

- `coordinator` - Main orchestrator
- `file_manager` - File and project operations
- `coder` - Code generation
- `code_reviewer` - Code review and analysis
- `code_rewriter` - Code fixes and refactoring
- `git_manager` - Version control
- `tester` - Testing operations
- `researcher` - Research and documentation

---

## Expected Project Structure

After following this guide, your MyWatch project should have:

```
mywatch/
├── .git/                      # Git repository
├── public/
│   └── index.html            # HTML template
├── src/
│   ├── App.jsx               # Main React component
│   ├── App.css               # Styling
│   └── main.jsx              # Entry point
├── package.json              # Dependencies
├── vite.config.js            # Vite configuration
└── README.md                 # Project documentation
```

---

## Example Session Flow

Here's a complete example of commands you might use:

```bash
# 1. Start coordinator
python3 smart_launcher.py guided

# 2. In coordinator terminal:
set_workspace ~/mywatch
workspace

# 3. Start other agents (or use smart_launcher.py ai-development)

# 4. Create project:
delegate "create ReactJS project structure for MyWatch app" to file_manager
delegate "create React component displaying time and date with live updates" to coder
delegate "create package.json for React with vite" to file_manager
delegate "create src/main.jsx entry point" to coder

# 5. Review and version control:
delegate "review MyWatch code" to code_reviewer
delegate "initialize git repository" to git_manager
delegate "commit with message 'Initial MyWatch React application'" to git_manager

# 6. Check progress:
tasks
agents
stats

# 7. Install and run:
exit  # Exit coordinator
cd ~/mywatch
npm install
npm run dev
```

---

## Advanced Features

### Multi-Step Workflows

For complex tasks, the coordinator can create multi-step workflows automatically:

```
delegate "create complete ReactJS MyWatch app with styling, testing, and documentation"
```

The coordinator will analyze and create a workflow with multiple agents working in sequence.

### AI-Powered Agent Selection

Let the AI choose the best agent:

```
delegate "add timezone selection feature"
```

The coordinator's AI will analyze the task and delegate to the most appropriate agent.

### Status Monitoring

Use the monitoring script for live updates:

```bash
# In a separate terminal
python3 agent_status.py --live 3
```

This provides real-time updates on agent status every 3 seconds.

---

## Tips for Success

1. **Keep coordinator running** - It's the central hub for all operations
2. **Use specific descriptions** - Clear task descriptions get better results
3. **Monitor task status** - Check `tasks` regularly to see progress
4. **Let agents work** - Some operations take time, especially with AI generation
5. **Review before committing** - Always review code before version control
6. **Save your session** - Take notes of successful delegation patterns
7. **Start simple** - Begin with basic features, then add complexity
8. **Use workflows** - For complex projects, let coordinator create multi-step workflows

---

## Next Steps

After successfully creating MyWatch, you can:

1. **Add more features**: Timer, stopwatch, world clocks
2. **Improve styling**: Animations, themes, responsive design
3. **Add testing**: Unit tests with Jest
4. **Deploy**: Build and deploy to hosting service
5. **Document**: Create comprehensive README
6. **Optimize**: Performance improvements and code splitting

---

## Conclusion

You've now learned how to use the multi-agent system to create a ReactJS application from scratch. The agents handle project setup, code generation, review, and version control, allowing you to focus on defining requirements and coordinating the workflow.

The same pattern can be applied to any development project - just delegate tasks to the appropriate agents and let them collaborate!

**Happy coding with your AI development team!**

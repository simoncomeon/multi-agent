# Automated Multi-Agent Launcher Guide

## ✨ **Yes! Full automation is available with multiple options**

### **Quick Start - React.js Development**

```bash
# Option 1: Use preset workflow (RECOMMENDED)
python3 smart_launcher.py react-development

# Option 2: Use bash launcher with preset
./launch_agents.sh --react-dev

# Option 3: Custom agent selection
./launch_agents.sh coordinator:main file_manager:files coder:dev code_reviewer:reviewer code_rewriter:fixer git_manager:git
```

## **Available Launchers**

### 1. **Smart Launcher** (Python) - `smart_launcher.py`
**RECOMMENDED - Most flexible and reliable**

```bash
# List available workflows
python3 smart_launcher.py --list

# Launch preset workflow in new terminals
python3 smart_launcher.py react-development

# Launch preset workflow in background
python3 smart_launcher.py react-development --bg

# Launch custom agents
python3 smart_launcher.py --custom coordinator:main coder:dev code_reviewer:reviewer
```

### 2. **Bash Launcher** - `launch_agents.sh`
**Good for terminal emulator compatibility**

```bash
# Show usage and presets
./launch_agents.sh

# Launch React development team
./launch_agents.sh --react-dev

# Launch full team
./launch_agents.sh --full-team

# Launch code review team  
./launch_agents.sh --code-review

# Launch custom configuration
./launch_agents.sh coordinator:main file_manager:files coder:dev
```

### 3. **Tmux Launcher** - `launch_agents_tmux.sh`  
**Best for session management**

```bash
# Create tmux session with agents
./launch_agents_tmux.sh coordinator:main file_manager:files coder:dev

# Attach to running session
tmux attach -t multi-agent-session

# List tmux windows
tmux list-windows -t multi-agent-session
```

## **Preset Workflows Available**

### **React Development** (`react-development`)
Perfect for your React.js time display app:
- **coordinator:main** - Orchestrates all tasks
- **file_manager:files** - Creates project structure  
- **coder:dev** - Implements React components
- **code_reviewer:reviewer** - Reviews code quality
- **code_rewriter:fixer** - Fixes any issues
- **git_manager:git** - Handles version control

### **Code Review** (`code-review`)
For code quality focus:
- **coordinator:main** - Task coordination
- **code_reviewer:reviewer** - Code analysis
- **code_rewriter:fixer** - Issue fixing

### **Full Development** (`full-development`)  
Complete team with research capabilities:
- All react-development agents PLUS
- **researcher:research** - Information gathering

### **Minimal** (`minimal`)
Lightweight setup:
- **coordinator:main** - Basic coordination
- **coder:dev** - Core development

## **Complete React.js Workflow**

### **Step 1: Launch All Agents**
```bash
# Choose your preferred launcher:
python3 smart_launcher.py react-development
# OR
./launch_agents.sh --react-dev
```

### **Step 2: Execute in Coordinator Terminal**
```bash
# All commands in coordinator terminal:
delegate "Create React.js TimeDisplayApp project structure with components for time, date, week display" to file_manager

delegate "Initialize git repository for TimeDisplayApp" to git_manager  

delegate "Create React TimeDisplay component with real-time updates" to coder

delegate "Create timeUtils.js with date/time utility functions" to coder

delegate "Review all TimeDisplayApp code for quality and issues" to code_reviewer

delegate "Fix all issues found in TimeDisplayApp code reviews" to code_rewriter

delegate "Create final git commits and tag release" to git_manager
```

## 🎛**Configuration Customization**

### **Add New Workflow**
Edit `agent_workflows.json`:
```json
{
  "workflows": {
    "my-custom-workflow": {
      "description": "My custom development workflow",
      "agents": [
        {"role": "coordinator", "name": "main"},
        {"role": "coder", "name": "dev"},
        {"role": "file_manager", "name": "files"}
      ]
    }
  }
}
```

### **Terminal Compatibility**
Launchers automatically detect and use:
- gnome-terminal
- xterm  
- konsole
- terminator
- alacritty
- kitty

## 🧹 **Cleanup Integration**

```bash
# Clean before starting
./multi-agent clean

# Launch agents
python3 smart_launcher.py react-development

# Work with agents...

# Clean when done
./multi-agent cleanup
```

## **Your React.js App - Complete Commands**

### **One Command Launch:**
```bash
python3 smart_launcher.py react-development
```

### **Coordinator Delegate Commands:**
```bash
delegate "Create React.js TimeDisplayApp with time/date/week components" to file_manager
delegate "Create React components for real-time time display" to coder  
delegate "Review and validate TimeDisplayApp code quality" to code_reviewer
delegate "Fix all compilation and quality issues" to code_rewriter
delegate "Setup git repository and version control" to git_manager
```

---

## **Benefits of Automated Launch**

- **One command** starts all required agents
- **Separate terminals** for each agent (easy to monitor)
- **Preset workflows** for common development tasks
- **Custom configurations** for specific needs
- **🧹 Integrated cleanup** for fresh starts
- **Status monitoring** with `./multi-agent status`

**Your multi-agent system is now fully automated! Just run one command and start delegating tasks.** ✨
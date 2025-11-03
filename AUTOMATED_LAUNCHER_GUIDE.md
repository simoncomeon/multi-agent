# Automated Multi-Agent Launcher Guide with Project_Process Paradigm

## TARGET: **Project_Process-Focused AI Collaboration**

### **Quick Start - AI-Powered Universal Development**

```bash
# Option 1: Use preset workflow with Project_Process (RECOMMENDED)
python3 smart_launcher.py ai-development

# Option 2: Use bash launcher with Project_Process preset
./launch_agents.sh --ai-dev

# Option 3: Custom agent selection for focused project work
./launch_agents.sh coordinator:main file_manager:files coder:dev code_reviewer:reviewer code_rewriter:fixer git_manager:git

# Then set project focus in coordinator terminal:
set_project MyTimeDisplayApp    # Focus on specific project
project                        # Check current project status
files                          # View loaded files for AI context
```

## **Available Launchers**

### 1. **Smart Launcher** (Python) - `smart_launcher.py`
**RECOMMENDED - Most flexible and reliable**

```bash
# List available workflows
python3 smart_launcher.py --list

# Launch preset workflow in new terminals
python3 smart_launcher.py ai-development

# Launch preset workflow in background
python3 smart_launcher.py ai-development --bg

# Launch custom agents
python3 smart_launcher.py --custom coordinator:main coder:dev code_reviewer:reviewer
```

### 2. **Bash Launcher** - `launch_agents.sh`
**Good for terminal emulator compatibility**

```bash
# Show usage and presets
./launch_agents.sh

# Launch AI-powered development team  
./launch_agents.sh --ai-dev

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

### **AI-Powered Development** (`ai-development`) - **Universal Framework Support with Project_Process**
Perfect for AI-collaborative development in any framework (React, Vue, Python, Node.js, Java, etc.):
- **coordinator:main** - Orchestrates Project_Process workflows with AI context
- **file_manager:files** - AI-powered project creation using complete context
- **coder:dev** - AI-generated components with project awareness
- **code_reviewer:reviewer** - AI analysis of entire project structure
- **code_rewriter:fixer** - AI-driven fixes using full project context
- **git_manager:git** - Context-aware version control operations

**Key Features:**
- All agents share complete project file context
- AI model receives full project contents as input
- No hardcoded solutions - pure AI collaboration
- Context-aware intelligent suggestions

### **Code Review** (`code-review`)
For code quality focus:
- **coordinator:main** - Task coordination
- **code_reviewer:reviewer** - Code analysis
- **code_rewriter:fixer** - Issue fixing

### **Full Development** (`full-development`)  
Complete team with research capabilities:
- All ai-development agents PLUS
- **researcher:research** - Information gathering

### **Minimal** (`minimal`)
Lightweight setup:
- **coordinator:main** - Basic coordination
- **coder:dev** - Core development

## **Complete AI-Collaborative Universal Project_Process Workflow**

### **Step 1: Launch All Agents with Project_Process Focus**
```bash
# Choose your preferred launcher:
python3 smart_launcher.py ai-development
# OR
./launch_agents.sh --ai-dev
```

### **Step 2: Set Project_Process Focus**
```bash
# In coordinator terminal - establish Project_Process:
project                                    # Check current project status
set_project TimeDisplayApp                # Focus on specific project
files                                     # View loaded project files for AI
```

### **Step 3: AI-Collaborative Development Commands**
```bash
# All commands use AI model with complete project context:

# AI-powered project creation with full context awareness (any framework)
delegate "Create TimeDisplayApp using AI analysis - detect best framework (React/Vue/Python/etc.) and implement with time, date, week components" to file_manager

# Initialize version control with project understanding  
delegate "Initialize git repository for TimeDisplayApp project" to git_manager

# AI-generated components using full project context (framework-aware)
delegate "Use AI to create intelligent TimeDisplay component with real-time updates, analyzing project structure and framework" to coder

# AI-powered utility creation with framework awareness
delegate "Generate utility files using AI analysis of component requirements and project architecture (adapt to detected framework)" to coder

# AI-driven comprehensive code review using full project context
delegate "Perform AI-powered code review of entire TimeDisplayApp project for quality, performance, and framework best practices" to code_reviewer

# AI-collaborative issue fixing using complete project understanding
delegate "Use AI collaboration to fix all issues found in TimeDisplayApp, considering framework conventions and dependencies" to code_rewriter

# Intelligent version control with project awareness
delegate "Create intelligent git commits and releases using AI analysis of project changes and framework structure" to git_manager
```

### **Step 4: Monitor AI Collaboration**
```bash
# Check AI collaboration status:
project                                   # Current project and loaded files
files                                     # Project context available to AI
agents                                    # Active agents working on project
tasks                                     # Current AI collaboration tasks
```

## CONTROLS:**Configuration Customization**

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

##  **Cleanup Integration**

```bash
# Clean before starting
./multi-agent clean

# Launch agents
python3 smart_launcher.py react-development

# Work with agents...

# Clean when done
./multi-agent cleanup
```

## **Your Universal App - Complete Commands (Any Framework)**

### **One Command Launch:**
```bash
python3 smart_launcher.py ai-development
```

### **Coordinator Delegate Commands:**
```bash
delegate "Create TimeDisplayApp using best-fit framework (React/Vue/Python/etc.) with time/date/week components" to file_manager
delegate "Create framework-appropriate components for real-time time display" to coder
delegate "Review and validate TimeDisplayApp code quality and framework best practices" to code_reviewer
delegate "Fix all compilation, framework-specific, and quality issues" to code_rewriter
delegate "Setup git repository and version control" to git_manager
```

---

## **Benefits of Automated Launch**

- **One command** starts all required agents
- **Separate terminals** for each agent (easy to monitor)
- **Preset workflows** for common development tasks
- **Custom configurations** for specific needs
- ** Integrated cleanup** for fresh starts
- **Status monitoring** with `./multi-agent status`

**Your multi-agent system is now fully automated! Just run one command and start delegating tasks.** FEATURE:
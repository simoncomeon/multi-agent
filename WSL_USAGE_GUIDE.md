# WSL: WSL Multi-Agent System - Complete Guide

## **Perfect! Your Agents Are Running Successfully**

Your output shows all 6 agents launched correctly:
- coordinator (main) - PID: 65949
- file_manager (files) - PID: 65952 
- coder (dev) - PID: 65955
- code_reviewer (reviewer) - PID: 65958
- code_rewriter (fixer) - PID: 65961
- git_manager (git) - PID: 65964

## **WSL-Optimized Workflow for React.js App**

### **Step 1: Launch Agents (DONE)**
```bash
python3 wsl_launcher.py react-dev
```

### **Step 2: Connect to Coordinator**
```bash
# Option 1: Use connection helper
./connect_coordinator.sh

# Option 2: Direct connection
python3 bin/multi_agent_terminal.py coordinator main
```

### **Step 3: Delegate Tasks for Your React.js Time Display App**

Once connected to the coordinator terminal, run these commands:

```bash
# Create project structure
delegate "Create React.js TimeDisplayApp project with components for displaying current time, date, and ISO week number. Include proper folder structure with src/components/, package.json, and all necessary React.js files" to file_manager

# Initialize version control
delegate "Initialize git repository for TimeDisplayApp project, create appropriate .gitignore for React.js" to git_manager

# Create main time display component
delegate "Create TimeDisplay.jsx component that shows current time (HH:MM:SS), current date (YYYY-MM-DD), and ISO week number with real-time updates using React hooks (useState, useEffect). Update every second and include proper cleanup" to coder

# Create utility functions
delegate "Create timeUtils.js with functions: getCurrentTime(), getCurrentDate(), getWeekNumber() using proper ISO week calculation. Include JSDoc documentation and error handling" to coder

# Create main App component
delegate "Create App.jsx that imports and renders TimeDisplay component with modern CSS styling, responsive design for mobile and desktop, and proper error boundaries" to coder

# Create package.json with dependencies
delegate "Create package.json for React.js project with dependencies: react, react-dom, date-fns for date calculations, react-scripts for build tools. Include proper scripts for start, build, test" to coder

# Review all code for quality
delegate "Review all TimeDisplayApp components and files for React.js best practices, code quality, performance, accessibility, and potential issues. Generate comprehensive review reports" to code_reviewer

# Fix any issues found
delegate "Fix all issues found in code reviews for TimeDisplayApp, ensure all components compile correctly, handle any syntax or logic errors" to code_rewriter

# Final git commits
delegate "Create structured git commits for TimeDisplayApp development, add all files, create meaningful commit messages, tag release v1.0.0" to git_manager
```

## **WSL-Specific Commands**

### **Agent Management**
```bash
# Launch agents
python3 wsl_launcher.py react-dev # Full React team
python3 wsl_launcher.py code-review # Code review team 
python3 wsl_launcher.py minimal # Basic setup

# Check status
python3 wsl_launcher.py status
./multi-agent status

# Enhanced agent management (in coordinator terminal)
agents                    # List all agents with PID and status
status file_manager      # Detailed health check of specific agent
kill faulty_agent        # Terminate problematic agent
restart coder            # Kill and respawn agent (fault recovery)
spawn researcher info    # Create new specialized agent
cleanup                  # Remove inactive agents from registry

# Clean up
python3 wsl_launcher.py clean
./multi-agent clean
```

### **Connection Options**
```bash
# Connect to coordinator (recommended)
./connect_coordinator.sh

# Connect to specific agent
python3 bin/multi_agent_terminal.py <role> <name>
python3 bin/multi_agent_terminal.py coder dev
python3 bin/multi_agent_terminal.py code_reviewer reviewer
```

### **Alternative Launchers**
```bash
# WSL-specific launcher
./launch_agents_wsl.sh --react-dev

# Background mode
./launch_agents_wsl.sh --background coordinator:main file_manager:files coder:dev

# Smart launcher with WSL detection
python3 smart_launcher.py react-development --bg
```

## **Your React.js App - Expected Results**

After running all delegate commands, you should have:

```
TimeDisplayApp/
├── public/
│ └── index.html
├── src/
│ ├── components/
│ │ └── TimeDisplay.jsx
│ ├── utils/
│ │ └── timeUtils.js
│ ├── App.jsx
│ ├── App.css
│ └── index.js
├── package.json
├── .gitignore
└── README.md
```

### **Key Features**
- Real-time clock (updates every second)
- DATE: Current date display
- ISO week number calculation 
- Responsive design (mobile + desktop)
- FEATURE: Modern React hooks (useState, useEffect)
- Proper cleanup and error handling
- Git version control with structured commits

## **Troubleshooting WSL**

### **Enhanced WSL Troubleshooting with Agent Management**

### **If agents don't register:**
```bash
# Check agent health
./connect_coordinator.sh
agents                   # Check all agent status with PIDs
status coordinator       # Detailed coordinator health

# If agent is stuck
restart file_manager    # Kill and respawn specific agent
cleanup                 # Remove inactive entries
```

### **If coordinator connection fails:**
```bash
# Check coordinator status  
status coordinator      # In any agent terminal
kill coordinator        # If stuck
spawn coordinator main  # Recreate coordinator

# Or restart entire system
./multi-agent clean
python3 wsl_launcher.py react-dev
```

### **Agent Recovery Strategies:**
```bash
# For faulty file manager
kill files
spawn file_manager new_files

# For stuck code reviewer  
restart reviewer
status reviewer         # Verify recovery

# Complete system health check
agents                  # List all with process status
cleanup                 # Remove zombies
```

### **For better terminal experience:**
1. Install Windows Terminal from Microsoft Store
2. Use `./launch_agents_wsl.sh --react-dev` for separate terminals
3. Or continue with background mode + connection script

## **WSL Pro Tips**

- **Background mode works perfectly** - agents communicate via files
- **Use connection helper** - `./connect_coordinator.sh` for easy access
- **Check PIDs** - All your agents are running (visible in process list)
- **File-based communication** - Agents use `.agent_comm/` directory
- **No GUI needed** - Perfect for WSL environment

## **You're All Set!**

Your WSL multi-agent system is working perfectly! Just connect to the coordinator and start delegating tasks for your React.js time display application. The agents will handle all the implementation details automatically.

**Next step:** Run `./connect_coordinator.sh` and start delegating! 
# Multi-Agent AI Terminal System

A sophisticated multi-agent coordination system where specialized AI agents collaborate to solve complex problems through intelligent task delegation and real-time communication.

## Directory Structure

```
multi-agent/
├── multi-agent              # Main entry script
├── bin/                     # Executable scripts
│   ├── launch.sh           # Agent launcher
│   ├── multi_agent_terminal.py  # Core agent implementation
│   └── launch_agents.sh    # Legacy launcher
├── workspace/              # Working directory for agents
│   ├── .agent_comm/       # Inter-agent communication files
│   │   ├── agents.json    # Active agent registry
│   │   ├── tasks.json     # Shared task queue
│   │   └── messages.json  # Inter-agent messages
│   └── [your project files]
├── examples/               # Demo scripts and examples
│   └── demo_multi_agents.py
└── docs/                   # Documentation
    └── README.md
```

## -- Quick Start

### 1. Start the Multi-Agent System

```bash
cd multi-agent

# Start coordinator agent (main orchestrator)
./multi-agent start coordinator main_coord

# In separate terminals, start specialized agents:
./multi-agent start coder dev_agent
./multi-agent start code_reviewer quality_agent
./multi-agent start code_rewriter fixer_agent
./multi-agent start file_manager file_agent  
./multi-agent start git_manager git_agent
./multi-agent start researcher research_agent
```

### 2. Basic Commands

```bash
# Check system status
./multi-agent status

# Run demonstration
./multi-agent demo

# Enter workspace
./multi-agent workspace

# Clean communication files
./multi-agent clean
```

## Agent Roles

| Role | Specialization | Key Capabilities |
|------|----------------|------------------|
| **Coordinator** | Task orchestration | Project management, workflow coordination |
| **Coder** | Code analysis & generation | Bug detection, code review, programming |
| **Code Reviewer** | Quality assurance | Error detection, optimization, validation, architectural review |
| **Code Rewriter** | Automated code fixing | Fixes issues found by code reviewer, applies improvements |
| **File Manager** | File operations | File creation, organization, structure |
| **Git Manager** | Version control | Commits, branching, repository management |
| **Researcher** | Information gathering | Documentation, best practices, analysis |

## -- Example Workflows

### Project Creation Workflow
```bash
# In coordinator terminal:
delegate 'create Python web app structure' to file_manager
delegate 'analyze requirements and generate main.py' to coder  
delegate 'research Flask best practices' to researcher
delegate 'initialize git repository' to git_manager
```

### Code Review Workflow
```bash
# In coordinator terminal:
delegate 'analyze app.py for security issues' to coder
delegate 'review app.py for errors and improvements' to code_reviewer
delegate 'fix issues found in code review' to code_rewriter
delegate 'create comprehensive README' to file_manager
delegate 'commit reviewed changes' to git_manager
```

### Automated Quality Assurance Pipeline
```bash
# Complete automated code improvement cycle:
delegate 'review entire project for code quality' to code_reviewer
delegate 'apply all fixes from review automatically' to code_rewriter
delegate 'test fixed code and validate functionality' to coder
delegate 'commit improvements with detailed message' to git_manager
```

## Agent Commands

### Universal Commands (all agents)
- `help` - Show agent-specific help
- `agents` - List all active agents with process status
- `tasks` - Show task queue status  
- `delegate <description> to <role>` - Assign task to specialist
- `ollama <prompt>` - Query AI directly
- `exit` - Shutdown agent

### Agent Lifecycle Management Commands
- `status <agent_name>` - Detailed health check and status of specific agent
- `kill <agent_name>` - Terminate and remove faulty agent from system
- `restart <agent_name>` - Kill and respawn agent with same role (fault recovery)
- `spawn <role> <name>` - Create new specialized agent with custom name
- `cleanup` - Remove all inactive agents from registry
- `project` - Show current project process focus and files loaded
- `set_project <name>` - Set focus to specific project for AI context
- `files` - View project files loaded for AI collaboration

### Specialized Commands

#### Coordinator Agent
- `coordinate <project>` - Orchestrate multi-step project

#### Coder Agent  
- `analyze <file>` - Deep code analysis
- `review <file>` - Code review

#### Code Reviewer Agent
- `review <file>` - Comprehensive file review for errors and improvements
- `optimize <project_path>` - Optimize project performance and quality
- `validate <project_path>` - Validate project completeness and runnability
- `helicopter <project_path>` - High-level architectural review

#### Code Rewriter Agent
- `fix <file>` - Apply fixes based on code reviewer recommendations
- `rewrite <file> <improvements>` - Rewrite file with specific improvements
- `apply_review <review_file>` - Apply all fixes from a review report

#### File Manager Agent
- `create <file> <description>` - AI-powered file creation
- `organize` - Organize workspace structure

#### Git Manager Agent
- `commit <message>` - Git commit with message
- `status` - Git repository status

## -- Advanced Features

### Enhanced File Manager - Smart Project Intelligence

The file manager now includes advanced project intelligence:

**Auto-Project Location**
```bash
# File manager automatically finds existing projects
delegate "Create TimeComponent" to file_manager
# → Locates "TimeDisplayApp" project automatically
# → Creates: workspace/TimeDisplayApp/src/TimeComponent.jsx
# → NO MORE "UnknownProject" creation!
```

**Project Structure Analysis**
- **React Projects**: Detects package.json, src/, components/ structure
- **Python Projects**: Identifies setup.py, requirements.txt, src/ layout  
- **Java Projects**: Recognizes pom.xml, Maven/Gradle structure
- **Vue Projects**: Finds Vue config, components, assets directories
- **Node.js Projects**: Detects Express, API, routes patterns

**Intelligent Component Creation**
- Analyzes existing project to match coding style
- Places files in appropriate directories based on framework
- Integrates with existing architecture seamlessly
- Uses project context for AI-generated code

### Production-Grade Agent Management

**Health Monitoring & Fault Recovery**
```bash
# Monitor system health
agents                    # List all agents with PID and status
status file_manager       # Detailed health check
   # Output: ID, Role, Status, PID, Process State, Pending Tasks

# Handle faulty agents  
kill problematic_agent    # Terminate faulty agent
restart coder            # Kill and respawn with same role
spawn tester qa_new      # Create specialized agent

# System maintenance
cleanup                  # Remove inactive/zombie agents
```

**Dynamic Agent Scaling**
```bash
# Scale up for complex projects
spawn code_reviewer frontend_reviewer
spawn code_reviewer backend_reviewer  
spawn coder react_specialist
spawn coder python_specialist

# Scale down when complete
kill frontend_reviewer
kill react_specialist
```

**Process Management Features**
- **PID Tracking**: Each agent's process ID monitored
- **Health Verification**: Real-time process status checking
- **Graceful Shutdown**: SIGTERM for clean termination
- **Registry Cleanup**: Automatic removal of orphaned entries
- **Zero-Downtime Recovery**: Restart agents without affecting others

### Inter-Agent Communication

```
Agent Communication Flow:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Coordinator │───▶│    Coder    │───▶│Code Reviewer│
│   (Main)    │    │ (Analysis)  │    │ (Quality)   │
└─────────────┘    └─────────────┘    └─────────────┘
       │                                      │
       │           ┌─────────────┐           ▼
       └──────────▶│File Manager │    ┌─────────────┐
                   │ (Creation)  │    │Code Rewriter│
                   └─────────────┘    │  (Fixer)    │
                          │           └─────────────┘
                          │                  │
                   ┌─────────────┐           │
                   │Git Manager  │◀──────────┘
                   │ (Version)   │
                   └─────────────┘
                          │
                   ┌─────────────┐
                   │ Researcher  │
                   │(Information)│
                   └─────────────┘
```

- **JSON-based messaging**: Agents communicate via structured JSON files
- **Real-time task queue**: Background monitoring of pending tasks
- **Status synchronization**: Shared awareness of system state
- **Result propagation**: Agents build on each other's work
- **Automated Fix Pipeline**: Code Reviewer → Code Rewriter → Git Manager workflow
- **Review-Fix Coordination**: Code Rewriter automatically processes Code Reviewer outputs
- **Multi-file Intelligence**: Code Rewriter can locate and fix issues across project files

### Task Management
- **Priority-based scheduling**: Important tasks processed first
- **Automatic retry**: Failed tasks can be retried automatically  
- **Progress tracking**: Real-time status updates
- **Result storage**: Task outcomes stored for reference
- **Review-Fix Chaining**: Code Rewriter automatically processes Code Reviewer outputs
- **Cross-file Intelligence**: Code Rewriter can find and fix issues across multiple files
- **Iterative Improvement**: Multiple review-fix cycles until code quality standards met

### Workspace Management
- **Isolated workspace**: All agent work happens in dedicated directory
- **Shared context**: Agents aware of workspace changes
- **Communication logs**: Full audit trail of agent interactions
- **Clean separation**: System files separate from work files

## -- Configuration

### Environment Variables
```bash
export OLLAMA_CMD="ollama"           # Ollama command
export DEFAULT_MODEL="llama3.2"     # Default AI model
export WORKSPACE_DIR="./workspace"   # Working directory
```

### Customization
- Edit `bin/multi_agent_terminal.py` to add new agent roles
- Modify task types in the `execute_task()` method
- Extend communication protocols in `AgentCommunication` class

## -- System Monitoring

```bash
# Check active agents
./multi-agent status

# View communication files directly
cat workspace/.agent_comm/agents.json
cat workspace/.agent_comm/tasks.json  
cat workspace/.agent_comm/messages.json
```

## -- Troubleshooting

### Common Issues

1. **Agent not responding**
   ```bash
   status agent_name        # Check detailed agent health
   restart agent_name       # Kill and respawn agent
   ./multi-agent clean     # Clear communication files
   ./multi-agent status    # Check system status
   ```

2. **Tasks not executing**
   - Check agent health: `status file_manager`
   - Verify agent is running: `agents` (shows PID and process status)
   - Restart problematic agent: `restart coder`
   - Check task queue: `tasks`

3. **File Manager creating "UnknownProject"**
   - Set project focus first: `set_project MyProject`
   - Use specific project names in delegate commands
   - Check existing projects: `project`
   - Enhanced file manager now auto-locates existing projects

4. **Agent process stuck or zombie**
   ```bash
   kill stuck_agent         # Force terminate
   cleanup                  # Remove inactive agents  
   spawn role new_name      # Create replacement
   ```

5. **Communication errors**
   - Ensure workspace directory has write permissions
   - Check `.agent_comm/` directory exists
   - Verify JSON files are not corrupted
   - Use `cleanup` to remove corrupted entries

6. **Project context not loading**
   ```bash
   set_project ProjectName  # Set explicit focus
   files                    # Verify files loaded
   project                  # Check current project status
   ```

### Agent Recovery Strategies

**Complete Agent Reset**
```bash
# For severely corrupted agent
kill problem_agent
cleanup
spawn agent_role new_name
```

**System Health Check**  
```bash
# Regular maintenance routine
agents                    # Check all agent status
cleanup                   # Remove inactive agents
./multi-agent status     # Overall system health
```

**Project Focus Issues**
```bash
# If agents lose project context
set_project MyProject    # Refocus all agents
files                    # Verify project files loaded
delegate "status check" to file_manager  # Test functionality
```

## -- Development

### Adding New Agent Roles
1. Add role to `AgentRole` enum in `multi_agent_terminal.py`
2. Implement specialized methods in `MultiAgentTerminal` class
3. Add role-specific commands in `process_command()` method
4. Update help documentation

### Extending Task Types
1. Add new task type in `execute_task()` method
2. Create corresponding handler method
3. Update task delegation logic
4. Add to agent specialization mapping

## -- License

This multi-agent system is open source and available for modification and extension.

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality  
4. Submit pull request with detailed description

---

**Ready to coordinate AI agents?** Run `./multi-agent demo` to see the system in action!
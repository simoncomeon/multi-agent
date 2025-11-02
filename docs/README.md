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
- `agents` - List all active agents
- `tasks` - Show task queue status  
- `delegate <description> to <role>` - Assign task to specialist
- `ollama <prompt>` - Query AI directly
- `exit` - Shutdown agent

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
   ./multi-agent clean  # Clear communication files
   ./multi-agent status # Check agent status
   ```

2. **Tasks not executing**
   - Check agent is active: `./multi-agent status`
   - Verify task queue: `cat workspace/.agent_comm/tasks.json`
   - Restart specific agent role

3. **Communication errors**
   - Ensure workspace directory has write permissions
   - Check `.agent_comm/` directory exists
   - Verify JSON files are not corrupted

4. **Code Rewriter not processing reviews**
   - Verify Code Reviewer has completed task: `./multi-agent status`
   - Check Code Rewriter agent is active and registered
   - Ensure review output format is compatible with Code Rewriter input

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
# Multi-Agent AI Terminal System with Project_Process Paradigm

A sophisticated multi-agent coordination system where specialized AI agents collaborate on focused **Project_Process** workflows using complete project context for intelligent AI-powered development.

## 🎯 Project_Process Paradigm

- **Single Project Focus**: All agents work on ONE Project_Process at a time
- **Complete Project Context**: AI model receives full project file contents as input
- **True AI Collaboration**: No hardcoded solutions - all generation through AI model
- **Context-Aware Intelligence**: Agents understand entire project structure
- **Collaborative Workflows**: Agents share project knowledge for better results

## ✨ Features

- **7 Specialized Agent Roles**: Coordinator, Coder, Code Reviewer, Code Rewriter, File Manager, Git Manager, Researcher
- **Project_Process Management**: Focus on one project with complete context loading
- **AI-Powered Generation**: All code/content generated through AI model with project context
- **Real-time Communication**: JSON-based inter-agent messaging with project awareness
- **Cross-platform**: Native Linux/macOS support with WSL optimization
- **Automated Launchers**: Multiple startup methods for different environments

## 🚀 Quick Start

```bash
# Start the system with Project_Process focus
./launch_agents.sh

# Set Project_Process focus (in coordinator terminal)
project                    # Check current project
set_project TimeDisplayApp # Focus on specific project
files                      # View loaded project files

# Or use automated launcher with preset workflows
python3 smart_launcher.py react-development

# Check system status
./multi-agent status
```

## Agent Roles

| Role | Specialization |
|------|----------------|
| **Coordinator** | Project orchestration and workflow management |
| **Coder** | Code generation and analysis |
| **Code Reviewer** | Quality assurance and error detection |
| **Code Rewriter** | Automated code fixing based on reviews |
| **File Manager** | Universal project creation and file operations |
| **Git Manager** | Version control operations |
| **Researcher** | Information gathering and best practices |

## 🤖 AI-Powered Project_Process Creation

The File Manager agent uses AI collaboration with project context for intelligent creation:

```bash
# Set project focus first
set_project MyReactApp

# AI-powered creation with full context awareness
delegate 'create React.js todo app with time tracking components' to file_manager
delegate 'add Flask API server to existing React project' to file_manager
delegate 'enhance Vue.js dashboard with real-time data' to file_manager
```

**AI Collaboration Features:**
- Complete project context provided to AI model
- Context-aware component generation
- Intelligent file structure decisions
- No hardcoded templates - pure AI creativity

**Project Process Commands:**
- `project` - Show current project status
- `set_project <name>` - Focus on specific project
- `files` - View loaded project files for AI context

## Documentation

- **General Usage**: `docs/README.md`
- **WSL Setup**: `WSL_USAGE_GUIDE.md`
- **Automated Launchers**: `AUTOMATED_LAUNCHER_GUIDE.md`

## System Requirements

- Python 3.8+
- [Ollama](https://ollama.ai/) with llama3.2 model
- Git (for version control features)
- For WSL: Windows Terminal recommended

## License

Open source - modify and extend as needed.
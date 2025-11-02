# Multi-Agent AI Terminal System

A sophisticated multi-agent coordination system where specialized AI agents collaborate to solve complex problems through intelligent task delegation and real-time communication.

## Features

- **7 Specialized Agent Roles**: Coordinator, Coder, Code Reviewer, Code Rewriter, File Manager, Git Manager, Researcher
- **Universal Project Creation**: Supports 14+ project types (React.js, Vue.js, Angular, Flask, Django, etc.)
- **Real-time Communication**: JSON-based inter-agent messaging
- **Cross-platform**: Native Linux/macOS support with WSL optimization
- **Automated Launchers**: Multiple startup methods for different environments

## Quick Start

```bash
# Start the system
./launch_agents.sh

# Or use WSL-optimized launcher
./launch_agents_wsl.sh

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

## Universal Project Creation

The File Manager agent can intelligently create projects of any type:

```bash
delegate 'create a React.js todo app' to file_manager
delegate 'create a Flask API server' to file_manager
delegate 'create a Vue.js dashboard' to file_manager
```

Supported project types: React.js, React Native, Vue.js, Angular, Next.js, Flask, Django, FastAPI, Node.js, Python, JavaScript, Web, API, Generic

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
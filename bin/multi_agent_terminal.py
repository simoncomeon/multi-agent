#!/usr/bin/env python3
"""
Enhanced Multi-Agent Terminal System with Collaborative Approach
Focuses on intelligent guidance rather than hardcoded solutions
"""

import os
import sys
import json
import uuid
import threading
import time
import readline
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional
import subprocess

# Import our Ollama client
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from src.core.ollama_client import ollama_client

# === Enhanced Terminal Colors ===
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BRIGHT_YELLOW = '\033[93;1m'
    BRIGHT_GREEN = '\033[92;1m'
    BRIGHT_RED = '\033[91;1m'
    BRIGHT_CYAN = '\033[96;1m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def colored_print(text: str, color: str = Colors.WHITE):
    """Print colored text"""
    print(f"{color}{text}{Colors.ENDC}")

def colored_text(text, color):
    """Return colored text without printing"""
    return f"{color}{text}{Colors.ENDC}"

# === Enhanced Agent System ===
class AgentRole(Enum):
    COORDINATOR = "coordinator"
    CODER = "coder"
    CODE_REVIEWER = "code_reviewer"
    CODE_REWRITER = "code_rewriter"
    FILE_MANAGER = "file_manager"
    GIT_MANAGER = "git_manager"
    RESEARCHER = "researcher"
    TESTER = "tester"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    id: str
    type: str
    description: str
    assigned_to: str
    created_by: str
    status: TaskStatus
    priority: int
    data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class AgentMessage:
    id: str
    from_agent: str
    to_agent: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime

class AgentCommunication:
    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        self.comm_dir = self.workspace_dir / ".agent_comm"
        self.comm_dir.mkdir(exist_ok=True)
        
        # Communication files
        self.tasks_file = self.comm_dir / "tasks.json"
        self.messages_file = self.comm_dir / "messages.json"
        self.agents_file = self.comm_dir / "agents.json"
        
        # Initialize files if they don't exist
        for file_path in [self.tasks_file, self.messages_file, self.agents_file]:
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    def register_agent(self, agent_id: str, role: AgentRole, status: str = "active"):
        """Register an agent in the system"""
        agents = self.load_agents()
        
        # Update or add agent
        agent_info = {
            "id": agent_id,
            "role": role.value,
            "status": status,
            "last_seen": datetime.now().isoformat(),
            "pid": os.getpid()
        }
        
        # Remove existing entry if any
        agents = [a for a in agents if a["id"] != agent_id]
        agents.append(agent_info)
        
        self.save_agents(agents)
        colored_print(f"Agent {agent_id} ({role.value}) registered", Colors.GREEN)
    
    def load_agents(self) -> List[Dict]:
        try:
            with open(self.agents_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def save_agents(self, agents: List[Dict]):
        with open(self.agents_file, 'w') as f:
            json.dump(agents, f, indent=2)
    
    def get_active_agents(self) -> List[Dict]:
        """Get list of active agents"""
        agents = self.load_agents()
        return [agent for agent in agents if agent.get("status") == "active"]
    
    def unregister_agent(self, agent_id: str):
        """Unregister/deactivate an agent"""
        agents = self.load_agents()
        
        for agent in agents:
            if agent["id"] == agent_id:
                agent["status"] = "inactive"
                agent["deactivated_at"] = datetime.now().isoformat()
                break
        
        self.save_agents(agents)
        colored_print(f"Agent {agent_id} unregistered/deactivated", Colors.YELLOW)
    
    def remove_agent(self, agent_id: str):
        """Completely remove an agent from the system"""
        agents = self.load_agents()
        agents = [a for a in agents if a["id"] != agent_id]
        self.save_agents(agents)
        colored_print(f"Agent {agent_id} completely removed", Colors.RED)
    
    def get_agent_status(self, agent_id: str) -> Dict:
        """Get status of a specific agent"""
        agents = self.load_agents()
        for agent in agents:
            if agent["id"] == agent_id:
                return agent
        return None
    
    def kill_agent_by_pid(self, agent_id: str) -> bool:
        """Kill agent process by PID"""
        import signal
        
        agent_info = self.get_agent_status(agent_id)
        if not agent_info:
            return False
        
        pid = agent_info.get("pid")
        if not pid:
            return False
        
        try:
            os.kill(pid, signal.SIGTERM)
            colored_print(f"Sent SIGTERM to agent {agent_id} (PID: {pid})", Colors.YELLOW)
            return True
        except ProcessLookupError:
            colored_print(f"Process {pid} for agent {agent_id} not found", Colors.YELLOW)
            return False
        except PermissionError:
            colored_print(f"Permission denied to kill process {pid}", Colors.RED)
            return False
    
    def load_tasks(self) -> List[Dict]:
        try:
            with open(self.tasks_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def save_tasks(self, tasks: List[Dict]):
        with open(self.tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
    
    def create_task(self, task_type: str, description: str, assigned_to: str, 
                   created_by: str, priority: int = 1, data: Dict = None) -> str:
        """Create a new task"""
        task_id = str(uuid.uuid4())[:8]
        task = Task(
            id=task_id,
            type=task_type,
            description=description,
            assigned_to=assigned_to,
            created_by=created_by,
            status=TaskStatus.PENDING,
            priority=priority,
            data=data or {},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        tasks = self.load_tasks()
        # Convert task to JSON-serializable dict
        task_dict = {
            "id": task.id,
            "type": task.type,
            "description": task.description,
            "assigned_to": task.assigned_to,
            "created_by": task.created_by,
            "status": task.status.value,
            "priority": task.priority,
            "data": task.data,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat()
        }
        tasks.append(task_dict)
        self.save_tasks(tasks)
        
        colored_print(f"-- Task created: {task_id} -> {assigned_to}", Colors.BRIGHT_YELLOW)
        return task_id
    
    def update_task_status(self, task_id: str, status: TaskStatus, result: Dict = None):
        """Update task status"""
        tasks = self.load_tasks()
        for task in tasks:
            if task["id"] == task_id:
                task["status"] = status.value
                task["updated_at"] = datetime.now().isoformat()
                if result:
                    task["result"] = result
                break
        self.save_tasks(tasks)
    
    def get_pending_tasks(self, agent_id: str) -> List[Dict]:
        """Get pending tasks for an agent"""
        tasks = self.load_tasks()
        
        # Get agent's role to match against role-based assignments
        agents = self.get_active_agents()
        agent_role = None
        for agent in agents:
            if agent["id"] == agent_id:
                agent_role = agent["role"]
                break
        
        # Return tasks assigned to this agent ID OR to this agent's role
        pending = []
        for task in tasks:
            if task["status"] == "pending":
                assigned_to = task["assigned_to"]
                if assigned_to == agent_id or (agent_role and assigned_to == agent_role):
                    pending.append(task)
        
        # Only show debug info when there are actual tasks or errors
        if pending and len(pending) > 0:
            print(f" Found {len(pending)} pending tasks for {agent_id} ({agent_role})")
            for task in pending:
                print(f" Task {task['id']}: {task['description']}")
        
        return pending

class MultiAgentTerminal:
    def __init__(self, agent_id: str, role: AgentRole):
        self.agent_id = agent_id
        self.role = role
        # Fix workspace directory to point to the correct location
        current_dir = os.getcwd()
        if current_dir.endswith('/bin'):
            self.workspace_dir = os.path.join(os.path.dirname(current_dir), 'workspace')
        else:
            self.workspace_dir = os.path.join(current_dir, 'workspace')
        
        # Ensure workspace directory exists
        os.makedirs(self.workspace_dir, exist_ok=True)
        self.comm = AgentCommunication(self.workspace_dir)
        
        # Project Process Management - NEW PARADIGM
        self.current_project_process = None
        self.project_process_workspace = None
        self.project_process_files = {}  # Cache of project files for AI input
        
        # AI Configuration
        self.ollama_cmd = "ollama"
        self.default_model = "llama3.2"
        self.history_file = str(Path.home() / f".agent_history_{agent_id}")
        
        # Register this agent
        self.comm.register_agent(agent_id, role)
        colored_print(f"Agent {agent_id} initialized with role: {role.value}", Colors.BRIGHT_GREEN)
        
        # Load command history and check for active project process
        self.load_history()
        self.detect_active_project_process()
        
        # Start task monitoring
        self.running = True
        self.task_thread = threading.Thread(target=self.monitor_tasks, daemon=True)
        self.task_thread.start()
        
        # Check if this is a coordinator starting in guided mode
        self.guided_mode = self.check_guided_mode()
    
    def load_history(self):
        """Load command history"""
        try:
            readline.read_history_file(self.history_file)
        except FileNotFoundError:
            pass
    
    def save_history(self):
        """Save command history"""
        try:
            readline.write_history_file(self.history_file)
        except:
            pass
            
    def check_guided_mode(self):
        """Check if this coordinator should start in guided mode (only coordinator active)"""
        if self.role != AgentRole.COORDINATOR:
            return False
            
        # Always start in guided mode for coordinator agents
        # This provides a better user experience for new users
        return True
        
    def show_guided_welcome(self):
        """Show guided welcome message for new users"""
        print()
        colored_print("=" * 60, Colors.BRIGHT_YELLOW)
        colored_print("  🤖 AI DEVELOPMENT ASSISTANT - WELCOME! 🤖", Colors.BRIGHT_GREEN)
        colored_print("=" * 60, Colors.BRIGHT_YELLOW)
        print()
        colored_print("Hi! I'm your AI Development Coordinator.", Colors.BRIGHT_CYAN)
        colored_print("I'll help you build amazing projects with AI assistance.", Colors.CYAN)
        print()
        colored_print("What would you like to do today?", Colors.WHITE)
        print()
        colored_print("OPTIONS:", Colors.BRIGHT_YELLOW)
        colored_print("1. 'create project' - Start a new development project", Colors.GREEN)
        colored_print("2. 'work on <project>' - Resume work on an existing project", Colors.GREEN) 
        colored_print("3. 'spawn team' - Create a full AI development team", Colors.GREEN)
        colored_print("4. 'help' - See all available commands", Colors.GREEN)
        print()
        colored_print("EXAMPLES:", Colors.BRIGHT_YELLOW)
        colored_print("• 'create project' → I'll ask what you want to build", Colors.CYAN)
        colored_print("• 'create react app' → Quick React project creation", Colors.CYAN)
        colored_print("• 'create python project' → Quick Python project setup", Colors.CYAN)
        colored_print("• 'spawn team' → Launch coder, reviewer, file manager, etc.", Colors.CYAN)
        print()
        colored_print("Just type what you want to do in natural language!", Colors.BRIGHT_GREEN)
        print()
        
    def handle_guided_command(self, user_input):
        """Handle commands in guided mode with natural language processing"""
        input_lower = user_input.lower().strip()
        
        # PRIORITY 1: Delegation commands - check FIRST to avoid conflicts
        if input_lower.startswith('delegate ') and ' to ' in input_lower:
            return False  # Let main loop handle delegate commands normally
        
        # PRIORITY 2: Project creation commands
        elif any(phrase in input_lower for phrase in ['create project', 'new project', 'start project']):
            self.start_project_creation_flow()
            return True
        elif any(phrase in input_lower for phrase in ['create react', 'react app', 'react project']) and 'delegate' not in input_lower:
            self.quick_create_project('react', 'React Application')
            return True
        elif any(phrase in input_lower for phrase in ['create python', 'python project', 'python app']) and 'delegate' not in input_lower:
            self.quick_create_project('python', 'Python Application')
            return True
        elif any(phrase in input_lower for phrase in ['create vue', 'vue app', 'vue project']) and 'delegate' not in input_lower:
            self.quick_create_project('vue', 'Vue Application')
            return True
        elif any(phrase in input_lower for phrase in ['create node', 'node app', 'nodejs']) and 'delegate' not in input_lower:
            self.quick_create_project('nodejs', 'Node.js Application')
            return True
        
        # Team management commands
        elif any(phrase in input_lower for phrase in ['spawn team', 'create team', 'launch team', 'full team']):
            self.spawn_development_team()
            return True
        elif any(phrase in input_lower for phrase in ['spawn agents', 'create agents', 'launch agents']):
            self.spawn_development_team()
            return True
            
        # Project management commands
        elif input_lower.startswith('work on ') or input_lower.startswith('resume '):
            project_name = input_lower.replace('work on ', '').replace('resume ', '').strip()
            self.resume_project(project_name)
            return True
            
        return False  # Not a guided command, process normally
        
    def start_project_creation_flow(self):
        """Start interactive project creation flow"""
        print()
        colored_print("PROJECT CREATION WIZARD", Colors.BRIGHT_YELLOW)
        colored_print("=" * 30, Colors.YELLOW)
        print()
        
        try:
            # Get project name
            project_name = input(colored_text("What should we call your project? ", Colors.BRIGHT_CYAN)).strip()
            if not project_name:
                colored_print("ERROR: Project name is required!", Colors.RED)
                return
                
            # Get project type
            print()
            colored_print("What type of project would you like to create?", Colors.BRIGHT_CYAN)
            colored_print("1. React App (Frontend)", Colors.GREEN)
            colored_print("2. Vue App (Frontend)", Colors.GREEN)
            colored_print("3. Python Project (Backend/Scripts)", Colors.GREEN)
            colored_print("4. Node.js App (Backend)", Colors.GREEN)
            colored_print("5. Full-Stack (React + Python)", Colors.GREEN)
            colored_print("6. Custom/Other", Colors.GREEN)
            print()
            
            choice = input(colored_text("Enter your choice (1-6): ", Colors.BRIGHT_CYAN)).strip()
            
            project_types = {
                '1': ('react', 'React Application'),
                '2': ('vue', 'Vue Application'), 
                '3': ('python', 'Python Project'),
                '4': ('nodejs', 'Node.js Application'),
                '5': ('fullstack', 'Full-Stack Application'),
                '6': ('custom', 'Custom Project')
            }
            
            if choice in project_types:
                proj_type, proj_desc = project_types[choice]
                print()
                colored_print(f"Creating {proj_desc}: {project_name}", Colors.BRIGHT_GREEN)
                
                # Ask about AI team
                print()
                spawn_team = input(colored_text("Should I create a full AI development team for this project? (y/n): ", Colors.BRIGHT_CYAN)).strip().lower()
                
                # Create the project
                self.create_project_with_type(project_name, proj_type, proj_desc)
                
                if spawn_team in ['y', 'yes', 'true', '1']:
                    print()
                    colored_print("Spawning AI development team...", Colors.BRIGHT_YELLOW)
                    self.spawn_development_team()
                    
            else:
                colored_print("Invalid choice! Please try again.", Colors.RED)
                
        except KeyboardInterrupt:
            print()
            colored_print("Project creation cancelled.", Colors.YELLOW)
            
    def quick_create_project(self, project_type, description):
        """Quick project creation without wizard"""
        try:
            project_name = input(colored_text(f"Enter name for your {description}: ", Colors.BRIGHT_CYAN)).strip()
            if project_name:
                self.create_project_with_type(project_name, project_type, description)
                
                # Ask about team
                spawn_team = input(colored_text("Create AI development team? (y/n): ", Colors.BRIGHT_CYAN)).strip().lower()
                if spawn_team in ['y', 'yes']:
                    self.spawn_development_team()
            else:
                colored_print("Project name required!", Colors.RED)
        except KeyboardInterrupt:
            print()
            colored_print("Cancelled.", Colors.YELLOW)
            
    def create_project_with_type(self, project_name, project_type, description):
        """Create project and delegate to file manager"""
        print()
        colored_print(f"Creating {description}: {project_name}", Colors.BRIGHT_GREEN)
        
        # Check if file_manager exists, if not spawn it temporarily
        agents = self.comm.get_active_agents()
        file_manager_exists = any(agent['role'] == 'file_manager' for agent in agents)
        
        if not file_manager_exists:
            colored_print("Spawning file manager agent...", Colors.CYAN)
            self.spawn_single_agent('file_manager', 'files')
            # Give it a moment to register
            import time
            time.sleep(2)
        
        # Create task for file manager
        task_description = f"Create {project_type} project '{project_name}' - {description}"
        task_id = self.comm.create_task(
            task_type='project_creation',
            description=task_description,
            assigned_to='files',  # file manager agent
            created_by=self.agent_id,
            priority=1,
            data={'project_name': project_name, 'project_type': project_type, 'description': description}
        )
        
        colored_print(f"SUCCESS: Project creation task assigned to file manager (Task #{task_id})", Colors.BRIGHT_GREEN)
        colored_print(f"TIP: Use 'tasks' command to monitor progress", Colors.CYAN)
        
    def spawn_development_team(self):
        """Spawn a complete AI development team"""
        print()
        colored_print("SPAWNING AI DEVELOPMENT TEAM", Colors.BRIGHT_YELLOW)
        colored_print("=" * 35, Colors.YELLOW)
        
        agents_to_spawn = [
            ('file_manager', 'files', 'Project structure and file management'),
            ('coder', 'dev', 'Code writing and implementation'),  
            ('code_reviewer', 'reviewer', 'Code quality and review'),
            ('code_rewriter', 'fixer', 'Code optimization and fixes'),
            ('git_manager', 'git', 'Version control management')
        ]
        
        # Check which agents already exist
        existing_agents = {agent['role'] for agent in self.comm.get_active_agents()}
        
        spawned = 0
        for role, name, description in agents_to_spawn:
            if role not in existing_agents:
                colored_print(f"Spawning {description} agent ({name})...", Colors.CYAN)
                success = self.spawn_single_agent(role, name)
                if success:
                    spawned += 1
                    time.sleep(1)  # Prevent overwhelming the system
            else:
                colored_print(f"INFO: {role} agent already exists", Colors.YELLOW)
                
        print()
        if spawned > 0:
            colored_print(f"SUCCESS: Spawned {spawned} new agents!", Colors.BRIGHT_GREEN)
            colored_print("TIP: Use 'agents' command to see your full team", Colors.CYAN)
        else:
            colored_print("INFO: All agents already exist", Colors.CYAN)
            
    def spawn_single_agent(self, role, name):
        """Spawn a single agent in a new terminal"""
        try:
            import subprocess
            import sys
            import os
            
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            agent_script = os.path.join(script_dir, "bin", "multi_agent_terminal.py")
            
            # Detect system type for terminal launching
            system_type = self.detect_system()
            
            # Use terminal launch instead of background
            if system_type == "wsl":
                # WSL - launch in Windows Terminal
                terminals = [
                    ["wt.exe", "-w", "0", "new-tab", "--title", f"Agent: {role} ({name})", 
                     "bash", "-c", f"cd '{script_dir}' && python3 '{agent_script}' '{name}' '{role}'"],
                ]
                
                for terminal_cmd in terminals:
                    try:
                        subprocess.run(terminal_cmd, check=True, capture_output=True, text=True)
                        return True
                    except (FileNotFoundError, OSError):
                        continue
                        
            elif system_type == "linux":
                # Linux - try various terminal emulators
                terminals = [
                    ["gnome-terminal", "--", "bash", "-c", f"cd '{script_dir}' && python3 '{agent_script}' '{name}' '{role}'; exec bash"],
                    ["xterm", "-e", f"cd '{script_dir}' && python3 '{agent_script}' '{name}' '{role}'; exec bash"],
                    ["konsole", "-e", f"cd '{script_dir}' && python3 '{agent_script}' '{name}' '{role}'"],
                ]
                
                for terminal_cmd in terminals:
                    try:
                        subprocess.Popen(terminal_cmd, cwd=script_dir)
                        return True
                    except (FileNotFoundError, OSError):
                        continue
            
            # Fallback to background if no terminal available
            colored_print(f"WARNING: No terminal emulator found, launching {role} agent in background", Colors.YELLOW)
            subprocess.Popen([sys.executable, str(agent_script), name, role], 
                           cwd=script_dir)
            return True
            
        except Exception as e:
            colored_print(f"ERROR: Failed to spawn {role} agent: {e}", Colors.RED)
            return False
            
    def detect_system(self):
        """Detect the operating system type"""
        import platform
        
        if os.path.exists("/proc/version"):
            with open("/proc/version", "r") as f:
                if "microsoft" in f.read().lower():
                    return "wsl"
        
        system = platform.system().lower()
        if system == "linux":
            return "linux"
        elif system == "darwin":
            return "macos" 
        elif system == "windows":
            return "windows"
        else:
            return "linux"
            
    def resume_project(self, project_name):
        """Resume work on an existing project"""
        project_path = os.path.join(self.workspace_dir, project_name)
        if os.path.exists(project_path):
            self.set_project_process(project_name)
            colored_print(f"SUCCESS: Resumed work on project '{project_name}'", Colors.BRIGHT_GREEN)
            colored_print(f"FOLDER: {project_path}", Colors.CYAN)
        else:
            colored_print(f"ERROR: Project '{project_name}' not found", Colors.RED)
            colored_print("TIP: Use 'create project' to start a new one", Colors.CYAN)

    def detect_active_project_process(self):
        """Detect if there's an active project process in workspace"""
        try:
            workspace_items = os.listdir(self.workspace_dir)
            # Filter out system directories and only consider actual project directories
            system_dirs = {'.agent_comm', '__pycache__', '.git', '.vscode', 'node_modules'}
            project_dirs = []
            
            for item in workspace_items:
                if item not in system_dirs and os.path.isdir(os.path.join(self.workspace_dir, item)):
                    # Check if it looks like an active project (has common project files)
                    project_path = os.path.join(self.workspace_dir, item)
                    project_indicators = ['package.json', 'requirements.txt', 'Cargo.toml', 'pom.xml', 'go.mod', '.project', 'main.py', 'app.py', 'index.js', 'App.js']
                    
                    if any(os.path.exists(os.path.join(project_path, indicator)) for indicator in project_indicators):
                        project_dirs.append(item)
            
            if len(project_dirs) == 1:
                # Single active project - set as current
                self.set_project_process(project_dirs[0])
                colored_print(f"INFO: Detected active project: {project_dirs[0]}", Colors.CYAN)
            elif len(project_dirs) > 1:
                colored_print(f"WARNING: Multiple projects detected: {', '.join(project_dirs)}", Colors.YELLOW)
                colored_print(f"TIP: Use 'set_project <name>' to focus on one project process", Colors.CYAN)
            else:
                colored_print(f"FOLDER: No active project process detected", Colors.BLUE)
        except Exception as e:
            colored_print(f"Error detecting project process: {e}", Colors.RED)
    
    def set_project_process(self, project_name: str):
        """Set the current project process focus"""
        project_path = os.path.join(self.workspace_dir, project_name)
        
        if os.path.exists(project_path) and os.path.isdir(project_path):
            self.current_project_process = project_name
            self.project_process_workspace = project_path
            
            # Load project files for AI input
            self.load_project_files()
            
            colored_print(f"TARGET: Project Process Focus: {project_name}", Colors.BRIGHT_GREEN)
            colored_print(f"FOLDER: Workspace: {project_path}", Colors.GREEN)
        else:
            colored_print(f"ERROR: Project process '{project_name}' not found", Colors.RED)
    
    def load_project_files(self):
        """Load all project files content for AI model input"""
        if not self.project_process_workspace:
            return
        
        self.project_process_files = {}
        
        try:
            for root, dirs, files in os.walk(self.project_process_workspace):
                # Skip node_modules and other build directories
                dirs[:] = [d for d in dirs if d not in ['node_modules', 'build', 'dist', '.git']]
                
                for file in files:
                    if file.endswith(('.js', '.jsx', '.py', '.html', '.css', '.json', '.md')):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, self.project_process_workspace)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                self.project_process_files[relative_path] = {
                                    'path': file_path,
                                    'content': content,
                                    'size': len(content)
                                }
                        except Exception as e:
                            colored_print(f"WARNING: Could not read {relative_path}: {e}", Colors.YELLOW)
            
            file_count = len(self.project_process_files)
            colored_print(f"FILES: Loaded {file_count} project files for AI collaboration", Colors.CYAN)
            
        except Exception as e:
            colored_print(f"Error loading project files: {e}", Colors.RED)
    
    def get_project_context_for_ai(self) -> str:
        """Get formatted project context for AI model input"""
        if not self.current_project_process:
            return "No active project process"
        
        context = f"PROJECT PROCESS: {self.current_project_process}\n"
        context += f"WORKSPACE: {self.project_process_workspace}\n\n"
        context += "PROJECT FILES:\n"
        
        for relative_path, file_info in self.project_process_files.items():
            context += f"\n--- FILE: {relative_path} ---\n"
            context += file_info['content']
            context += f"\n--- END FILE: {relative_path} ---\n"
        
        return context
    
    def create_standardized_ai_input(self, operation_type: str, task_description: str = "", context_type: str = "GENERAL", **kwargs) -> Dict:
        """Create standardized input for AI model operations"""
        
        # Get project context
        project_context = self.get_project_context_for_ai()
        
        standardized_input = {
            "operation_metadata": {
                "type": operation_type,
                "context_type": context_type,
                "timestamp": datetime.now().isoformat(),
                "agent_id": self.agent_id,
                "project_process": self.current_project_process
            },
            "project_context": {
                "name": self.current_project_process,
                "workspace": self.project_process_workspace,
                "files": self.project_process_files,
                "file_count": len(self.project_process_files) if self.project_process_files else 0
            },
            "task_specification": {
                "description": task_description,
                "requirements": kwargs.get("requirements", []),
                "constraints": kwargs.get("constraints", []),
                "target_files": kwargs.get("target_files", []),
                "expected_output": kwargs.get("expected_output", "IMPLEMENTATION")
            },
            "full_context": project_context
        }
        
        return standardized_input
    
    def execute_standardized_ai_operation(self, standardized_input: Dict) -> Dict:
        """Execute AI operation with standardized input format"""
        
        operation_type = standardized_input["operation_metadata"]["type"]
        
        # Create standardized prompt
        prompt = self.build_standardized_prompt(standardized_input)
        
        # Execute AI operation
        ai_result = self.try_ai_implementation(prompt)
        
        # Add metadata to result
        if ai_result.get('status') == 'success':
            ai_result['operation_metadata'] = standardized_input["operation_metadata"]
            ai_result['processed_at'] = datetime.now().isoformat()
        
        return ai_result
    
    def build_standardized_prompt(self, standardized_input: Dict) -> str:
        """Build standardized prompt for AI model"""
        
        operation_type = standardized_input["operation_metadata"]["type"]
        task_desc = standardized_input["task_specification"]["description"]
        project_context = standardized_input["full_context"]
        
        base_prompt = f"""STANDARDIZED AI OPERATION
Operation Type: {operation_type}
Project Process: {standardized_input["project_context"]["name"]}

FULL PROJECT CONTEXT:
{project_context}

TASK SPECIFICATION:
{task_desc}

REQUIREMENTS:
{chr(10).join(f"- {req}" for req in standardized_input["task_specification"]["requirements"])}

CONSTRAINTS:
{chr(10).join(f"- {constraint}" for constraint in standardized_input["task_specification"]["constraints"])}

INSTRUCTIONS:
- Analyze the project context to understand existing structure and patterns
- Provide clean, executable code only
- No explanations, comments, or documentation unless specifically requested
- Use appropriate technology stack based on project analysis
- Return only working, runnable code
- Do not make assumptions about framework unless evident from project context

Expected Output Format: {standardized_input["task_specification"]["expected_output"]}
"""
        
        return base_prompt
    
    def process_standardized_ai_output(self, ai_result: Dict, operation_type: str) -> str:
        """Process standardized AI output based on operation type"""
        
        raw_output = ai_result.get('implementation', '')
        
        if operation_type == "TASK_ANALYSIS":
            return f"AI Analysis: {raw_output}"
        elif operation_type == "FILE_GENERATION":
            return raw_output
        elif operation_type == "CODE_ENHANCEMENT":
            return raw_output
        else:
            return raw_output
    
    def provide_fallback_guidance(self, description: str) -> str:
        """Provide fallback guidance when AI unavailable"""
        return f"""Universal Guidance for: {description}

1. Analyze existing project structure and patterns
2. Identify required files and components based on task
3. Choose appropriate implementation approach for current tech stack
4. Implement following project's established conventions
5. Test and validate the implementation

This task requires AI model collaboration for detailed implementation guidance."""
    
    def monitor_tasks(self):
        """Monitor for new tasks assigned to this agent"""
        last_check_time = 0
        
        while self.running:
            try:
                current_time = time.time()
                # Check every 5 seconds to reduce spam
                if current_time - last_check_time >= 5:
                    pending_tasks = self.comm.get_pending_tasks(self.agent_id)
                    
                    if pending_tasks:
                        colored_print(f"\n[{self.agent_id}] Processing {len(pending_tasks)} task(s)...", Colors.CYAN)
                        for task in pending_tasks:
                            self.handle_task(task)
                    
                    last_check_time = current_time
                
                time.sleep(1)
            except Exception as e:
                colored_print(f"Task monitoring error: {e}", Colors.RED)
                time.sleep(5)
    
    def handle_project_notification(self, task: Dict) -> Dict:
        """Handle project change notifications from file manager"""
        data = task.get('data', {})
        project_name = data.get('project_name')
        project_path = data.get('project_path')
        
        if project_name:
            # Set this project as current for this agent too
            self.set_project_process(project_name)
            colored_print(f"NOTIFY: Agent {self.agent_id} now focused on project '{project_name}'", Colors.BRIGHT_YELLOW)
        
        return {
            "type": "project_notification_received",
            "project_name": project_name,
            "agent_id": self.agent_id,
            "message": f"Agent {self.agent_id} updated to work on project '{project_name}'"
        }
    
    def handle_task(self, task: Dict):
        """Handle a task assigned to this agent"""
        task_id = task["id"]
        task_type = task.get("type", "")
        description = task["description"]
        
        colored_print(f"\n[{self.agent_id}] Handling task {task_id}: {description}", Colors.YELLOW)
        
        # Update task status to in_progress
        self.comm.update_task_status(task_id, TaskStatus.IN_PROGRESS)
        
        try:
            # Handle project notifications first (all agents can receive these)
            if task_type == 'project_notification':
                result = self.handle_project_notification(task)
            elif self.role == AgentRole.CODER:
                if "code" in task_type.lower() or "generate" in task_type.lower():
                    result = self.handle_code_generation_task(task)
                else:
                    result = self.handle_general_task(task)
            elif self.role == AgentRole.COORDINATOR:
                result = self.handle_coordination_task(task)
            elif self.role == AgentRole.CODE_REVIEWER:
                result = self.handle_code_review_task(task)
            elif self.role == AgentRole.FILE_MANAGER:
                result = self.handle_file_management_task(task)
            elif self.role == AgentRole.GIT_MANAGER:
                result = self.handle_git_management_task(task)
            elif self.role == AgentRole.RESEARCHER:
                result = self.handle_research_task(task)
            elif self.role == AgentRole.TESTER:
                result = self.handle_testing_task(task)
            elif self.role == AgentRole.CODE_REWRITER:
                result = self.handle_code_rewriter_task(task)
            else:
                result = self.handle_general_task(task)
            
            self.comm.update_task_status(task_id, TaskStatus.COMPLETED, result)
            colored_print(f"Task {task_id} completed successfully!", Colors.GREEN)
            
        except Exception as e:
            error_result = {"error": str(e), "type": "task_execution_error"}
            self.comm.update_task_status(task_id, TaskStatus.FAILED, error_result)
            colored_print(f"Task {task_id} failed: {e}", Colors.RED)
    
    def handle_code_generation_task(self, task: Dict) -> Dict:
        """Handle code generation using AI-first approach with collaborative fallback"""
        description = task["description"]
        
        # Try AI model first for actual implementation
        ai_result = self.try_ai_implementation(description)
        
        if ai_result.get('status') == 'success':
            colored_print(f"\n=== AI CODE GENERATION ===", Colors.BRIGHT_GREEN)
            colored_print(f"Generated code for: {description}", Colors.GREEN)
            colored_print(f"Model: {ai_result.get('model', 'unknown')}", Colors.CYAN)
            colored_print(f"================================\n", Colors.BRIGHT_GREEN)
            
            return {
                "type": "code_generation",
                "code": ai_result.get('implementation', ''),
                "model": ai_result.get('model', 'unknown'),
                "approach": "ai_generated",
                "message": f"Successfully generated code using {ai_result.get('model', 'AI model')}"
            }
        else:
            # Fallback to collaborative guidance if AI unavailable
            guidance = self.analyze_task_and_provide_guidance(description)
            
            colored_print(f"\n=== COLLABORATIVE ANALYSIS ===", Colors.BRIGHT_YELLOW)
            colored_print(guidance, Colors.CYAN)
            colored_print(f"================================\n", Colors.BRIGHT_YELLOW)
            
            return {
                "type": "collaborative_guidance",
                "guidance": guidance,
                "ai_implementation": ai_result,
                "approach": "collaborative",
                "message": "AI model not available. Providing collaborative guidance instead."
            }
    
    def analyze_task_and_provide_guidance(self, description: str) -> str:
        """Universal task analysis using AI collaboration with standardized input/output"""
        
        # Standardized AI Input
        standardized_input = self.create_standardized_ai_input(
            operation_type="TASK_ANALYSIS",
            task_description=description,
            context_type="PROJECT_ANALYSIS"
        )
        
        colored_print(f"   AGENT: Universal AI task analysis with standardized input", Colors.BRIGHT_CYAN)
        
        # Try AI analysis with standardized input
        ai_result = self.execute_standardized_ai_operation(standardized_input)
        
        if ai_result.get('status') == 'success':
            return self.process_standardized_ai_output(ai_result, "TASK_ANALYSIS")
        
        # Fallback to basic analysis if AI unavailable
        return self.provide_fallback_guidance(description)
        
        # Framework detection
        if "react" in desc_lower:
            analysis["framework"] = "React"
            analysis["suggested_approach"].append("Use functional components with hooks")
            analysis["suggested_approach"].append("Consider state management needs")
        elif "vue" in desc_lower:
            analysis["framework"] = "Vue"
            analysis["suggested_approach"].append("Use composition API for modern Vue development")
        elif "python" in desc_lower:
            analysis["framework"] = "Python"
            analysis["suggested_approach"].append("Follow PEP 8 style guidelines")
            analysis["suggested_approach"].append("Consider using type hints")
        elif "node" in desc_lower or "javascript" in desc_lower:
            analysis["framework"] = "Node.js/JavaScript"
            analysis["suggested_approach"].append("Use modern ES6+ features")
        
        # Component type detection
        if "time" in desc_lower or "clock" in desc_lower:
            analysis["component_type"] = "Time/Clock Display"
            analysis["features"] = ["real-time updates", "date formatting", "time formatting"]
            analysis["suggested_approach"].append("Implement timer with setInterval")
            analysis["suggested_approach"].append("Consider timezone handling")
        elif "todo" in desc_lower or "task" in desc_lower:
            analysis["component_type"] = "Task Management"
            analysis["features"] = ["add/remove items", "mark complete", "persistence"]
            analysis["suggested_approach"].append("Use local state or localStorage")
            analysis["suggested_approach"].append("Consider CRUD operations")
        elif "app" in desc_lower:
            analysis["component_type"] = "Application"
            analysis["features"] = ["user interface", "routing", "state management"]
            analysis["suggested_approach"].append("Plan component hierarchy")
            analysis["suggested_approach"].append("Consider data flow patterns")
        
        # Generate intelligent guidance
        guidance = f'''TASK ANALYSIS: {description}
{'=' * 60}

FRAMEWORK DETECTED: {analysis["framework"] or "Not specified - recommend clarifying"}
COMPONENT TYPE: {analysis["component_type"] or "Generic component"}
SUGGESTED FEATURES: {", ".join(analysis["features"]) if analysis["features"] else "Basic functionality"}

ARCHITECTURAL GUIDANCE:
{chr(10).join(f"• {approach}" for approach in analysis["suggested_approach"])}

IMPLEMENTATION STRATEGY:
This task requires collaborative development between AI model and human developer.

RECOMMENDED WORKFLOW:
1. AI Model: Generate initial implementation based on requirements
2. Human Developer: Review and customize for specific needs  
3. Collaborative Refinement: Iterate based on testing and feedback

TECHNICAL CONSIDERATIONS:
• Follow framework best practices and conventions
• Implement proper error handling and edge cases
• Consider accessibility and user experience
• Plan for testing and maintainability

COLLABORATION NOTES:
- This agent provides architectural guidance, not hardcoded solutions
- Work with AI model when available for actual code generation
- Encourage iterative development and testing
- Focus on learning and understanding, not just copying code'''
        
        return guidance
    
    def try_ai_implementation(self, description: str) -> Dict:
        """Try to get AI implementation if model is available"""
        try:
            # Check if Ollama is available (local or remote)
            if not ollama_client.is_available():
                return {"status": "unavailable", "message": "Ollama not available"}
            
            # Generate prompt for AI model
            prompt = f"""Create a simple, clean implementation for: {description}

Requirements:
- Return ONLY executable code
- No explanations or documentation 
- No error handling unless specifically requested
- No comments or examples
- Just working, runnable code

Code:"""
            
            # Use the unified Ollama client
            result = ollama_client.generate(prompt)
            
            if result['success']:
                return {
                    "status": "success",
                    "implementation": result['response'],
                    "model": ollama_client.default_model
                }
            else:
                return {"status": "error", "message": f"AI model execution failed: {result['error']}"}
            
        except Exception as e:
            return {"status": "unavailable", "message": f"AI model not available: {e}"}
    
    def handle_coordination_task(self, task: Dict) -> Dict:
        """Handle coordination tasks - delegate to other agents"""
        description = task["description"].lower()
        
        # Intelligent delegation based on task content
        if any(keyword in description for keyword in ["file", "directory", "folder", "create", "organize", "structure", "edit", "modify", "update", "add to", "enhance"]):
            # File operations -> file_manager
            delegated_task_id = self.comm.create_task(
                task_type="file_management",
                description=task["description"],
                assigned_to="file_manager",
                created_by=self.agent_id,
                priority=task.get("priority", 1)
            )
            return {"delegated_task_id": delegated_task_id, "delegated_to": "file_manager"}
        
        elif any(keyword in description for keyword in ["git", "commit", "push", "pull", "branch", "version"]):
            # Git operations -> git_manager
            delegated_task_id = self.comm.create_task(
                task_type="git_management", 
                description=task["description"],
                assigned_to="git_manager",
                created_by=self.agent_id,
                priority=task.get("priority", 1)
            )
            return {"delegated_task_id": delegated_task_id, "delegated_to": "git_manager"}
        
        elif any(keyword in description for keyword in ["code", "generate", "implement", "write", "develop"]):
            # Code generation -> coder
            delegated_task_id = self.comm.create_task(
                task_type="code_generation",
                description=task["description"],
                assigned_to="coder",
                created_by=self.agent_id,
                priority=task.get("priority", 1)
            )
            return {"delegated_task_id": delegated_task_id, "delegated_to": "coder"}
        
        elif any(keyword in description for keyword in ["review", "check", "analyze", "quality"]):
            # Code review -> code_reviewer
            delegated_task_id = self.comm.create_task(
                task_type="code_review",
                description=task["description"],
                assigned_to="code_reviewer",
                created_by=self.agent_id,
                priority=task.get("priority", 1)
            )
            return {"delegated_task_id": delegated_task_id, "delegated_to": "code_reviewer"}
        
        elif any(keyword in description for keyword in ["test", "testing", "unit", "integration"]):
            # Testing -> tester
            delegated_task_id = self.comm.create_task(
                task_type="testing",
                description=task["description"],
                assigned_to="tester",
                created_by=self.agent_id,
                priority=task.get("priority", 1)
            )
            return {"delegated_task_id": delegated_task_id, "delegated_to": "tester"}
        
        elif any(keyword in description for keyword in ["research", "find", "search", "investigate"]):
            # Research -> researcher
            delegated_task_id = self.comm.create_task(
                task_type="research",
                description=task["description"],
                assigned_to="researcher", 
                created_by=self.agent_id,
                priority=task.get("priority", 1)
            )
            return {"delegated_task_id": delegated_task_id, "delegated_to": "researcher"}
        
        else:
            # Default to coder for general tasks
            delegated_task_id = self.comm.create_task(
                task_type="general",
                description=task["description"],
                assigned_to="coder",
                created_by=self.agent_id,
                priority=task.get("priority", 1)
            )
            return {"delegated_task_id": delegated_task_id, "delegated_to": "coder"}
    
    def handle_code_review_task(self, task: Dict) -> Dict:
        """Handle code review tasks and create structured review reports for code rewriter"""
        
        description = task["description"]
        colored_print(f"INFO: CODE REVIEWER: Conducting comprehensive code review", Colors.BRIGHT_CYAN)
        colored_print(f"   Task: {description}", Colors.CYAN)
        
        # Use universal AI collaboration for code review
        review_result = self.conduct_comprehensive_code_review(description)
        
        # If issues found, automatically delegate to code rewriter
        if review_result.get("issues_found", 0) > 0:
            self.delegate_to_code_rewriter(review_result)
        
        return {
            "status": "completed",
            "review_report": review_result,
            "message": f"Code review completed: {review_result.get('summary', 'Review finished')}"
        }
    
    def conduct_comprehensive_code_review(self, description: str) -> Dict:
        """Conduct comprehensive code review using AI with project context"""
        
        # Create standardized AI input for code review
        standardized_input = self.create_standardized_ai_input(
            operation_type="CODE_REVIEW",
            task_description=f"Comprehensive code review: {description}",
            context_type="QUALITY_ANALYSIS",
            requirements=[
                "Analyze code quality and best practices",
                "Identify bugs, security issues, and performance problems",
                "Check for maintainability and readability issues",
                "Verify proper error handling and edge cases",
                "Assess architecture and design patterns"
            ],
            constraints=[
                "Provide specific line numbers and file locations for issues",
                "Categorize issues by severity (critical, major, minor)",
                "Suggest specific fixes for each issue found",
                "Include positive feedback for well-written code"
            ],
            expected_output="STRUCTURED_REVIEW_REPORT"
        )
        
        # Execute AI-powered code review
        ai_result = self.execute_standardized_ai_operation(standardized_input)
        
        if ai_result.get('status') == 'success':
            review_content = ai_result.get('implementation', '')
            return self.parse_review_report(review_content)
        else:
            # Fallback review
            return self.conduct_basic_code_review(description)
    
    def parse_review_report(self, review_content: str) -> Dict:
        """Parse AI review output into structured format"""
        
        # This parses the AI review into structured data
        # In a real implementation, this would parse AI output for:
        # - Issues found with severity levels
        # - Specific file locations and line numbers  
        # - Suggested fixes for each issue
        # - Overall quality assessment
        
        issues = []
        
        # Extract issues from AI review (simplified parsing)
        lines = review_content.split('\n')
        current_issue = {}
        
        for line in lines:
            if 'CRITICAL:' in line or 'MAJOR:' in line or 'MINOR:' in line:
                if current_issue:
                    issues.append(current_issue)
                current_issue = {
                    "severity": line.split(':')[0].strip(),
                    "description": line.split(':', 1)[1].strip() if ':' in line else line,
                    "file": "",
                    "line_number": 0,
                    "suggested_fix": ""
                }
            elif 'File:' in line and current_issue:
                current_issue["file"] = line.split(':', 1)[1].strip()
            elif 'Line:' in line and current_issue:
                try:
                    current_issue["line_number"] = int(line.split(':', 1)[1].strip())
                except:
                    pass
            elif 'Fix:' in line and current_issue:
                current_issue["suggested_fix"] = line.split(':', 1)[1].strip()
        
        if current_issue:
            issues.append(current_issue)
        
        return {
            "issues_found": len(issues),
            "issues": issues,
            "summary": f"Found {len(issues)} issues requiring attention",
            "ai_review_content": review_content,
            "timestamp": datetime.now().isoformat()
        }
    
    def conduct_basic_code_review(self, description: str) -> Dict:
        """Fallback basic code review when AI unavailable"""
        
        colored_print(f"   INFO: Conducting basic code review analysis", Colors.YELLOW)
        
        # Basic file analysis
        issues = []
        if self.project_process_files:
            for file_path, file_info in self.project_process_files.items():
                # Basic checks
                content = file_info['content']
                if 'TODO' in content or 'FIXME' in content:
                    issues.append({
                        "severity": "MINOR",
                        "description": "Contains TODO or FIXME comments",
                        "file": file_path,
                        "line_number": 0,
                        "suggested_fix": "Complete or remove TODO/FIXME items"
                    })
        
        return {
            "issues_found": len(issues),
            "issues": issues,
            "summary": f"Basic review completed - {len(issues)} issues found",
            "timestamp": datetime.now().isoformat()
        }
    
    def delegate_to_code_rewriter(self, review_result: Dict):
        """Delegate issues to code rewriter with structured task list"""
        
        issues = review_result.get("issues", [])
        if not issues:
            return
        
        colored_print(f"   PROCESS: Delegating {len(issues)} issues to code rewriter", Colors.BRIGHT_YELLOW)
        
        # Create structured task for code rewriter
        rewriter_task_description = f"Fix {len(issues)} code issues from review report"
        
        # Create detailed task with structured issue list
        task_id = self.comm.create_task(
            task_type="code_rewrite_from_review",
            description=rewriter_task_description,
            assigned_to="code_rewriter",
            created_by=self.agent_id,
            priority=1,
            data={
                "review_report": review_result,
                "total_issues": len(issues),
                "critical_issues": len([i for i in issues if i.get("severity") == "CRITICAL"]),
                "major_issues": len([i for i in issues if i.get("severity") == "MAJOR"]),
                "minor_issues": len([i for i in issues if i.get("severity") == "MINOR"]),
                "source_agent": self.agent_id
            }
        )
        
        colored_print(f"   SUCCESS: Created rewriter task {task_id} with {len(issues)} structured fixes", Colors.GREEN)
    
    def handle_file_management_task(self, task: Dict) -> Dict:
        """Handle file management tasks - create directories, organize project structure, edit files"""
        description = task["description"]
        
        colored_print(f"FOLDER: FILE MANAGER: Processing file management task", Colors.BRIGHT_CYAN)
        colored_print(f"   Task: {description}", Colors.CYAN)
        
        # Check if this is an edit task or create task
        if self.is_edit_task(description):
            return self.handle_file_edit_task(description)
        else:
            return self.handle_file_create_task(task)
    
    def is_edit_task(self, description: str) -> bool:
        """Determine if this is an edit task or create task"""
        edit_keywords = ["edit", "modify", "update", "change", "add to", "enhance", "improve"]
        desc_lower = description.lower()
        return any(keyword in desc_lower for keyword in edit_keywords)
    
    def handle_file_create_task(self, task: Dict) -> Dict:
        """Handle file creation tasks - Enhanced with auto project location"""
        description = task["description"]
        task_data = task.get("data", {})
        
        colored_print(f"FILE MANAGER: Processing creation task", Colors.BRIGHT_YELLOW)
        colored_print(f"   Task: {description}", Colors.WHITE)
        
        # STEP 1: Auto-locate existing project directory FIRST
        existing_project = self.auto_locate_project_directory(description, task_data)
        
        if existing_project:
            # Use existing project - create files within it
            project_path = existing_project["path"]
            project_name = existing_project["name"]
            
            colored_print(f"   FOUND: Located existing project '{project_name}'", Colors.BRIGHT_GREEN)
            colored_print(f"   PATH: {project_path}", Colors.GREEN)
            
            # Auto-set project focus for all file operations
            self.set_project_process(project_name)
            
            # Create the requested component/file within existing project
            result = self.create_component_in_existing_project(project_path, description, task_data)
            
            return {
                "type": "file_management_completed",
                "project_path": project_path,
                "project_name": project_name,
                "component_created": result.get("component_name"),
                "files_created": result.get("files_created", []),
                "message": f"Successfully created component in existing project '{project_name}'"
            }
        
        else:
            # No existing project - create new project structure
            colored_print(f"   INFO: No existing project found, creating new project", Colors.CYAN)
            
            # Extract project information from task data and description
            project_info = self.analyze_project_requirements(description, task_data)
            
            # Create project structure
            project_path = self.create_project_structure(project_info)
            
            return {
                "type": "file_management_completed",
                "project_path": project_path,
                "project_info": project_info,
                "message": f"Successfully created project structure at {project_path}",
                "files_created": self.list_created_files(project_path)
            }
    
    def auto_locate_project_directory(self, description: str, task_data: Dict = None) -> Dict:
        """Automatically locate existing project directory without creating UnknownProject"""
        import os
        
        colored_print(f"   AUTO: Scanning workspace for existing projects...", Colors.CYAN)
        
        # PRIORITY 1: Use current project if already set
        if hasattr(self, 'current_project_process') and self.current_project_process:
            current_path = os.path.join(self.workspace_dir, self.current_project_process)
            if os.path.exists(current_path):
                colored_print(f"   CURRENT: Using active project '{self.current_project_process}'", Colors.BRIGHT_GREEN)
                return {
                    "name": self.current_project_process,
                    "path": current_path,
                    "source": "current_project"
                }
        
        # PRIORITY 2: Look for project name in task data
        if task_data and 'project_name' in task_data:
            project_name = task_data['project_name']
            project_path = os.path.join(self.workspace_dir, project_name)
            if os.path.exists(project_path):
                colored_print(f"   TASK_DATA: Found project '{project_name}' from task data", Colors.BRIGHT_GREEN)
                return {
                    "name": project_name,
                    "path": project_path,
                    "source": "task_data"
                }
        
        # PRIORITY 3: Scan all existing projects in workspace
        existing_projects = []
        if os.path.exists(self.workspace_dir):
            for item in os.listdir(self.workspace_dir):
                item_path = os.path.join(self.workspace_dir, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    # Analyze if this is a valid project directory
                    project_info = self.analyze_existing_project_structure(item_path)
                    if project_info:
                        existing_projects.append({
                            "name": item,
                            "path": item_path,
                            "framework": project_info.get("framework"),
                            "suitability": self.calculate_project_suitability(item_path, description)
                        })
        
        if existing_projects:
            colored_print(f"   SCAN: Found {len(existing_projects)} existing projects", Colors.CYAN)
            for proj in existing_projects:
                colored_print(f"      • {proj['name']} ({proj['framework']}) - Suitability: {proj['suitability']}", Colors.CYAN)
            
            # PRIORITY 4: Use most suitable existing project
            best_project = max(existing_projects, key=lambda x: x['suitability'])
            if best_project['suitability'] > 0.3:  # Minimum suitability threshold
                colored_print(f"   BEST_MATCH: Selected '{best_project['name']}' (suitability: {best_project['suitability']:.2f})", Colors.BRIGHT_GREEN)
                return {
                    "name": best_project['name'],
                    "path": best_project['path'],
                    "source": "auto_selected",
                    "suitability": best_project['suitability']
                }
        
        colored_print(f"   RESULT: No suitable existing project found", Colors.YELLOW)
        return None
    
    def analyze_existing_project_structure(self, project_path: str) -> Dict:
        """Analyze an existing directory to determine if it's a valid project"""
        import os
        
        project_info = {"framework": "unknown", "is_valid_project": False}
        
        try:
            files = os.listdir(project_path)
            
            # Check for common project indicators
            if "package.json" in files:
                project_info["framework"] = "javascript/node"
                project_info["is_valid_project"] = True
            elif "requirements.txt" in files or "setup.py" in files:
                project_info["framework"] = "python"
                project_info["is_valid_project"] = True
            elif "pom.xml" in files:
                project_info["framework"] = "java"
                project_info["is_valid_project"] = True
            elif "Cargo.toml" in files:
                project_info["framework"] = "rust"
                project_info["is_valid_project"] = True
            elif "src" in files or "components" in files:
                project_info["is_valid_project"] = True
                
                # Check deeper for React/Vue indicators
                src_path = os.path.join(project_path, "src")
                if os.path.exists(src_path):
                    src_files = os.listdir(src_path)
                    if any(".jsx" in f for f in src_files):
                        project_info["framework"] = "react"
                    elif any(".vue" in f for f in src_files):
                        project_info["framework"] = "vue"
                    elif "App.js" in src_files:
                        project_info["framework"] = "react"
        except:
            pass
        
        return project_info if project_info["is_valid_project"] else None
    
    def calculate_project_suitability(self, project_path: str, task_description: str) -> float:
        """Calculate how suitable an existing project is for the given task"""
        import os
        
        suitability = 0.0
        desc_lower = task_description.lower()
        project_name = os.path.basename(project_path).lower()
        
        # Name matching
        if "time" in desc_lower and "time" in project_name:
            suitability += 0.8
        elif "todo" in desc_lower and "todo" in project_name:
            suitability += 0.8
        elif "app" in desc_lower and "app" in project_name:
            suitability += 0.4
        
        # Component matching
        try:
            # Check if project has similar components already
            if os.path.exists(os.path.join(project_path, "src", "components")):
                components_dir = os.path.join(project_path, "src", "components")
                component_files = os.listdir(components_dir)
                
                if "time" in desc_lower:
                    if any("time" in f.lower() for f in component_files):
                        suitability += 0.5
                if "date" in desc_lower:
                    if any("date" in f.lower() for f in component_files):
                        suitability += 0.5
                        
                # Base suitability for having components directory
                suitability += 0.2
        except:
            pass
        
        # Framework compatibility
        project_info = self.analyze_existing_project_structure(project_path)
        if project_info:
            if ("react" in desc_lower and project_info.get("framework") == "react") or \
               ("vue" in desc_lower and project_info.get("framework") == "vue") or \
               ("javascript" in desc_lower and "javascript" in project_info.get("framework", "")):
                suitability += 0.3
        
        return min(suitability, 1.0)  # Cap at 1.0
    
    def analyze_component_requirements(self, description: str, project_path: str) -> Dict:
        """Analyze what component needs to be created"""
        import os
        
        desc_lower = description.lower()
        component_info = {
            "name": "UnknownComponent",
            "type": "generic",
            "features": [],
            "target_dir": "src/components"
        }
        
        # Detect component name and type
        if "time" in desc_lower:
            component_info["name"] = "TimeComponent"
            component_info["type"] = "display"
            component_info["features"] = ["time_display", "real_time_updates", "formatting"]
        elif "date" in desc_lower:
            component_info["name"] = "DateComponent"  
            component_info["type"] = "display"
            component_info["features"] = ["date_display", "formatting"]
        elif "week" in desc_lower:
            component_info["name"] = "WeekComponent"
            component_info["type"] = "display"
            component_info["features"] = ["week_number", "week_display"]
        elif "todo" in desc_lower or "task" in desc_lower:
            component_info["name"] = "TodoComponent"
            component_info["type"] = "interactive"
            component_info["features"] = ["add_task", "remove_task", "mark_complete"]
        elif "button" in desc_lower:
            component_info["name"] = "Button"
            component_info["type"] = "ui"
            component_info["features"] = ["clickable", "customizable"]
        
        # Determine target directory based on project structure
        if os.path.exists(os.path.join(project_path, "src", "components")):
            component_info["target_dir"] = "src/components"
        elif os.path.exists(os.path.join(project_path, "components")):
            component_info["target_dir"] = "components"
        elif os.path.exists(os.path.join(project_path, "src")):
            component_info["target_dir"] = "src"
        else:
            component_info["target_dir"] = "."
        
        colored_print(f"      Component: {component_info['name']} ({component_info['type']})", Colors.YELLOW)
        colored_print(f"      Target: {component_info['target_dir']}", Colors.YELLOW)
        colored_print(f"      Features: {', '.join(component_info['features'])}", Colors.YELLOW)
        
        return component_info
    
    def get_project_structure_context(self, project_path: str) -> str:
        """Get project structure context for AI model"""
        import os
        
        context = f"PROJECT STRUCTURE ANALYSIS:\n"
        context += f"Project Path: {project_path}\n\n"
        
        try:
            # Get directory structure
            context += "DIRECTORY STRUCTURE:\n"
            for root, dirs, files in os.walk(project_path):
                level = root.replace(project_path, '').count(os.sep)
                indent = '  ' * level
                context += f"{indent}{os.path.basename(root)}/\n"
                
                sub_indent = '  ' * (level + 1)
                for file in files[:10]:  # Limit to first 10 files per directory
                    context += f"{sub_indent}{file}\n"
                    
                if len(files) > 10:
                    context += f"{sub_indent}... ({len(files) - 10} more files)\n"
                
                # Don't go too deep
                if level > 3:
                    dirs[:] = []
            
            # Analyze key files for patterns
            context += "\nKEY FILES ANALYSIS:\n"
            
            # Check package.json for project type
            package_json_path = os.path.join(project_path, "package.json")
            if os.path.exists(package_json_path):
                try:
                    import json
                    with open(package_json_path, 'r') as f:
                        package_data = json.load(f)
                        context += f"Framework: {package_data.get('name', 'Unknown')}\n"
                        if 'dependencies' in package_data:
                            deps = list(package_data['dependencies'].keys())[:5]
                            context += f"Dependencies: {', '.join(deps)}\n"
                except:
                    context += "Framework: JavaScript project (package.json found)\n"
            
            # Check for existing components
            components_dir = os.path.join(project_path, "src", "components")
            if os.path.exists(components_dir):
                existing_components = [f for f in os.listdir(components_dir) 
                                     if f.endswith(('.js', '.jsx', '.vue', '.ts', '.tsx'))]
                if existing_components:
                    context += f"Existing Components: {', '.join(existing_components[:5])}\n"
            
        except Exception as e:
            context += f"Error analyzing structure: {e}\n"
        
        return context
    
    def execute_ai_component_creation(self, project_path: str, component_info: Dict, ai_result: Dict) -> list:
        """Execute component creation based on AI analysis"""
        import os
        
        files_created = []
        
        try:
            # Parse AI output for file creation instructions
            implementation = ai_result.get('implementation', '')
            
            # This would normally parse the AI output to extract file paths and content
            # For now, create a basic component file
            
            target_dir = os.path.join(project_path, component_info['target_dir'])
            os.makedirs(target_dir, exist_ok=True)
            
            # Determine file extension based on project
            project_info = self.analyze_existing_project_structure(project_path)
            
            if project_info and project_info.get('framework') == 'react':
                file_extension = '.jsx'
            elif project_info and project_info.get('framework') == 'vue':
                file_extension = '.vue'
            else:
                file_extension = '.js'
            
            # Create the component file
            component_file = os.path.join(target_dir, f"{component_info['name']}{file_extension}")
            
            # Generate component content using AI result
            component_content = self.generate_component_content(component_info, ai_result, file_extension)
            
            with open(component_file, 'w') as f:
                f.write(component_content)
            
            files_created.append(component_file)
            colored_print(f"      Created: {os.path.relpath(component_file, project_path)}", Colors.GREEN)
            
        except Exception as e:
            colored_print(f"   ERROR: Failed to create AI component: {e}", Colors.RED)
            files_created = self.create_fallback_component(project_path, component_info)
        
        return files_created
    
    def create_fallback_component(self, project_path: str, component_info: Dict) -> list:
        """Create a basic fallback component if AI fails"""
        import os
        
        files_created = []
        
        try:
            target_dir = os.path.join(project_path, component_info['target_dir'])
            os.makedirs(target_dir, exist_ok=True)
            
            # Create basic React component
            component_file = os.path.join(target_dir, f"{component_info['name']}.jsx")
            
            component_content = f"""import React from 'react';

const {component_info['name']} = () => {{
    return (
        <div className="{component_info['name'].lower()}-component">
            <h3>{component_info['name']}</h3>
            <p>Component created by File Manager</p>
            {self.generate_feature_elements(component_info['features'])}
        </div>
    );
}};

export default {component_info['name']};
"""
            
            with open(component_file, 'w') as f:
                f.write(component_content)
            
            files_created.append(component_file)
            colored_print(f"      Created: {os.path.relpath(component_file, project_path)}", Colors.GREEN)
            
        except Exception as e:
            colored_print(f"   ERROR: Failed to create fallback component: {e}", Colors.RED)
        
        return files_created
    
    def generate_feature_elements(self, features: list) -> str:
        """Generate JSX elements based on component features"""
        elements = ""
        
        if "time_display" in features:
            elements += "\n            <div className='time-display'>{new Date().toLocaleTimeString()}</div>"
        if "date_display" in features:
            elements += "\n            <div className='date-display'>{new Date().toLocaleDateString()}</div>"
        if "week_number" in features:
            elements += "\n            <div className='week-number'>Week {Math.ceil((Date.now() - new Date(new Date().getFullYear(), 0, 1)) / (7 * 24 * 60 * 60 * 1000))}</div>"
        
        return elements
    
    def generate_component_content(self, component_info: Dict, ai_result: Dict, file_extension: str) -> str:
        """Generate component content based on AI result and component info"""
        
        # If AI provided detailed implementation, use it
        implementation = ai_result.get('implementation', '')
        
        if implementation and len(implementation) > 100:
            return implementation
        
        # Otherwise, generate based on component info
        if file_extension == '.jsx':
            return self.generate_react_component(component_info)
        elif file_extension == '.vue':
            return self.generate_vue_component(component_info)
        else:
            return self.generate_js_component(component_info)
    
    def generate_react_component(self, component_info: Dict) -> str:
        """Generate a React component"""
        name = component_info['name']
        features = component_info.get('features', [])
        
        return f"""import React, {{ useState, useEffect }} from 'react';

const {name} = () => {{
    {self.generate_react_hooks(features)}

    return (
        <div className="{name.lower()}-container">
            <h2>{name}</h2>
            {self.generate_react_jsx(features)}
        </div>
    );
}};

export default {name};
"""
    
    def generate_react_hooks(self, features: list) -> str:
        """Generate React hooks based on features"""
        hooks = []
        
        if any(f in features for f in ["time_display", "real_time_updates"]):
            hooks.append("const [currentTime, setCurrentTime] = useState(new Date());")
            hooks.append("""
    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentTime(new Date());
        }, 1000);
        
        return () => clearInterval(timer);
    }, []);""")
        
        return "\n    ".join(hooks)
    
    def generate_react_jsx(self, features: list) -> str:
        """Generate React JSX based on features"""
        jsx_elements = []
        
        if "time_display" in features:
            jsx_elements.append("<div className='time'>{currentTime.toLocaleTimeString()}</div>")
        if "date_display" in features:
            jsx_elements.append("<div className='date'>{currentTime.toLocaleDateString()}</div>")
        if "week_number" in features:
            jsx_elements.append("<div className='week'>Week {Math.ceil((currentTime - new Date(currentTime.getFullYear(), 0, 1)) / (7 * 24 * 60 * 60 * 1000))}</div>")
        
        if not jsx_elements:
            jsx_elements.append("<p>Component ready for customization</p>")
        
        return "\n            ".join(jsx_elements)
    
    def generate_vue_component(self, component_info: Dict) -> str:
        """Generate a Vue component"""
        name = component_info['name']
        features = component_info.get('features', [])
        
        return f"""<template>
    <div class="{name.lower()}-container">
        <h2>{name}</h2>
        {self.generate_vue_template(features)}
    </div>
</template>

<script>
export default {{
    name: '{name}',
    {self.generate_vue_script(features)}
}};
</script>

<style scoped>
.{name.lower()}-container {{
    padding: 1rem;
    border: 1px solid #ccc;
    border-radius: 8px;
}}
</style>
"""
    
    def generate_vue_template(self, features: list) -> str:
        """Generate Vue template based on features"""
        template_elements = []
        
        if "time_display" in features:
            template_elements.append("<div class='time'>{{ currentTime.toLocaleTimeString() }}</div>")
        if "date_display" in features:
            template_elements.append("<div class='date'>{{ currentTime.toLocaleDateString() }}</div>")
        if "week_number" in features:
            template_elements.append("<div class='week'>Week {{ weekNumber }}</div>")
        
        if not template_elements:
            template_elements.append("<p>Component ready for customization</p>")
        
        return "\n        ".join(template_elements)
    
    def generate_vue_script(self, features: list) -> str:
        """Generate Vue script section based on features"""
        if any(f in features for f in ["time_display", "real_time_updates", "week_number"]):
            return """data() {
        return {
            currentTime: new Date()
        };
    },
    computed: {
        weekNumber() {
            const startOfYear = new Date(this.currentTime.getFullYear(), 0, 1);
            return Math.ceil((this.currentTime - startOfYear) / (7 * 24 * 60 * 60 * 1000));
        }
    },
    mounted() {
        this.timer = setInterval(() => {
            this.currentTime = new Date();
        }, 1000);
    },
    beforeUnmount() {
        if (this.timer) {
            clearInterval(this.timer);
        }
    }"""
        else:
            return """data() {
        return {};
    }"""
    
    def generate_js_component(self, component_info: Dict) -> str:
        """Generate a JavaScript component"""
        name = component_info['name']
        features = component_info.get('features', [])
        
        return f"""class {name} {{
    constructor(container) {{
        this.container = container;
        {self.generate_js_properties(features)}
        this.init();
    }}
    
    init() {{
        this.render();
        {self.generate_js_init(features)}
    }}
    
    render() {{
        this.container.innerHTML = `
            <div class="{name.lower()}-component">
                <h2>{name}</h2>
                {self.generate_js_html(features)}
            </div>
        `;
    }}
    
    {self.generate_js_methods(features)}
}}

export default {name};
"""
    
    def generate_js_properties(self, features: list) -> str:
        """Generate JavaScript properties based on features"""
        if any(f in features for f in ["time_display", "real_time_updates"]):
            return "this.currentTime = new Date();"
        return ""
    
    def generate_js_init(self, features: list) -> str:
        """Generate JavaScript initialization based on features"""
        if any(f in features for f in ["time_display", "real_time_updates"]):
            return """this.timer = setInterval(() => {
            this.currentTime = new Date();
            this.updateDisplay();
        }, 1000);"""
        return ""
    
    def generate_js_html(self, features: list) -> str:
        """Generate JavaScript HTML based on features"""
        html_elements = []
        
        if "time_display" in features:
            html_elements.append("<div class='time' id='time-display'></div>")
        if "date_display" in features:
            html_elements.append("<div class='date' id='date-display'></div>")
        if "week_number" in features:
            html_elements.append("<div class='week' id='week-display'></div>")
        
        if not html_elements:
            html_elements.append("<p>Component ready for customization</p>")
        
        return "\\n                ".join(html_elements)
    
    def generate_js_methods(self, features: list) -> str:
        """Generate JavaScript methods based on features"""
        if any(f in features for f in ["time_display", "real_time_updates", "date_display", "week_number"]):
            return """updateDisplay() {
        const timeEl = this.container.querySelector('#time-display');
        const dateEl = this.container.querySelector('#date-display');
        const weekEl = this.container.querySelector('#week-display');
        
        if (timeEl) timeEl.textContent = this.currentTime.toLocaleTimeString();
        if (dateEl) dateEl.textContent = this.currentTime.toLocaleDateString();
        if (weekEl) {
            const startOfYear = new Date(this.currentTime.getFullYear(), 0, 1);
            const weekNumber = Math.ceil((this.currentTime - startOfYear) / (7 * 24 * 60 * 60 * 1000));
            weekEl.textContent = `Week ${weekNumber}`;
        }
    }
    
    destroy() {
        if (this.timer) {
            clearInterval(this.timer);
        }
    }"""
        else:
            return """// Add custom methods here"""
    
    def create_component_in_existing_project(self, project_path: str, description: str, task_data: Dict = None) -> Dict:
        """Create a component/file within an existing project"""
        import os
        
        colored_print(f"   COMPONENT: Creating component in existing project", Colors.BRIGHT_YELLOW)
        
        # Analyze what component to create
        component_info = self.analyze_component_requirements(description, project_path)
        
        # Send project structure context to AI model for intelligent file placement
        project_context = self.get_project_structure_context(project_path)
        
        # Create standardized AI input with project context
        standardized_input = self.create_standardized_ai_input(
            operation_type="COMPONENT_CREATION",
            task_description=f"Create component in existing project: {description}",
            context_type="EXISTING_PROJECT_ENHANCEMENT",
            requirements=[
                f"Component: {component_info.get('name', 'Unknown')}",
                f"Type: {component_info.get('type', 'generic')}",
                f"Features: {', '.join(component_info.get('features', []))}",
                f"Target directory: {component_info.get('target_dir', 'src/components')}"
            ],
            constraints=[
                "Analyze existing project structure and follow established patterns",
                "Use same coding style and conventions as existing files", 
                "Integrate seamlessly with existing components and architecture",
                "Place files in appropriate directories based on project structure"
            ],
            expected_output="COMPONENT_FILES_AND_INTEGRATION",
            project_context=project_context
        )
        
        # Execute AI-powered component creation
        ai_result = self.execute_standardized_ai_operation(standardized_input)
        
        files_created = []
        if ai_result.get('status') == 'success':
            files_created = self.execute_ai_component_creation(project_path, component_info, ai_result)
        else:
            files_created = self.create_fallback_component(project_path, component_info)
        
        colored_print(f"   SUCCESS: Created component '{component_info.get('name')}' with {len(files_created)} files", Colors.BRIGHT_GREEN)
        
        return {
            "component_name": component_info.get('name'),
            "files_created": files_created,
            "target_directory": component_info.get('target_dir')
        }

    def handle_file_edit_task(self, description: str) -> Dict:
        """Handle file editing tasks"""
        colored_print(f"️ FILE EDITOR: Processing file edit request", Colors.BRIGHT_YELLOW)
        
        # Find the project to edit
        project_path = self.find_project_to_edit(description)
        
        if not project_path:
            return {
                "type": "file_edit_failed",
                "error": "Could not find project to edit",
                "message": "Please specify the project name or ensure the project exists"
            }
        
        colored_print(f"   FOLDER: Found project: {project_path}", Colors.YELLOW)
        
        # Analyze what needs to be edited
        edit_info = self.analyze_edit_requirements(description)
        
        # Perform the actual edits
        edited_files = self.perform_file_edits(project_path, edit_info)
        
        return {
            "type": "file_edit_completed",
            "project_path": project_path,
            "edit_info": edit_info,
            "edited_files": edited_files,
            "message": f"Successfully edited {len(edited_files)} file(s) in project"
        }
    
    def find_project_to_edit(self, description: str) -> str:
        """Find the project that needs to be edited"""
        import os
        
        # FIRST PRIORITY: Use current project if set
        if hasattr(self, 'current_project_process') and self.current_project_process:
            current_project_path = os.path.join(self.workspace_dir, self.current_project_process)
            if os.path.exists(current_project_path):
                colored_print(f"   AUTO: Using current project: {self.current_project_process}", Colors.BRIGHT_GREEN)
                return current_project_path
        
        # Extract project name from description
        desc_lower = description.lower()
        
        # Look for existing projects in workspace
        workspace_projects = []
        if os.path.exists(self.workspace_dir):
            for item in os.listdir(self.workspace_dir):
                item_path = os.path.join(self.workspace_dir, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    workspace_projects.append(item)
        
        colored_print(f"   INFO: Available projects: {', '.join(workspace_projects)}", Colors.CYAN)
        
        # Try to match project name from description
        for project in workspace_projects:
            if project.lower() in desc_lower:
                colored_print(f"   MATCH: Found project '{project}' mentioned in task description", Colors.YELLOW)
                return os.path.join(self.workspace_dir, project)
        
        # If only one project exists, use it and set as current
        if len(workspace_projects) == 1:
            colored_print(f"   TARGET: Using only available project: {workspace_projects[0]}", Colors.CYAN)
            # Auto-set as current project
            self.set_project_process(workspace_projects[0])
            return os.path.join(self.workspace_dir, workspace_projects[0])
        
        # Check for common project names
        common_names = ["timedisplayapp", "todoapp", "app", "project"]
        for name in common_names:
            if name in desc_lower:
                for project in workspace_projects:
                    if name in project.lower():
                        colored_print(f"   COMMON: Matched common name '{name}' to project '{project}'", Colors.YELLOW)
                        return os.path.join(self.workspace_dir, project)
        
        # No project found
        colored_print(f"   WARNING: No suitable project found for editing. Available: {workspace_projects}", Colors.RED)
        return None
    
    def analyze_edit_requirements(self, description: str) -> Dict:
        """Analyze what needs to be edited"""
        desc_lower = description.lower()
        
        edit_info = {
            "action": "modify",
            "target_component": None,
            "new_features": [],
            "files_to_edit": []
        }
        
        # Detect what component to edit
        if "time display" in desc_lower or "timedisplay" in desc_lower:
            edit_info["target_component"] = "TimeDisplay"
            edit_info["files_to_edit"].append("src/components/TimeDisplay.js")
        
        # Detect what to add
        if "week" in desc_lower and "number" in desc_lower:
            edit_info["new_features"].append("week_number")
        if "week display" in desc_lower:
            edit_info["new_features"].append("week_display")
        
        colored_print(f"   INFO: Edit Analysis:", Colors.BRIGHT_YELLOW)
        colored_print(f"      Target: {edit_info['target_component']}", Colors.YELLOW)
        colored_print(f"      Features: {', '.join(edit_info['new_features'])}", Colors.YELLOW)
        colored_print(f"      Files: {', '.join(edit_info['files_to_edit'])}", Colors.YELLOW)
        
        return edit_info
    
    def perform_file_edits(self, project_path: str, edit_info: Dict) -> List[str]:
        """Perform the actual file edits using AI collaboration"""
        import os
        
        edited_files = []
        
        for file_path in edit_info["files_to_edit"]:
            full_file_path = os.path.join(project_path, file_path)
            
            if os.path.exists(full_file_path):
                colored_print(f"   ️ Editing: {file_path}", Colors.BRIGHT_GREEN)
                
                # Use AI collaboration for any file type
                success = self.edit_file_with_ai_collaboration(full_file_path, edit_info)
                
                if success:
                    edited_files.append(file_path)
                    colored_print(f"   SUCCESS: Completed: {file_path}", Colors.GREEN)
                else:
                    colored_print(f"   WARNING: Edit guidance provided for: {file_path}", Colors.YELLOW)
            else:
                colored_print(f"   ERROR: File not found: {file_path}", Colors.RED)
        
        return edited_files
    
    def edit_file_with_ai_collaboration(self, file_path: str, edit_info: Dict) -> bool:
        """Edit any file using AI collaboration"""
        
        # Read the current file content
        with open(file_path, 'r') as f:
            current_content = f.read()
        
        colored_print(f"       Current file content loaded ({len(current_content)} chars)", Colors.CYAN)
        
        # Use AI model to generate the enhanced version
        enhanced_content = self.collaborate_with_ai_for_file_edit(
            file_path=file_path,
            current_content=current_content,
            edit_requirements=edit_info
        )
        
        if enhanced_content and enhanced_content != current_content:
            # Write the AI-generated enhanced content
            with open(file_path, 'w') as f:
                f.write(enhanced_content)
            
            colored_print(f"      AGENT: AI-generated enhancement applied", Colors.BRIGHT_GREEN)
            return True
        else:
            colored_print(f"      TIP: Collaborative guidance provided (AI model unavailable)", Colors.CYAN)
            return False
    
    def edit_time_display_component(self, file_path: str, edit_info: Dict):
        """Edit the TimeDisplay component using AI collaboration"""
        
        # Read the current file content
        with open(file_path, 'r') as f:
            current_content = f.read()
        
        colored_print(f"       Current file content loaded ({len(current_content)} chars)", Colors.CYAN)
        
        # Use AI model to generate the enhanced version
        enhanced_content = self.collaborate_with_ai_for_file_edit(
            file_path=file_path,
            current_content=current_content,
            edit_requirements=edit_info
        )
        
        if enhanced_content and enhanced_content != current_content:
            # Write the AI-generated enhanced component
            with open(file_path, 'w') as f:
                f.write(enhanced_content)
            
            colored_print(f"      AGENT: AI-generated enhancement applied", Colors.BRIGHT_GREEN)
        else:
            colored_print(f"      WARNING: No changes generated by AI model", Colors.YELLOW)
    
    def collaborate_with_ai_for_file_edit(self, file_path: str, current_content: str, edit_requirements: Dict) -> str:
        """Universal file editing using standardized AI collaboration"""
        
        colored_print(f"      AGENT: Universal AI collaboration for file editing", Colors.BRIGHT_CYAN)
        
        # Prepare standardized AI input for file editing
        file_name = file_path.split('/')[-1]
        features_needed = ", ".join(edit_requirements.get("new_features", []))
        
        standardized_input = self.create_standardized_ai_input(
            operation_type="FILE_ENHANCEMENT",
            task_description=f"Enhance {file_name} with requested features",
            context_type="FILE_EDITING",
            requirements=[
                f"Target file: {file_name}",
                f"Enhancement request: {features_needed}",
                f"Target component: {edit_requirements.get('target_component', 'File')}",
                "Maintain all existing functionality",
                "Integrate seamlessly with project structure"
            ],
            constraints=[
                "Preserve existing code structure and patterns",
                "Use appropriate technology stack for file type",
                "Follow project's established conventions and style",
                "Ensure backward compatibility",
                "Make minimal necessary changes"
            ],
            expected_output="ENHANCED_FILE_CONTENT",
            target_files=[file_name],
            current_file_content=current_content
        )
        
        # Execute standardized AI file enhancement
        ai_result = self.execute_standardized_ai_operation(standardized_input)
        
        if ai_result.get('status') == 'success':
            enhanced_content = ai_result.get('implementation', '').strip()
            
            # Universal validation - check if content is meaningful
            if enhanced_content and len(enhanced_content) > len(current_content) * 0.5:
                colored_print(f"      SUCCESS: AI model provided enhanced file content", Colors.GREEN)
                return enhanced_content
            else:
                colored_print(f"      WARNING: AI model output appears incomplete", Colors.YELLOW)
        else:
            colored_print(f"      WARNING: AI model unavailable for enhancement", Colors.YELLOW)
        
        # Fallback: provide guidance and return original
        colored_print(f"      TIP: Providing collaborative guidance instead", Colors.CYAN)
        self.provide_universal_edit_guidance(file_path, edit_requirements)
        
        return current_content  # Return original if AI can't help
    
    def provide_universal_edit_guidance(self, file_path: str, edit_requirements: Dict):
        """Provide universal editing guidance for any file type"""
        
        file_name = file_path.split('/')[-1]
        file_ext = file_name.split('.')[-1] if '.' in file_name else 'unknown'
        features = ", ".join(edit_requirements.get("new_features", []))
        
        colored_print(f"      INFO: UNIVERSAL EDIT GUIDANCE:", Colors.BRIGHT_CYAN)
        colored_print(f"         File: {file_name} (type: {file_ext})", Colors.CYAN)
        colored_print(f"         Requested: {features}", Colors.CYAN)
        colored_print(f"      TIP: SUGGESTED APPROACH:", Colors.CYAN)
        colored_print(f"         1. Analyze current file structure and patterns", Colors.CYAN)
        colored_print(f"         2. Identify integration points for new features", Colors.CYAN)
        colored_print(f"         3. Implement using project's established conventions", Colors.CYAN)
        colored_print(f"         4. Test changes for compatibility and functionality", Colors.CYAN)
        colored_print(f"       This requires AI model collaboration for implementation.", Colors.MAGENTA)
    
    def try_ai_implementation_for_edit(self, prompt: str) -> Dict:
        """Try to get AI implementation for file editing"""
        try:
            # Check if Ollama is available (local or remote)
            if not ollama_client.is_available():
                return {"status": "unavailable", "message": "Ollama not available"}
            
            # Use the unified Ollama client
            result = ollama_client.generate(prompt)
            
            if result['success']:
                return {
                    "status": "success",
                    "implementation": result['response'],
                    "model": ollama_client.default_model
                }
            else:
                return {"status": "error", "message": f"AI model execution failed: {result['error']}"}
            
        except Exception as e:
            return {"status": "unavailable", "message": f"AI model not available: {e}"}
    
    def provide_edit_guidance(self, file_path: str, edit_requirements: Dict):
        """Provide collaborative guidance when AI model is unavailable"""
        
        colored_print(f"      INFO: COLLABORATIVE EDIT GUIDANCE:", Colors.BRIGHT_YELLOW)
        colored_print(f"         File: {file_path.split('/')[-1]}", Colors.YELLOW)
        colored_print(f"         Target: {edit_requirements.get('target_component', 'Component')}", Colors.YELLOW)
        colored_print(f"         Features needed: {', '.join(edit_requirements.get('new_features', []))}", Colors.YELLOW)
        colored_print(f"", Colors.YELLOW)
        colored_print(f"      TIP: SUGGESTED APPROACH:", Colors.BRIGHT_CYAN)
        colored_print(f"         1. Read the current file content", Colors.CYAN)
        colored_print(f"         2. Identify where to add new functionality", Colors.CYAN)
        colored_print(f"         3. Implement the requested features", Colors.CYAN)
        colored_print(f"         4. Test the changes work correctly", Colors.CYAN)
        colored_print(f"", Colors.CYAN)
        colored_print(f"       This task requires AI model collaboration for actual implementation.", Colors.MAGENTA)
    
    def analyze_project_requirements(self, description: str, task_data: Dict = None) -> Dict:
        """Analyze project requirements from task data and description"""
        desc_lower = description.lower()
        
        project_info = {
            "name": "UnknownProject",
            "framework": None,
            "components": [],
            "features": []
        }
        
        # FIRST PRIORITY: Use task data if available
        if task_data:
            if 'project_name' in task_data:
                project_info["name"] = task_data['project_name']
                colored_print(f"   DATA: Using project name from task data: {project_info['name']}", Colors.BRIGHT_GREEN)
            
            if 'project_type' in task_data:
                project_info["framework"] = task_data['project_type']
                colored_print(f"   DATA: Using project type from task data: {project_info['framework']}", Colors.BRIGHT_GREEN)
            
            if 'description' in task_data:
                project_info["description"] = task_data['description']
        
        # FALLBACK: Extract project name from description if not in task data
        if project_info["name"] == "UnknownProject":
            if "timedisplayapp" in desc_lower or "time display app" in desc_lower:
                project_info["name"] = "TimeDisplayApp"
            elif "todoapp" in desc_lower or "todo app" in desc_lower:
                project_info["name"] = "TodoApp"
            elif "project" in desc_lower:
                # Try to extract project name
                words = description.split()
                for i, word in enumerate(words):
                    if word.lower() in ["project", "app", "application"] and i > 0:
                        project_info["name"] = words[i-1].replace(",", "").replace(".", "")
                        break
        
        # Detect framework
        if "react" in desc_lower:
            project_info["framework"] = "react"
            project_info["components"].extend(["App", "components", "styles"])
        elif "vue" in desc_lower:
            project_info["framework"] = "vue"
            project_info["components"].extend(["App", "components", "assets"])
        elif "python" in desc_lower:
            project_info["framework"] = "python"
            project_info["components"].extend(["src", "tests", "docs"])
        elif "node" in desc_lower:
            project_info["framework"] = "nodejs"
            project_info["components"].extend(["src", "routes", "models"])
        
        # Extract specific components mentioned
        if "time" in desc_lower:
            project_info["components"].append("TimeDisplay")
        if "date" in desc_lower:
            project_info["components"].append("DateDisplay") 
        if "week" in desc_lower:
            project_info["components"].append("WeekDisplay")
        
        colored_print(f"STATUS: PROJECT ANALYSIS:", Colors.BRIGHT_YELLOW)
        colored_print(f"   Name: {project_info['name']}", Colors.YELLOW)
        colored_print(f"   Framework: {project_info['framework']}", Colors.YELLOW)
        colored_print(f"   Components: {', '.join(project_info['components'])}", Colors.YELLOW)
        
        return project_info
    
    def create_project_structure(self, project_info: Dict) -> str:
        """Universal project creation using AI collaboration with standardized input/output"""
        import os
        
        project_name = project_info["name"]
        
        # Create project in workspace
        project_path = os.path.join(self.workspace_dir, project_name)
        
        colored_print(f"CONFIG: CREATING UNIVERSAL PROJECT STRUCTURE:", Colors.BRIGHT_GREEN)
        colored_print(f"   Path: {project_path}", Colors.GREEN)
        
        # Create main project directory
        os.makedirs(project_path, exist_ok=True)
        
        # Use standardized AI approach for project creation
        standardized_input = self.create_standardized_ai_input(
            operation_type="PROJECT_CREATION",
            task_description=f"Create complete project structure for: {project_name}",
            context_type="PROJECT_STRUCTURE",
            requirements=[
                f"Project name: {project_name}",
                f"Description: {project_info.get('description', 'AI-generated project')}",
                f"Components: {', '.join(project_info.get('components', []))}",
                f"Features: {', '.join(project_info.get('features', []))}"
            ],
            constraints=[
                "Analyze project requirements to determine appropriate technology stack",
                "Create modern, scalable project structure",
                "Include all necessary configuration and setup files",
                "Follow current best practices for chosen technology"
            ],
            expected_output="PROJECT_FILES_AND_STRUCTURE"
        )
        
        # Execute AI-powered project creation
        ai_result = self.execute_standardized_ai_operation(standardized_input)
        
        if ai_result.get('status') == 'success':
            self.execute_ai_project_creation(project_path, project_info, ai_result)
        else:
            self.create_universal_fallback_structure(project_path, project_info)
        
        # Automatically set this as the current project for the file manager
        self.auto_set_project_focus(project_name, project_path)
        
        colored_print(f"SUCCESS: UNIVERSAL PROJECT CREATED: {project_path}", Colors.BRIGHT_GREEN)
        colored_print(f"AUTO: Project '{project_name}' set as current working directory", Colors.BRIGHT_YELLOW)
        return project_path
    
    def auto_set_project_focus(self, project_name: str, project_path: str):
        """Automatically set the current project for file manager operations"""
        
        # Set the current project for this file manager instance
        self.set_project_process(project_name)
        
        # Also broadcast to all other agents that this is the active project
        self.broadcast_project_change(project_name, project_path)
        
        colored_print(f"   AUTO: File manager now focused on project '{project_name}'", Colors.CYAN)
        colored_print(f"   NOTIFY: All agents notified of new active project", Colors.CYAN)
    
    def broadcast_project_change(self, project_name: str, project_path: str):
        """Notify all agents about the new active project"""
        
        # Get all active agents
        active_agents = self.comm.get_active_agents()
        
        # Send project notification task to all agents
        for agent in active_agents:
            if agent['id'] != self.agent_id:  # Don't send to self
                self.comm.create_task(
                    task_type='project_notification',
                    description=f"Project '{project_name}' is now active",
                    assigned_to=agent['id'],
                    created_by=self.agent_id,
                    priority=5,  # Low priority notification
                    data={
                        'project_name': project_name,
                        'project_path': project_path,
                        'notification_type': 'project_focus_change'
                    }
                )
    
    def execute_ai_project_creation(self, project_path: str, project_info: Dict, ai_result: Dict):
        """Execute project creation based on AI analysis"""
        
        colored_print(f"   AGENT: Executing AI-generated project structure", Colors.BRIGHT_CYAN)
        
        # Create files based on AI recommendations
        files_to_create = self.parse_ai_project_output(ai_result.get('implementation', ''))
        
        for file_path, content in files_to_create.items():
            full_path = os.path.join(project_path, file_path)
            
            # Create directory if needed
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Generate content using AI for each file
            file_content = self.generate_universal_file_content(file_path, content, project_info)
            
            # Write file
            with open(full_path, 'w') as f:
                f.write(file_content)
                
            colored_print(f"   SUCCESS: Created: {file_path}", Colors.GREEN)
    
    def create_universal_fallback_structure(self, project_path: str, project_info: Dict):
        """Create basic universal project structure when AI unavailable"""
        
        colored_print(f"   INFO: Creating universal fallback structure", Colors.YELLOW)
        
        # Basic universal files
        basic_files = {
            "README.md": self.generate_universal_file_content("README.md", "", project_info),
            "package.json": self.generate_universal_file_content("package.json", "", project_info),
            "src/main.js": self.generate_universal_file_content("src/main.js", "", project_info),
            "src/style.css": self.generate_universal_file_content("src/style.css", "", project_info)
        }
        
        for file_path, content in basic_files.items():
            full_path = os.path.join(project_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)
            
            colored_print(f"   SUCCESS: Created: {file_path}", Colors.GREEN)
    
    def parse_ai_project_output(self, ai_output: str) -> Dict[str, str]:
        """Parse AI output to extract file structure"""
        
        # This would parse AI output to determine project structure
        # For now, return basic structure that AI can customize
        return {
            "README.md": "AI-generated README",
            "package.json": "AI-generated package configuration",
            "src/index.js": "AI-generated main entry point",
            "src/style.css": "AI-generated styles"
        }
    
    def generate_universal_file_content(self, file_path: str, base_content: str, project_info: Dict) -> str:
        """Generate file content using AI collaboration - completely universal"""
        
        # Use standardized AI input for file generation
        standardized_input = self.create_standardized_ai_input(
            operation_type="FILE_GENERATION",
            task_description=f"Generate content for file: {file_path}",
            context_type="FILE_CREATION",
            requirements=[
                f"File type: {file_path.split('.')[-1] if '.' in file_path else 'text'}",
                f"Project: {project_info.get('name', 'Project')}",
                f"Purpose: {base_content or 'Standard project file'}",
                "Must integrate with overall project structure and goals"
            ],
            constraints=[
                "Use appropriate syntax and conventions for file type",
                "Follow modern best practices",
                "Ensure compatibility with project requirements",
                "Make it production-ready and well-documented"
            ],
            expected_output="FILE_CONTENT",
            target_files=[file_path]
        )
        
        # Execute AI file generation
        ai_result = self.execute_standardized_ai_operation(standardized_input)
        
        if ai_result.get('status') == 'success':
            return ai_result.get('implementation', self.get_universal_fallback_content(file_path, project_info))
        
        return self.get_universal_fallback_content(file_path, project_info)
    
    def get_universal_fallback_content(self, file_path: str, project_info: Dict) -> str:
        """Get universal fallback content for any file type"""
        
        file_ext = file_path.split('.')[-1].lower() if '.' in file_path else ''
        project_name = project_info.get('name', 'Project')
        
        if file_ext == 'md':
            return f"# {project_name}\n\nUniversal project created with AI-powered multi-agent collaboration.\n\n## Setup\n\n1. Install dependencies\n2. Run the application\n\n## Features\n\nAI-generated features based on project requirements."
        
        elif file_ext == 'json':
            return f'{{\n  "name": "{project_name.lower()}",\n  "version": "1.0.0",\n  "description": "Universal project created with AI collaboration",\n  "main": "src/index.js",\n  "scripts": {{\n    "start": "echo \\"Please configure start script\\"",\n    "build": "echo \\"Please configure build script\\""\n  }}\n}}'
        
        elif file_ext in ['js', 'ts']:
            return f"// {project_name} - Universal AI-generated entry point\n\n// Main application logic\nconsole.log('{project_name} started with AI collaboration');\n\n// TODO: Implement main functionality based on project requirements"
        
        elif file_ext == 'css':
            return f"/* {project_name} - Universal AI-generated styles */\n\nbody {{\n  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;\n  margin: 0;\n  padding: 20px;\n  background: #f5f5f5;\n}}\n\n.container {{\n  max-width: 1200px;\n  margin: 0 auto;\n  background: white;\n  padding: 20px;\n  border-radius: 8px;\n  box-shadow: 0 2px 10px rgba(0,0,0,0.1);\n}}"
        
        else:
            return f"# {project_name}\n\nUniversal file created with AI-powered multi-agent collaboration.\nFile type: {file_ext or 'generic'}\nGenerated automatically based on project requirements."
    
    def create_react_structure(self, project_path: str, project_info: Dict):
        """Create React project structure"""
        import os
        
        # Create React directories
        directories = [
            "src",
            "src/components", 
            "src/styles",
            "src/utils",
            "public"
        ]
        
        for dir_path in directories:
            full_path = os.path.join(project_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
            colored_print(f"   FOLDER: Created: {dir_path}", Colors.GREEN)
        
        # Create basic files
        files_to_create = {
            "package.json": self.generate_react_package_json(project_info),
            "README.md": self.generate_readme(project_info),
            "public/index.html": self.generate_react_html(project_info),
            "src/index.js": self.generate_react_index_js(),
            "src/App.js": self.generate_react_app_js(project_info),
            "src/styles/App.css": self.generate_react_css(),
            "src/styles/index.css": "/* Global styles */"
        }
        
        # Create component files for specific components
        for component in project_info["components"]:
            if component in ["TimeDisplay", "DateDisplay", "WeekDisplay"]:
                component_file = f"src/components/{component}.js"
                files_to_create[component_file] = self.generate_react_component(component)
        
        # Write all files
        for file_path, content in files_to_create.items():
            full_file_path = os.path.join(project_path, file_path)
            with open(full_file_path, 'w') as f:
                f.write(content)
            colored_print(f"    Created: {file_path}", Colors.GREEN)
    
    def create_generic_structure(self, project_path: str, project_info: Dict):
        """Create generic project structure"""
        import os
        
        directories = ["src", "docs", "tests"]
        for dir_path in directories:
            full_path = os.path.join(project_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
            colored_print(f"   FOLDER: Created: {dir_path}", Colors.GREEN)
        
        # Create README
        readme_path = os.path.join(project_path, "README.md")
        with open(readme_path, 'w') as f:
            f.write(self.generate_readme(project_info))
        colored_print(f"    Created: README.md", Colors.GREEN)
    
    def list_created_files(self, project_path: str) -> List[str]:
        """List all files created in the project"""
        import os
        created_files = []
        
        for root, dirs, files in os.walk(project_path):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), project_path)
                created_files.append(rel_path)
        
        return created_files
    
    def generate_react_package_json(self, project_info: Dict) -> str:
        """Generate package.json using AI collaboration with project context"""
        
        # Get project context for AI model
        project_context = self.get_project_context_for_ai()
        
        prompt = f"""Generate a package.json file for a React project using full project context:

{project_context}

PROJECT REQUIREMENTS:
- Project name: {project_info['name']}
- Framework: React.js
- Required features: {', '.join(project_info.get('components', []))}
- Project description: {project_info.get('description', 'React application')}

Please generate a complete, modern package.json with appropriate dependencies, scripts, and configuration based on the project requirements and any existing project structure.

OUTPUT ONLY THE JSON CONTENT - NO EXPLANATIONS OR MARKDOWN FORMATTING."""
        
        # Try AI generation first
        ai_result = self.try_ai_implementation(prompt)
        if ai_result.get('status') == 'success':
            return ai_result.get('implementation', self._fallback_package_json(project_info))
        
        # Fallback to basic template if AI unavailable
        return self._fallback_package_json(project_info)
    
    def _fallback_package_json(self, project_info: Dict) -> str:
        """Fallback package.json when AI unavailable"""
        return f'''{{
  "name": "{project_info['name'].lower()}",
  "version": "0.1.0",
  "private": true,
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  }},
  "scripts": {{
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test"
  }}
}}'''
    
    def generate_readme(self, project_info: Dict) -> str:
        """Generate README.md using AI collaboration with project context"""
        
        # Get project context for AI model
        project_context = self.get_project_context_for_ai()
        
        prompt = f"""Generate a comprehensive README.md for this project using full project context:

{project_context}

PROJECT INFO:
- Name: {project_info['name']}
- Framework: {project_info.get('framework', 'generic')}
- Components: {', '.join(project_info.get('components', []))}
- Description: {project_info.get('description', 'Application created with AI-powered multi-agent collaboration')}

Create a detailed README.md that includes:
1. Project description and purpose
2. Installation and setup instructions
3. Usage examples
4. Project structure explanation
5. Features and components overview
6. Development guides

Make it comprehensive and professional, tailored to this specific project's needs and structure.

OUTPUT ONLY THE MARKDOWN CONTENT - NO CODE BLOCKS OR EXPLANATIONS."""
        
        # Try AI generation first
        ai_result = self.try_ai_implementation(prompt)
        if ai_result.get('status') == 'success':
            return ai_result.get('implementation', self._fallback_readme(project_info))
        
        # Fallback to basic template if AI unavailable
        return self._fallback_readme(project_info)
    
    def _fallback_readme(self, project_info: Dict) -> str:
        """Fallback README when AI unavailable"""
        return f'''# {project_info['name']}

A {project_info.get('framework', 'generic')} application created using AI-powered Project_Process collaboration.

## Features
{chr(10).join(f"- {component}" for component in project_info.get('components', []))}

## Setup
1. Install dependencies
2. Run the application
3. Open in browser

## Created with Project_Process Paradigm
Generated by Multi-Agent AI Collaboration - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
'''
    
    def generate_react_html(self, project_info: Dict) -> str:
        """Generate public/index.html using AI collaboration with project context"""
        
        # Get project context for AI model
        project_context = self.get_project_context_for_ai()
        
        prompt = f"""Generate an index.html file for a React application using full project context:

{project_context}

PROJECT REQUIREMENTS:
- Project name: {project_info['name']}
- React application HTML template
- Should be optimized for the specific project features and requirements
- Include appropriate meta tags, SEO considerations, and modern HTML5 structure

Create a professional, optimized index.html that serves as the entry point for this React application, considering the project's specific needs and features.

OUTPUT ONLY THE HTML CONTENT - NO EXPLANATIONS OR MARKDOWN FORMATTING."""
        
        # Try AI generation first
        ai_result = self.try_ai_implementation(prompt)
        if ai_result.get('status') == 'success':
            return ai_result.get('implementation', self._fallback_react_html(project_info))
        
        # Fallback to basic template if AI unavailable
        return self._fallback_react_html(project_info)
    
    def _fallback_react_html(self, project_info: Dict) -> str:
        """Fallback HTML when AI unavailable"""
        return f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="{project_info['name']} - Created with AI Project_Process" />
    <title>{project_info['name']}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>'''
    
    def generate_react_index_js(self) -> str:
        """Generate src/index.js using AI collaboration with project context"""
        
        # Get project context for AI model
        project_context = self.get_project_context_for_ai()
        
        prompt = f"""Generate a React index.js entry point using full project context:

{project_context}

REQUIREMENTS:
- React 18+ entry point file
- Should integrate with existing project structure and dependencies
- Include appropriate imports and setup based on project needs
- Consider any special requirements or configurations from the project context

Create an optimized index.js that serves as the proper entry point for this specific React application.

OUTPUT ONLY THE JAVASCRIPT CODE - NO EXPLANATIONS OR MARKDOWN FORMATTING."""
        
        # Try AI generation first
        ai_result = self.try_ai_implementation(prompt)
        if ai_result.get('status') == 'success':
            return ai_result.get('implementation', self._fallback_react_index_js())
        
        # Fallback to basic template if AI unavailable
        return self._fallback_react_index_js()
    
    def _fallback_react_index_js(self) -> str:
        """Fallback index.js when AI unavailable"""
        return '''import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);'''
    
    def generate_react_app_js(self, project_info: Dict) -> str:
        """Generate src/App.js using AI collaboration with project context"""
        
        # Get project context for AI model
        project_context = self.get_project_context_for_ai()
        
        prompt = f"""Generate a React App.js component using full project context:

{project_context}

PROJECT REQUIREMENTS:
- Main App component for: {project_info['name']}
- Required components: {', '.join(project_info.get('components', []))}
- Framework: {project_info.get('framework', 'React')}
- Should intelligently integrate all components based on project structure and needs
- Use modern React patterns and best practices
- Consider existing project architecture and styling approach

Create a comprehensive App.js that serves as the main component, intelligently organizing and presenting all project components.

OUTPUT ONLY THE JSX/JAVASCRIPT CODE - NO EXPLANATIONS OR MARKDOWN FORMATTING."""
        
        # Try AI generation first
        ai_result = self.try_ai_implementation(prompt)
        if ai_result.get('status') == 'success':
            return ai_result.get('implementation', self._fallback_react_app_js(project_info))
        
        # Fallback to basic template if AI unavailable
        return self._fallback_react_app_js(project_info)
    
    def _fallback_react_app_js(self, project_info: Dict) -> str:
        """Fallback App.js when AI unavailable"""
        imports = []
        components_jsx = []
        
        for component in project_info.get("components", []):
            imports.append(f"import {component} from './components/{component}';")
            components_jsx.append(f"        <{component} />")
        
        imports_str = chr(10).join(imports)
        components_str = chr(10).join(components_jsx)
        
        return f'''import React from 'react';
import './styles/App.css';
{imports_str}

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>{project_info['name']}</h1>
        <p>AI-Powered Project_Process Application</p>
      </header>
      <main className="App-main">
{components_str}
      </main>
    </div>
  );
}}

export default App;'''
    
    def generate_react_css(self) -> str:
        """Generate CSS using AI collaboration with project context"""
        
        # Get project context for AI model
        project_context = self.get_project_context_for_ai()
        
        prompt = f"""Generate modern CSS styling for a React application using full project context:

{project_context}

REQUIREMENTS:
- Modern, professional CSS styling
- Responsive design principles
- Should complement the project's components and structure
- Consider the project's theme and purpose based on context
- Include styling for all components mentioned in the project
- Use modern CSS features (flexbox, grid, CSS variables, etc.)

Create comprehensive, professional CSS that enhances the user experience and visual appeal of this specific application.

OUTPUT ONLY THE CSS CONTENT - NO EXPLANATIONS OR MARKDOWN FORMATTING."""
        
        # Try AI generation first
        ai_result = self.try_ai_implementation(prompt)
        if ai_result.get('status') == 'success':
            return ai_result.get('implementation', self._fallback_react_css())
        
        # Fallback to basic template if AI unavailable
        return self._fallback_react_css()
    
    def _fallback_react_css(self) -> str:
        """Fallback CSS when AI unavailable"""
        return '''.App {
  text-align: center;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.App-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  color: white;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.App-main {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.component {
  margin: 20px;
  padding: 15px;
  border-radius: 12px;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s ease;
}

.component:hover {
  transform: translateY(-2px);
}'''
    
    def generate_react_component(self, component_name: str) -> str:
        """Generate React component using AI collaboration with project context"""
        
        # Get project context for AI model
        project_context = self.get_project_context_for_ai()
        
        prompt = f"""Generate a React component using full project context:

{project_context}

COMPONENT REQUIREMENTS:
- Component name: {component_name}
- Should integrate seamlessly with existing project structure
- Use modern React patterns (hooks, functional components)
- Include appropriate styling and functionality based on component name
- Consider existing project dependencies and patterns

Analyze the project context and create a component that fits perfectly with the existing codebase, architecture, and design patterns.

OUTPUT ONLY THE JSX/JAVASCRIPT CODE - NO EXPLANATIONS OR MARKDOWN FORMATTING."""
        
        # Try AI generation first
        ai_result = self.try_ai_implementation(prompt)
        if ai_result.get('status') == 'success':
            return ai_result.get('implementation', self._fallback_react_component(component_name))
        
        # Fallback to basic template if AI unavailable
        return self._fallback_react_component(component_name)
    
    def _fallback_react_component(self, component_name: str) -> str:
        """Fallback React component when AI unavailable"""
        return f'''import React, {{ useState, useEffect }} from 'react';

const {component_name} = () => {{
  const [data, setData] = useState('');

  useEffect(() => {{
    // AI-generated component logic would go here
    const updateData = () => {{
      setData(new Date().toLocaleString());
    }};
    
    updateData();
    const interval = setInterval(updateData, 1000);
    
    return () => clearInterval(interval);
  }}, []);

  return (
    <div className="component {component_name.lower()}">
      <h3>{component_name}</h3>
      <p>{{data}}</p>
    </div>
  );
}};

export default {component_name};'''
    
    def handle_git_management_task(self, task: Dict) -> Dict:
        """Handle git management tasks"""
        return {"message": f"Git management task handled: {task['description']}"}
    
    def handle_research_task(self, task: Dict) -> Dict:
        """Handle research tasks"""
        return {"message": f"Research task completed: {task['description']}"}
    
    def handle_testing_task(self, task: Dict) -> Dict:
        """Handle testing tasks"""
        return {"message": f"Testing task completed: {task['description']}"}
    
    def handle_code_rewriter_task(self, task: Dict) -> Dict:
        """Handle code rewriting tasks from code reviewer reports"""
        
        description = task["description"]
        colored_print(f"CONFIG: CODE REWRITER: Processing code fixes", Colors.BRIGHT_CYAN)
        colored_print(f"   Task: {description}", Colors.CYAN)
        
        # Check if this is from a code review report
        if task.get("task_type") == "code_rewrite_from_review":
            return self.process_review_based_fixes(task)
        else:
            return self.process_general_rewrite_task(task)
    
    def process_review_based_fixes(self, task: Dict) -> Dict:
        """Process fixes based on structured code review report"""
        
        metadata = task.get("metadata", {})
        review_report = metadata.get("review_report", {})
        issues = review_report.get("issues", [])
        
        colored_print(f"   INFO: Processing {len(issues)} issues from code review", Colors.CYAN)
        
        fixed_issues = []
        failed_fixes = []
        
        # Process each issue systematically
        for i, issue in enumerate(issues, 1):
            colored_print(f"    Fixing issue {i}/{len(issues)}: {issue.get('severity', 'UNKNOWN')} - {issue.get('description', 'No description')}", Colors.YELLOW)
            
            fix_result = self.apply_single_issue_fix(issue, review_report)
            
            if fix_result.get("success"):
                fixed_issues.append(issue)
                colored_print(f"      SUCCESS: Fixed: {issue.get('file', 'unknown file')}", Colors.GREEN)
            else:
                failed_fixes.append(issue)
                colored_print(f"      ERROR: Failed: {fix_result.get('error', 'Unknown error')}", Colors.RED)
        
        # Summary
        total_fixes = len(fixed_issues)
        colored_print(f"   STATUS: REWRITE SUMMARY: {total_fixes}/{len(issues)} issues fixed", Colors.BRIGHT_GREEN)
        
        # Auto-delegate back to reviewer if critical issues remain
        if failed_fixes:
            self.request_review_follow_up(failed_fixes, task)
        
        return {
            "status": "completed",
            "total_issues": len(issues),
            "fixed_issues": total_fixes,
            "failed_fixes": len(failed_fixes),
            "fixed_details": fixed_issues,
            "failed_details": failed_fixes,
            "message": f"Code rewriter completed: {total_fixes}/{len(issues)} issues fixed"
        }
    
    def apply_single_issue_fix(self, issue: Dict, review_report: Dict) -> Dict:
        """Apply fix for a single code issue using AI collaboration"""
        
        file_path = issue.get("file", "")
        severity = issue.get("severity", "UNKNOWN")
        description = issue.get("description", "")
        suggested_fix = issue.get("suggested_fix", "")
        line_number = issue.get("line_number", 0)
        
        if not file_path or file_path not in self.project_process_files:
            return {"success": False, "error": f"File {file_path} not found in project"}
        
        # Get current file content
        current_content = self.project_process_files[file_path]["content"]
        
        # Create standardized AI input for specific fix
        standardized_input = self.create_standardized_ai_input(
            operation_type="ISSUE_FIX",
            task_description=f"Fix {severity} issue: {description}",
            context_type="CODE_REPAIR",
            requirements=[
                f"Fix specific issue: {description}",
                f"Target file: {file_path}",
                f"Line number: {line_number}" if line_number > 0 else "Locate issue in file",
                f"Suggested approach: {suggested_fix}" if suggested_fix else "Determine best fix approach",
                "Maintain all existing functionality",
                "Follow project coding standards"
            ],
            constraints=[
                "Make minimal necessary changes",
                "Preserve existing code structure where possible",
                "Ensure fix doesn't introduce new issues",
                "Test compatibility with existing code"
            ],
            expected_output="FIXED_FILE_CONTENT",
            target_files=[file_path],
            current_file_content=current_content
        )
        
        # Execute AI-powered issue fix
        ai_result = self.execute_standardized_ai_operation(standardized_input)
        
        if ai_result.get('status') == 'success':
            fixed_content = ai_result.get('implementation', '').strip()
            
            # Validate the fix
            if self.validate_fix(current_content, fixed_content, issue):
                # Apply the fix to the actual file
                success = self.apply_fix_to_file(file_path, fixed_content)
                return {"success": success, "fixed_content": fixed_content}
            else:
                return {"success": False, "error": "Fix validation failed"}
        else:
            return {"success": False, "error": "AI fix generation failed"}
    
    def validate_fix(self, original_content: str, fixed_content: str, issue: Dict) -> bool:
        """Validate that the fix is reasonable"""
        
        # Basic validation checks
        if not fixed_content or len(fixed_content) < len(original_content) * 0.5:
            return False
        
        # Check that fix addresses the issue type
        severity = issue.get("severity", "")
        description = issue.get("description", "").lower()
        
        # Add specific validation based on issue type
        if "todo" in description or "fixme" in description:
            return "TODO" not in fixed_content and "FIXME" not in fixed_content
        
        return True  # Basic validation passed
    
    def apply_fix_to_file(self, file_path: str, fixed_content: str) -> bool:
        """Apply the fixed content to the actual file"""
        
        try:
            full_path = self.project_process_files[file_path]["path"]
            
            # Backup original
            backup_path = f"{full_path}.backup"
            with open(full_path, 'r') as original:
                with open(backup_path, 'w') as backup:
                    backup.write(original.read())
            
            # Write fixed content
            with open(full_path, 'w') as f:
                f.write(fixed_content)
            
            # Update cached content
            self.project_process_files[file_path]["content"] = fixed_content
            
            colored_print(f"       Applied fix to {file_path} (backup: {backup_path})", Colors.GREEN)
            return True
            
        except Exception as e:
            colored_print(f"      ERROR: Error applying fix to {file_path}: {e}", Colors.RED)
            return False
    
    def request_review_follow_up(self, failed_fixes: list, original_task: Dict):
        """Request follow-up review for failed fixes"""
        
        colored_print(f"   PROCESS: Requesting review follow-up for {len(failed_fixes)} failed fixes", Colors.YELLOW)
        
        # Create follow-up task for code reviewer
        follow_up_description = f"Review {len(failed_fixes)} failed fixes from rewriter"
        
        self.comm.create_task(
            description=follow_up_description,
            task_type="review_follow_up",
            assigned_to="code_reviewer",
            priority="high",
            metadata={
                "failed_fixes": failed_fixes,
                "original_task_id": original_task.get("id"),
                "source_agent": self.agent_id
            }
        )
    
    def process_general_rewrite_task(self, task: Dict) -> Dict:
        """Process general rewrite tasks not from code review"""
        
        description = task["description"]
        
        # Use universal AI collaboration for general rewriting
        standardized_input = self.create_standardized_ai_input(
            operation_type="CODE_REWRITE",
            task_description=description,
            context_type="CODE_IMPROVEMENT",
            requirements=[
                "Improve code quality and maintainability",
                "Fix any obvious issues or bugs",
                "Optimize performance where possible",
                "Update to modern coding standards"
            ],
            constraints=[
                "Maintain all existing functionality",
                "Don't break existing integrations",
                "Follow project conventions",
                "Make targeted improvements"
            ],
            expected_output="IMPROVED_CODE"
        )
        
        ai_result = self.execute_standardized_ai_operation(standardized_input)
        
        if ai_result.get('status') == 'success':
            return {
                "status": "completed", 
                "improvements": ai_result.get('implementation', ''),
                "message": f"General code rewrite completed: {description}"
            }
        else:
            return {
                "status": "completed",
                "message": f"Code rewrite guidance provided for: {description}"
            }
    
    def handle_general_task(self, task: Dict) -> Dict:
        """Handle general tasks"""
        return {"message": f"General task handled: {task['description']}"}

    def kill_agent(self, agent_name: str):
        """Kill and remove a faulty agent"""
        colored_print(f"AGENT MANAGEMENT: Killing agent '{agent_name}'", Colors.BRIGHT_RED)
        
        # Find agent by name or ID
        agents = self.comm.get_active_agents()
        target_agent = None
        
        for agent in agents:
            if agent['id'] == agent_name or agent['role'] == agent_name:
                target_agent = agent
                break
        
        if not target_agent:
            colored_print(f"ERROR: Agent '{agent_name}' not found", Colors.RED)
            return
        
        # Kill the process
        killed = self.comm.kill_agent_by_pid(target_agent['id'])
        
        # Remove from registry
        self.comm.remove_agent(target_agent['id'])
        
        if killed:
            colored_print(f"SUCCESS: Agent '{agent_name}' killed and removed", Colors.GREEN)
        else:
            colored_print(f"WARNING: Agent '{agent_name}' removed from registry (process may have already stopped)", Colors.YELLOW)
    
    def restart_agent(self, agent_name: str):
        """Restart a specific agent"""
        colored_print(f"AGENT MANAGEMENT: Restarting agent '{agent_name}'", Colors.BRIGHT_YELLOW)
        
        # Find agent info
        agents = self.comm.get_active_agents()
        target_agent = None
        
        for agent in agents:
            if agent['id'] == agent_name or agent['role'] == agent_name:
                target_agent = agent
                break
        
        if not target_agent:
            colored_print(f"ERROR: Agent '{agent_name}' not found", Colors.RED)
            return
        
        # Kill existing process
        self.comm.kill_agent_by_pid(target_agent['id'])
        
        # Wait a moment
        import time
        time.sleep(1)
        
        # Spawn new instance
        role = target_agent['role']
        agent_id = target_agent['id']
        
        colored_print(f"RESTART: Spawning new instance of {role} agent", Colors.CYAN)
        success = self.spawn_single_agent(role, agent_id)
        
        if success:
            colored_print(f"SUCCESS: Agent '{agent_name}' restarted", Colors.GREEN)
        else:
            colored_print(f"ERROR: Failed to restart agent '{agent_name}'", Colors.RED)
    
    def show_agent_status(self, agent_name: str):
        """Show detailed status of a specific agent"""
        colored_print(f"AGENT STATUS: {agent_name}", Colors.BRIGHT_CYAN)
        
        # Find agent
        agents = self.comm.load_agents()
        target_agent = None
        
        for agent in agents:
            if agent['id'] == agent_name or agent['role'] == agent_name:
                target_agent = agent
                break
        
        if not target_agent:
            colored_print(f"ERROR: Agent '{agent_name}' not found", Colors.RED)
            return
        
        # Display status
        colored_print(f"   ID: {target_agent['id']}", Colors.WHITE)
        colored_print(f"   Role: {target_agent['role']}", Colors.WHITE)
        colored_print(f"   Status: {target_agent['status']}", 
                     Colors.GREEN if target_agent['status'] == 'active' else Colors.RED)
        colored_print(f"   PID: {target_agent.get('pid', 'unknown')}", Colors.WHITE)
        colored_print(f"   Last Seen: {target_agent.get('last_seen', 'unknown')}", Colors.WHITE)
        
        if target_agent.get('deactivated_at'):
            colored_print(f"   Deactivated: {target_agent['deactivated_at']}", Colors.YELLOW)
        
        # Check if process is actually running
        pid = target_agent.get('pid')
        if pid:
            try:
                os.kill(pid, 0)  # Signal 0 checks if process exists
                colored_print(f"   Process: RUNNING ✓", Colors.GREEN)
            except ProcessLookupError:
                colored_print(f"   Process: NOT RUNNING ✗", Colors.RED)
            except PermissionError:
                colored_print(f"   Process: EXISTS (no permission to check)", Colors.YELLOW)
        
        # Show pending tasks
        if target_agent['status'] == 'active':
            tasks = self.comm.get_pending_tasks(target_agent['id'])
            colored_print(f"   Pending Tasks: {len(tasks)}", Colors.CYAN)
            if tasks:
                for task in tasks[:3]:  # Show first 3 tasks
                    print(f"      • {task['id']}: {task['description'][:50]}...")
    
    def spawn_new_agent(self, role: str, name: str):
        """Spawn a new agent with specified role and name"""
        colored_print(f"AGENT MANAGEMENT: Spawning new agent '{name}' with role '{role}'", Colors.BRIGHT_GREEN)
        
        # Validate role
        valid_roles = ['coordinator', 'file_manager', 'coder', 'code_reviewer', 'code_rewriter', 'git_manager', 'researcher', 'tester']
        if role not in valid_roles:
            colored_print(f"ERROR: Invalid role '{role}'. Valid roles: {', '.join(valid_roles)}", Colors.RED)
            return
        
        # Check if agent already exists
        agents = self.comm.get_active_agents()
        if any(agent['id'] == name for agent in agents):
            colored_print(f"ERROR: Agent '{name}' already exists", Colors.RED)
            return
        
        # Spawn the agent
        success = self.spawn_single_agent(role, name)
        
        if success:
            colored_print(f"SUCCESS: Agent '{name}' ({role}) spawned successfully", Colors.GREEN)
        else:
            colored_print(f"ERROR: Failed to spawn agent '{name}'", Colors.RED)
    
    def cleanup_inactive_agents(self):
        """Remove all inactive agents from the registry"""
        colored_print("AGENT MANAGEMENT: Cleaning up inactive agents", Colors.BRIGHT_YELLOW)
        
        agents = self.comm.load_agents()
        active_count = len([a for a in agents if a['status'] == 'active'])
        inactive_agents = [a for a in agents if a['status'] != 'active']
        
        if not inactive_agents:
            colored_print("INFO: No inactive agents found", Colors.GREEN)
            return
        
        colored_print(f"FOUND: {len(inactive_agents)} inactive agents to remove", Colors.YELLOW)
        
        # Keep only active agents
        active_agents = [a for a in agents if a['status'] == 'active']
        self.comm.save_agents(active_agents)
        
        colored_print(f"SUCCESS: Removed {len(inactive_agents)} inactive agents", Colors.GREEN)
        colored_print(f"ACTIVE: {active_count} agents remain active", Colors.CYAN)

def main():
    if len(sys.argv) != 3:
        print("Usage: python multi_agent_terminal.py <agent_id> <role>")
        print("Roles: coordinator, coder, code_reviewer, code_rewriter, file_manager, git_manager, researcher, tester")
        return
    
    agent_id = sys.argv[1]
    role_str = sys.argv[2].upper()
    
    try:
        role = AgentRole[role_str]
    except KeyError:
        print(f"Invalid role: {role_str}")
        print("Valid roles:", [r.name for r in AgentRole])
        return
    
    # Create agent
    agent = MultiAgentTerminal(agent_id, role)
    
    # Show guided welcome for coordinator in guided mode
    if agent.guided_mode and role == AgentRole.COORDINATOR:
        agent.show_guided_welcome()
    else:
        colored_print(f"\n=== Multi-Agent Terminal ({agent_id}) ===", Colors.BRIGHT_YELLOW)
        colored_print(f"Role: {role.value}", Colors.CYAN)
        colored_print(f"Workspace: {agent.workspace_dir}", Colors.CYAN)
        colored_print("Commands: 'help', 'agents', 'tasks', 'delegate \"description\" to agent', 'quit'", Colors.WHITE)
        colored_print("=" * 50, Colors.BRIGHT_YELLOW)
    
    try:
        while True:
            try:
                # Use different prompt for guided mode
                if agent.guided_mode and role == AgentRole.COORDINATOR:
                    user_input = input(colored_text("\nWhat would you like to do? ", Colors.BRIGHT_CYAN)).strip()
                else:
                    user_input = input(f"\n[{agent_id}]> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                    
                # Handle guided commands for coordinator, then fall through to standard commands
                if agent.guided_mode and role == AgentRole.COORDINATOR:
                    if agent.handle_guided_command(user_input):
                        continue  # Command was handled in guided mode
                    # If not handled in guided mode, fall through to standard commands
                
                if user_input.lower() == 'help':
                    print("Available commands:")
                    print("  agents - Show active agents")
                    print("  tasks - Show pending tasks")
                    print("  delegate \"description\" to agent_name - Create task for specific agent")
                    print("  delegate description - Create task for coder (default)")
                    print("  project - Show current project process")
                    print("  set_project <name> - Set focus to specific project process")
                    print("  files - Show project files loaded for AI collaboration")
                    print()
                    if role == AgentRole.COORDINATOR:
                        colored_print("Coordinator Commands:", Colors.BRIGHT_CYAN)
                        print("  workspace - Show workspace information")
                        print("  set_workspace <path> - Set workspace directory")
                        print("  stats - Show delegation statistics")
                        print("  workflows - Show active workflows")
                        print()
                    colored_print("Agent Management Commands:", Colors.BRIGHT_YELLOW)
                    print("  kill <agent_name> - Kill and remove a faulty agent")
                    print("  restart <agent_name> - Restart a specific agent")
                    print("  status <agent_name> - Check status of specific agent")
                    print("  spawn <role> <name> - Create new agent with role and name")
                    print("  cleanup - Remove all inactive agents")
                    print()
                    print("  quit - Exit the terminal")
                elif user_input.lower() == 'agents':
                    agents = agent.comm.get_active_agents()
                    colored_print(f"\nActive Agents ({len(agents)}):", Colors.BRIGHT_CYAN)
                    for a in agents:
                        print(f"  {a['id']} ({a['role']}) - PID: {a.get('pid', 'unknown')}")
                elif user_input.lower() == 'tasks':
                    tasks = agent.comm.get_pending_tasks(agent_id)
                    colored_print(f"\nPending Tasks ({len(tasks)}):", Colors.BRIGHT_CYAN)
                    for t in tasks:
                        print(f"  {t['id']}: {t['description']}")
                elif user_input.lower() == 'project':
                    if agent.current_project_process:
                        colored_print(f"\nTARGET: Current Project Process: {agent.current_project_process}", Colors.BRIGHT_GREEN)
                        colored_print(f"FOLDER: Workspace: {agent.project_process_workspace}", Colors.GREEN)
                        colored_print(f"FILES: Files loaded: {len(agent.project_process_files)}", Colors.CYAN)
                    else:
                        colored_print("FOLDER: No active project process", Colors.YELLOW)
                        agent.detect_active_project_process()
                elif user_input.lower().startswith('set_project '):
                    project_name = user_input[12:].strip()
                    agent.set_project_process(project_name)
                elif user_input.lower() == 'files':
                    if agent.current_project_process:
                        colored_print(f"\nFILES: Project Files for {agent.current_project_process}:", Colors.BRIGHT_CYAN)
                        for relative_path, file_info in agent.project_process_files.items():
                            size_kb = file_info['size'] / 1024
                            print(f"  {relative_path} ({size_kb:.1f} KB)")
                    else:
                        colored_print("FOLDER: No active project process", Colors.YELLOW)
                # Agent Management Commands
                elif user_input.lower().startswith('kill '):
                    agent_name = user_input[5:].strip()
                    agent.kill_agent(agent_name)
                elif user_input.lower().startswith('restart '):
                    agent_name = user_input[8:].strip()
                    agent.restart_agent(agent_name)
                elif user_input.lower().startswith('status '):
                    agent_name = user_input[7:].strip()
                    agent.show_agent_status(agent_name)
                elif user_input.lower().startswith('spawn '):
                    parts = user_input[6:].strip().split()
                    if len(parts) >= 2:
                        role = parts[0]
                        name = parts[1]
                        agent.spawn_new_agent(role, name)
                    else:
                        colored_print("Usage: spawn <role> <name>", Colors.RED)
                elif user_input.lower() == 'cleanup':
                    agent.cleanup_inactive_agents()
                # Coordinator-specific commands (when using refactored coordinator)
                elif user_input.lower() == 'workspace':
                    # Show workspace information
                    if role == AgentRole.COORDINATOR:
                        try:
                            from src.agents import CoordinatorAgent
                            coord = CoordinatorAgent(agent_id, agent.workspace_dir)
                            coord.show_workspace_info()
                        except Exception as e:
                            colored_print(f"Workspace: {agent.workspace_dir}", Colors.CYAN)
                            colored_print(f"Status: {'Exists' if os.path.exists(agent.workspace_dir) else 'Not found'}", Colors.WHITE)
                    else:
                        colored_print(f"Workspace: {agent.workspace_dir}", Colors.CYAN)
                elif user_input.lower().startswith('set_workspace '):
                    # Set workspace directory
                    if role == AgentRole.COORDINATOR:
                        new_workspace = user_input[14:].strip()
                        # Expand ~ to home directory
                        new_workspace = os.path.expanduser(new_workspace)
                        new_workspace = os.path.abspath(new_workspace)
                        
                        try:
                            from src.agents import CoordinatorAgent
                            coord = CoordinatorAgent(agent_id, agent.workspace_dir)
                            success = coord.set_workspace(new_workspace)
                            if success:
                                agent.workspace_dir = new_workspace
                                agent.comm = AgentCommunication(new_workspace)
                        except Exception as e:
                            # Fallback implementation
                            if not os.path.exists(new_workspace):
                                os.makedirs(new_workspace, exist_ok=True)
                                colored_print(f"Created workspace directory: {new_workspace}", Colors.GREEN)
                            agent.workspace_dir = new_workspace
                            agent.comm = AgentCommunication(new_workspace)
                            colored_print(f"Workspace updated to: {new_workspace}", Colors.GREEN)
                    else:
                        colored_print("set_workspace command is only available for coordinator role", Colors.YELLOW)
                elif user_input.lower() == 'stats':
                    # Show delegation statistics (coordinator only)
                    if role == AgentRole.COORDINATOR:
                        try:
                            from src.agents import CoordinatorAgent
                            coord = CoordinatorAgent(agent_id, agent.workspace_dir)
                            stats = coord.get_delegation_statistics()
                            colored_print("\nDelegation Statistics:", Colors.BRIGHT_CYAN)
                            colored_print(f"  Total delegations: {stats['total_delegations']}", Colors.WHITE)
                            colored_print(f"  Successful: {stats['successful_delegations']}", Colors.GREEN)
                            colored_print(f"  Success rate: {stats['success_rate']:.1%}", Colors.CYAN)
                            colored_print(f"  Active workflows: {stats['active_workflows']}", Colors.YELLOW)
                        except Exception as e:
                            colored_print(f"Stats not available: {e}", Colors.YELLOW)
                    else:
                        colored_print("stats command is only available for coordinator role", Colors.YELLOW)
                elif user_input.lower() == 'workflows':
                    # Show active workflows (coordinator only)
                    if role == AgentRole.COORDINATOR:
                        try:
                            from src.agents import CoordinatorAgent
                            coord = CoordinatorAgent(agent_id, agent.workspace_dir)
                            workflows = coord.list_active_workflows()
                            if workflows:
                                colored_print("\nActive Workflows:", Colors.BRIGHT_CYAN)
                                for wf in workflows:
                                    colored_print(f"  [{wf['workflow_id']}] {wf['original_task']}", Colors.CYAN)
                                    colored_print(f"    Steps: {wf['total_steps']} | Status: {wf['status']}", Colors.WHITE)
                            else:
                                colored_print("No active workflows", Colors.YELLOW)
                        except Exception as e:
                            colored_print(f"Workflows not available: {e}", Colors.YELLOW)
                    else:
                        colored_print("workflows command is only available for coordinator role", Colors.YELLOW)
                elif user_input.lower().startswith('delegate '):
                    # Parse delegation command: delegate "description" to agent_name
                    command_part = user_input[9:].strip()
                    
                    if ' to ' in command_part:
                        # Parse: "description" to agent_name
                        parts = command_part.split(' to ')
                        if len(parts) == 2:
                            description = parts[0].strip().strip('"')
                            target_agent = parts[1].strip()
                            
                            # Map role names and agent names to actual role values for assignment
                            role_mapping = {
                                'file_manager': 'file_manager',
                                'files': 'files',  # Agent name -> agent ID
                                'coder': 'coder',
                                'dev': 'dev',      # Agent name -> agent ID
                                'code_reviewer': 'code_reviewer', 
                                'reviewer': 'reviewer',  # Agent name -> agent ID
                                'code_rewriter': 'code_rewriter',
                                'fixer': 'fixer',  # Agent name -> agent ID
                                'git_manager': 'git_manager',
                                'git': 'git',      # Agent name -> agent ID
                                'researcher': 'researcher',
                                'tester': 'tester',
                                'main': 'main'     # Coordinator agent name
                            }
                            
                            assigned_to = role_mapping.get(target_agent, target_agent)
                            
                            task_id = agent.comm.create_task(
                                task_type="general",
                                description=description,
                                assigned_to=assigned_to,
                                created_by=agent_id
                            )
                            colored_print(f"Task {task_id} created and delegated to {target_agent}!", Colors.GREEN)
                        else:
                            colored_print("Invalid format. Use: delegate \"description\" to agent_name", Colors.RED)
                    else:
                        # Old format: just delegate description (default to coder)
                        description = command_part
                        if description:
                            task_id = agent.comm.create_task(
                                task_type="general",
                                description=description,
                                assigned_to="coder",  # Default to coder
                                created_by=agent_id
                            )
                            colored_print(f"Task {task_id} created and delegated to coder!", Colors.GREEN)
                        else:
                            colored_print("Please provide a task description", Colors.RED)
                else:
                    colored_print(f"Unknown command: {user_input}", Colors.RED)
                    
            except KeyboardInterrupt:
                print()
                break
            except EOFError:
                break
    
    finally:
        agent.running = False
        agent.save_history()
        colored_print(f"\nAgent {agent_id} shutting down...", Colors.YELLOW)

if __name__ == "__main__":
    main()
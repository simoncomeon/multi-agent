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

        # Background job monitoring for heavy scaffold commands
        # - self.bg_jobs: list of dicts {pid, command, log, project_dir, predicted_app_dir, start_time}
        # - self.deferred_cmds: map of project_dir -> [commands]
        self.bg_jobs = []
        self.deferred_cmds = {}
        self.bg_monitor_thread = threading.Thread(target=self.monitor_background_jobs, daemon=True)
        self.bg_monitor_thread.start()

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
        
        # IMPORTANT: Create project as subdirectory but keep workspace at parent level
        # This ensures all agents communicate through the same .agent_comm directory
        project_path = os.path.join(self.workspace_dir, project_name)
        
        colored_print(f"Creating project at: {project_path}", Colors.CYAN)
        
        # Create the project directory
        os.makedirs(project_path, exist_ok=True)
        
        # Set this project as the active project process (but don't change workspace)
        self.set_project_process(project_name)
        
        # Ensure core agents exist (file manager and coder)
        agents = self.comm.get_active_agents()
        file_manager_exists = any(agent['role'] == 'file_manager' for agent in agents)
        coder_exists = any(agent['role'] == 'coder' for agent in agents)
        
        if not file_manager_exists:
            colored_print("Spawning file manager agent...", Colors.CYAN)
            self.spawn_single_agent('file_manager', 'files')
            # Give it a moment to register
            import time
            time.sleep(2)
        if not coder_exists:
            colored_print("Spawning coder agent...", Colors.CYAN)
            self.spawn_single_agent('coder', 'dev')
            import time
            time.sleep(2)
        
        # Build a high-level request and let coordinator (this agent) enrich and split into sub-tasks
        base_request = f"Create {project_type} project '{project_name}' - {description}"
        delegated = self.split_and_delegate_enriched_task(
            base_request,
            project_name,
            project_path
        )
        
        colored_print(f"SUCCESS: Project created at {project_path}", Colors.BRIGHT_GREEN)
        colored_print(f"SUCCESS: Active project set to '{project_name}'", Colors.BRIGHT_GREEN)
        colored_print(f"SUCCESS: Delegated {len(delegated)} task(s) from enriched plan", Colors.BRIGHT_GREEN)
        colored_print(f"TIP: Use 'project' to see project details", Colors.CYAN)
        colored_print(f"TIP: Use 'tasks' command to monitor progress", Colors.CYAN)

    def split_and_delegate_enriched_task(self, description: str, project_name: Optional[str] = None, project_path: Optional[str] = None) -> list:
        """Enrich a high-level description, parse structured plan, and delegate to proper agents."""
        # Enrich with AI first
        enriched = self.enrich_task_description(description, 'file_manager')

        # Ensure project context
        if not project_name and hasattr(self, 'current_project_process') and self.current_project_process:
            project_name = self.current_project_process
        if not project_path and hasattr(self, 'project_process_workspace') and self.project_process_workspace:
            project_path = self.project_process_workspace

        task_ids = []
        task_data_base = {
            'project_name': project_name,
            'project_workspace': project_path
        }

        # Build a structured payload for file manager
        fm_payload = {
            'steps': [],
            'tools': enriched.get('tools', []),
            'best_practices': {bp: True for bp in (enriched.get('best_practices') or [])},
            'project_structure': {},
            'files': enriched.get('required_files', [])
        }

        # If AI returned only enhanced text, try to extract commands/files heuristically
        if (not fm_payload['tools'] or not fm_payload['files']) and enriched.get('was_enhanced'):
            enhanced_text = enriched.get('enhanced_description') or ''
            if isinstance(enhanced_text, str) and enhanced_text:
                extracted = self._extract_plan_from_text(enhanced_text)
                if extracted.get('tools'):
                    fm_payload['tools'] = list({*fm_payload['tools'], *extracted['tools']})
                if extracted.get('files'):
                    fm_payload['files'] = list({*fm_payload['files'], *extracted['files']})
                if extracted.get('steps'):
                    fm_payload['steps'].extend(extracted['steps'])

        # Heuristic steps from tools and context
        if project_path:
            fm_payload['steps'].append(f"Open terminal and navigate to {project_path}")
        for tool in fm_payload['tools']:
            t = tool.lower()
            if 'create-react-app' in t:
                fm_payload['steps'].append(f"Run npx create-react-app {project_name.lower().replace(' ', '-')}")
            elif t.startswith('npm '):
                fm_payload['steps'].append(tool)
            elif t.startswith('pip'):
                fm_payload['steps'].append(tool)

        # Prefer sending structured dict to file manager to avoid dumping raw text
        fm_task_id = self.comm.create_task(
            task_type='file_management',
            description=fm_payload,  # structured dict; file_manager can handle it
            assigned_to='files',
            created_by=self.agent_id,
            priority=1,
            data={**task_data_base, 'execute_commands': True}
        )
        task_ids.append(fm_task_id)

        # Create a coder task to implement core files if any were listed
        req_files = enriched.get('required_files') or []
        if req_files:
            code_desc = f"Implement core files and components for project '{project_name}': {', '.join(req_files[:6])}"
            coder_task_id = self.comm.create_task(
                task_type='code_generation',
                description=code_desc,
                assigned_to='dev',
                created_by=self.agent_id,
                priority=1,
                data=task_data_base.copy()
            )
            task_ids.append(coder_task_id)

        return task_ids

    def _extract_plan_from_text(self, text: str) -> Dict[str, list]:
        """Extract a minimal plan from free-form AI text: commands, files, steps."""
        import re
        steps, tools, files = [], [], []

        # Commands: lines starting with $, Run ..., or starting with known tools
        for line in text.splitlines():
            s = line.strip()
            if not s:
                continue
            if s.startswith('$'):
                s = s[1:].strip()
            if s.lower().startswith('run '):
                s = s[4:].strip()
            if re.match(r'^(npx|npm|yarn|pnpm|pip3?|python3? -m pip)\b', s, re.I):
                tools.append(s)
                steps.append(f"Run {s}")

        # Files: look for path-like tokens with common extensions
        path_pattern = re.compile(r"(?:^|\s)([\w./-]+\.(?:js|jsx|ts|tsx|json|html|css|md|py))\b")
        for m in path_pattern.finditer(text):
            files.append(m.group(1))

        # Also include common config files mentioned
        for key in ["package.json", "requirements.txt", "pyproject.toml", "vite.config.ts", "vite.config.js", "public/index.html", "src/index.js", "src/App.js"]:
            if key in text and key not in files:
                files.append(key)

        # De-duplicate while preserving order
        def dedupe(seq):
            seen = set()
            out = []
            for x in seq:
                if x not in seen:
                    out.append(x)
                    seen.add(x)
            return out

        return {
            'steps': dedupe(steps),
            'tools': dedupe(tools),
            'files': dedupe(files)
        }
        
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
        
        # IMPORTANT: Apply project context from coordinator before processing
        self._apply_project_context(task)
        
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
        finally:
            # Clear temporary workspace after task
            self.temp_workspace = None
            self.temp_project = None
    
    def _extract_project_context_from_task(self, task: Dict) -> tuple:
        """
        Extract project workspace context from task data.
        Returns: (project_workspace_path, project_name) or (None, None)
        """
        task_data = task.get('data', {})
        
        if 'project_workspace' in task_data and 'project_name' in task_data:
            project_workspace = task_data['project_workspace']
            project_name = task_data['project_name']
            colored_print(f"INFO: Using project context from coordinator - {project_name} at {project_workspace}", Colors.CYAN)
            return project_workspace, project_name
        
        return None, None
    
    def _apply_project_context(self, task: Dict):
        """
        Apply project context from task to this agent's working directory.
        This ensures agents work in the correct project directory.
        """
        project_workspace, project_name = self._extract_project_context_from_task(task)
        
        if project_workspace and project_name:
            # Temporarily set workspace for this task
            self.temp_workspace = project_workspace
            self.temp_project = project_name
            return True
        
        # No project context provided, use current workspace
        self.temp_workspace = str(self.workspace_dir)
        self.temp_project = None
        return False
    
    def _get_working_directory(self) -> str:
        """Get the current working directory for file operations"""
        # Use temporary workspace if set (from task context)
        if hasattr(self, 'temp_workspace') and self.temp_workspace:
            return self.temp_workspace
        
        # Fall back to project process workspace if available
        if hasattr(self, 'project_process_workspace') and self.project_process_workspace:
            return str(self.project_process_workspace)
        
        # Default to base workspace
        return str(self.workspace_dir)
    
    def handle_code_generation_task(self, task: Dict) -> Dict:
        """Handle code generation using AI-first approach with collaborative fallback"""
        # Get the correct working directory from project context
        working_dir = self._get_working_directory()
        colored_print(f"CODE GENERATION: Operating in directory: {working_dir}", Colors.CYAN)
        
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
        
        # Get the correct working directory from project context
        working_dir = self._get_working_directory()
        
        description = task["description"]
        colored_print(f"INFO: CODE REVIEWER: Conducting comprehensive code review", Colors.BRIGHT_CYAN)
        colored_print(f"   Task: {description}", Colors.CYAN)
        colored_print(f"   Working Directory: {working_dir}", Colors.CYAN)
        
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
        
        # NEW: If description is a structured dict plan, handle it directly
        if isinstance(description, dict):
            return self.handle_structured_file_plan(task)
        
        # Check if this is an edit task or create task
        if self.is_edit_task(description):
            return self.handle_file_edit_task(description)
        else:
            return self.handle_file_create_task(task)
    
    def is_edit_task(self, description: str) -> bool:
        """Determine if this is an edit task or create task"""
        edit_keywords = ["edit", "modify", "update", "change", "add to", "enhance", "improve"]
        if not isinstance(description, str):
            return False
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
        
        # PRIORITY 1: Use project workspace from coordinator (task context)
        working_dir = self._get_working_directory()
        if working_dir != str(self.workspace_dir):
            # We have a specific project workspace from the coordinator
            project_name = os.path.basename(working_dir)
            if os.path.exists(working_dir):
                colored_print(f"   COORDINATOR: Using project workspace from coordinator - '{project_name}'", Colors.BRIGHT_GREEN)
                return {
                    "name": project_name,
                    "path": working_dir,
                    "source": "coordinator_context"
                }
        
        # PRIORITY 2: Use current project if already set
        if hasattr(self, 'current_project_process') and self.current_project_process:
            current_path = os.path.join(self.workspace_dir, self.current_project_process)
            if os.path.exists(current_path):
                colored_print(f"   CURRENT: Using active project '{self.current_project_process}'", Colors.BRIGHT_GREEN)
                return {
                    "name": self.current_project_process,
                    "path": current_path,
                    "source": "current_project"
                }
        
        # PRIORITY 3: Look for project name in task data
        if task_data and 'project_name' in task_data:
            project_name = task_data['project_name']
            # Check if project_workspace is also provided (full path)
            if 'project_workspace' in task_data:
                project_path = task_data['project_workspace']
            else:
                project_path = os.path.join(self.workspace_dir, project_name)
            
            if os.path.exists(project_path):
                colored_print(f"   TASK_DATA: Found project '{project_name}' from task data", Colors.BRIGHT_GREEN)
                return {
                    "name": project_name,
                    "path": project_path,
                    "source": "task_data"
                }
        
        # PRIORITY 4: Scan all existing projects in workspace
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
        desc_lower = task_description.lower() if isinstance(task_description, str) else ""
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
        
        desc_lower = description.lower() if isinstance(description, str) else ""
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
        """Create component files by parsing AI output only (no hard-coded templates)."""
        import os
        files_created = []

        try:
            implementation = ai_result.get('implementation', '') if isinstance(ai_result, dict) else ''

            # 1) Try to parse files directly from the provided AI implementation
            files_payload = self._parse_ai_files_payload(implementation)

            # 2) If nothing parsed, request a STRICT JSON files payload from AI
            if not files_payload:
                project_context = self.get_project_structure_context(project_path)
                strict_input = self.create_standardized_ai_input(
                    operation_type="COMPONENT_CREATION_FILES",
                    task_description=(
                        f"Generate all necessary files to add component {component_info.get('name')} "
                        f"(type: {component_info.get('type')}) with features: "
                        f"{', '.join(component_info.get('features', []))}."
                    ),
                    context_type="EXISTING_PROJECT_ENHANCEMENT",
                    requirements=[
                        "Return STRICT JSON only",
                        "JSON schema: {\"files\":[{\"path\":string,\"content\":string}]}",
                        f"Place files under {component_info.get('target_dir', 'src/components')} if appropriate",
                        "Use project conventions from context (framework, structure, imports)",
                    ],
                    constraints=[
                        "No explanations, no markdown, no backticks",
                        "Absolute or project-relative POSIX paths only",
                        "Ensure content compiles in the detected framework",
                    ],
                    expected_output="STRICT_JSON_FILES",
                    project_context=project_context
                )

                strict_result = self.execute_standardized_ai_operation(strict_input)
                strict_impl = strict_result.get('implementation', '') if isinstance(strict_result, dict) else ''
                files_payload = self._parse_ai_files_payload(strict_impl)

            # 3) Write files to disk
            if files_payload:
                for f in files_payload:
                    rel_path = f.get('path')
                    content = f.get('content', '')
                    if not rel_path or not isinstance(rel_path, str):
                        continue
                    fpath = os.path.join(project_path, rel_path)
                    os.makedirs(os.path.dirname(fpath), exist_ok=True)
                    with open(fpath, 'w', encoding='utf-8') as out:
                        out.write(content)
                    files_created.append(fpath)
                    colored_print(f"      Created: {os.path.relpath(fpath, project_path)}", Colors.GREEN)
            else:
                colored_print("   WARNING: AI did not return a parsable files payload. No files created.", Colors.YELLOW)

        except Exception as e:
            colored_print(f"   ERROR: Failed to create AI component from parsed output: {e}", Colors.RED)

        return files_created
    
    # NOTE: Removed fallback hard-coded component generation. AI-only path is used.
    
    # NOTE: Removed hard-coded JSX feature generation.

    # NEW: Structured file plan handler for file_manager
    def handle_structured_file_plan(self, task: Dict) -> Dict:
        """Handle a structured file plan dict with steps/tools/project_structure/files."""
        plan = task.get('description', {})
        data = task.get('data', {})
        
        # Determine project directory
        project_dir = None
        if 'project_workspace' in data and data['project_workspace']:
            project_dir = data['project_workspace']
        elif hasattr(self, 'project_process_workspace') and self.project_process_workspace:
            project_dir = self.project_process_workspace
        else:
            # Fallback to base workspace + project name
            pname = data.get('project_name') or 'NewProject'
            project_dir = os.path.join(self.workspace_dir, pname)
        
        os.makedirs(project_dir, exist_ok=True)
        colored_print(f"   Target: {project_dir}", Colors.CYAN)
        
        created_files = []
        created_dirs = []
        
        # Create directory structure
        struct = plan.get('project_structure')
        if isinstance(struct, dict):
            def create_tree(base_path, tree):
                for name, subtree in tree.items():
                    dir_path = os.path.join(base_path, name)
                    os.makedirs(dir_path, exist_ok=True)
                    created_dirs.append(dir_path)
                    if isinstance(subtree, dict):
                        create_tree(dir_path, subtree)
            create_tree(project_dir, struct)
        
        # Create listed files using AI-only content generation (no hard-coded templates)
        files = plan.get('files') or []
        project_info_for_ai = {"name": data.get('project_name') or os.path.basename(project_dir)}
        project_struct_context = self.get_project_structure_context(project_dir)
        for rel in files:
            if not isinstance(rel, str):
                continue
            fpath = os.path.join(project_dir, rel)
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
            # Ask AI for file content using universal generator
            content = self.generate_universal_file_content(rel, "", project_info_for_ai)
            with open(fpath, 'w', encoding='utf-8') as f:
                if content:
                    f.write(content)
            created_files.append(fpath)
            colored_print(f"      Created: {os.path.relpath(fpath, project_dir)}", Colors.GREEN)
        
        # Show suggested commands
        steps = plan.get('steps') or []
        commands = []
        for step in steps:
            if not isinstance(step, str):
                continue
            s = step.strip()
            if s.startswith('$'):
                s = s[1:].strip()
            if s.lower().startswith('run '):
                s = s[4:].strip()
            if any(s.lower().startswith(prefix) for prefix in ['npx ', 'npm ', 'yarn ', 'pnpm ', 'pip ', 'pip3 '] ):
                commands.append(s)
        
        executed = []
        exec_errors = []
        
        if commands:
            colored_print("\n   COMMANDS TO RUN:", Colors.BRIGHT_YELLOW)
            for cmd in commands:
                colored_print(f"      $ {cmd}", Colors.YELLOW)
            
            # Execute safe commands automatically in project_dir
            auto_execute = True if data.get('execute_commands', True) else False
            if auto_execute:
                import subprocess, shlex, time
                colored_print("\n   EXECUTING SAFE COMMANDS...", Colors.BRIGHT_YELLOW)
                whitelist_prefixes = ['npx create-react-app', 'npm install', 'npm init', 'pnpm install', 'yarn install', 'pip install', 'pip3 install']
                heavy_prefixes = ['npx create-react-app', 'npx create-next-app', 'npm create vite@latest', 'yarn create react-app', 'pnpm create vite']
                backgrounded = []
                deferred = []
                created_app_dir = None

                # Utility to parse app dir from heavy scaffolding command (best-effort)
                def _parse_app_dir_from_cmd(c: str) -> str:
                    parts = shlex.split(c)
                    # look for last non-option token
                    name = None
                    for tok in reversed(parts):
                        if not tok.startswith('-') and tok not in ['--template', '--use-npm', '--use-pnpm', '--typescript']:
                            name = tok
                            break
                    if name and name not in ['npx', 'create-react-app', 'create-next-app', 'npm', 'create', 'vite@latest', 'yarn', 'pnpm']:
                        return os.path.join(project_dir, name)
                    return None

                # Ensure log directory exists
                log_dir = os.path.join(project_dir, '.agent_logs')
                os.makedirs(log_dir, exist_ok=True)

                for cmd in commands:
                    safe = any(cmd.lower().startswith(p) for p in whitelist_prefixes)
                    if not safe:
                        colored_print(f"      SKIP (not whitelisted): {cmd}", Colors.YELLOW)
                        continue

                    is_heavy = any(cmd.lower().startswith(p) for p in heavy_prefixes)

                    # If we started a heavy scaffolding and app dir not yet present, defer dependent installs
                    if not is_heavy and created_app_dir and not os.path.exists(created_app_dir):
                        colored_print(f"      DEFER: {cmd} (waiting for scaffolding to complete)", Colors.YELLOW)
                        deferred.append(cmd)
                        continue

                    try:
                        if is_heavy:
                            # Run in background with logging
                            ts = time.strftime('%Y%m%d_%H%M%S')
                            log_file = os.path.join(log_dir, f"scaffold_{ts}.log")
                            colored_print(f"      RUN (bg): {cmd}", Colors.CYAN)
                            with open(log_file, 'w') as lf:
                                proc = subprocess.Popen(shlex.split(cmd), cwd=project_dir, stdout=lf, stderr=lf)
                            backgrounded.append({"command": cmd, "pid": proc.pid, "log": log_file})
                            executed.append(f"{cmd} [bg pid={proc.pid}]")
                            # Predict app dir to adjust subsequent npm install cwd when ready
                            predicted = _parse_app_dir_from_cmd(cmd)
                            if predicted:
                                created_app_dir = predicted
                            # Register background job for monitoring
                            try:
                                self.bg_jobs.append({
                                    "pid": proc.pid,
                                    "command": cmd,
                                    "log": log_file,
                                    "project_dir": project_dir,
                                    "predicted_app_dir": created_app_dir,
                                    "start_time": time.time()
                                })
                                colored_print(f"         MONITOR: Registered bg job PID {proc.pid}", Colors.BLUE)
                            except Exception as e:
                                colored_print(f"         WARN: Could not register bg job: {e}", Colors.YELLOW)
                        else:
                            # Determine correct cwd (inside app dir if present with package.json)
                            run_cwd = project_dir
                            if created_app_dir and os.path.exists(created_app_dir) and os.path.exists(os.path.join(created_app_dir, 'package.json')):
                                run_cwd = created_app_dir
                            elif cmd.lower().startswith('npm install') and not os.path.exists(os.path.join(project_dir, 'package.json')):
                                colored_print(f"         SKIP: {cmd} (no package.json found; likely waiting for scaffolding)", Colors.YELLOW)
                                deferred.append(cmd)
                                continue

                            colored_print(f"      RUN: {cmd}", Colors.CYAN)
                            result = subprocess.run(shlex.split(cmd), cwd=run_cwd, capture_output=True, text=True)
                            if result.returncode == 0:
                                executed.append(cmd)
                                out = (result.stdout or '').strip()
                                if out:
                                    colored_print(f"         OK: {cmd} (output truncated)", Colors.GREEN)
                            else:
                                err = (result.stderr or '').strip()
                                colored_print(f"         ERROR: {cmd} -> {result.returncode}", Colors.RED)
                                if err:
                                    colored_print(f"         STDERR: {err[:300]}", Colors.RED)
                                exec_errors.append({"command": cmd, "code": result.returncode, "stderr": err})
                    except FileNotFoundError as e:
                        colored_print(f"         NOT FOUND: {cmd.split()[0]} (install required)", Colors.RED)
                        exec_errors.append({"command": cmd, "error": str(e)})
                    except Exception as e:
                        colored_print(f"         FAILED: {cmd} ({e})", Colors.RED)
                        exec_errors.append({"command": cmd, "error": str(e)})

                # Persist deferred commands for background watcher
                if deferred:
                    try:
                        existing = self.deferred_cmds.get(project_dir, [])
                        # maintain order; append new deferred
                        self.deferred_cmds[project_dir] = existing + deferred
                        colored_print(f"      QUEUED: {len(deferred)} deferred command(s) for monitoring", Colors.BLUE)
                    except Exception as e:
                        colored_print(f"      WARN: Could not queue deferred commands: {e}", Colors.YELLOW)

        # Attach extra execution metadata
        try:
            backgrounded
        except NameError:
            backgrounded = []
        try:
            deferred
        except NameError:
            deferred = []
        
        return {
            "type": "file_management_completed",
            "project_path": project_dir,
            "message": f"Applied structured file plan (created {len(created_files)} files, {len(created_dirs)} dirs)",
            "files_created": created_files,
            "directories_created": created_dirs,
            "commands_suggested": commands,
            "commands_executed": executed,
            "commands_backgrounded": backgrounded,
            "commands_deferred": deferred,
            "command_errors": exec_errors
        }

    def monitor_background_jobs(self):
        """Monitor background scaffold jobs; when they finish, try to run deferred commands."""
        import errno
        import subprocess, shlex

        def pid_running(pid: int) -> bool:
            try:
                # Signal 0 checks for existence without killing
                os.kill(pid, 0)
            except OSError as e:
                return e.errno == errno.EPERM  # Process exists but no permission
            else:
                return True

        def find_app_dir(project_dir: str, predicted: str = None) -> str:
            # Prefer predicted if it exists and has package.json
            if predicted and os.path.exists(predicted) and os.path.exists(os.path.join(predicted, 'package.json')):
                return predicted
            # Look for a single subdirectory with package.json
            try:
                for root, dirs, files in os.walk(project_dir):
                    # limit depth: immediate children first
                    for d in dirs:
                        candidate = os.path.join(root, d)
                        if os.path.exists(os.path.join(candidate, 'package.json')):
                            return candidate
                    break  # only immediate level
            except Exception:
                pass
            # As a fallback, use the project_dir if it contains package.json
            if os.path.exists(os.path.join(project_dir, 'package.json')):
                return project_dir
            return None

        while getattr(self, 'running', False):
            try:
                # Work on a shallow copy to allow modification
                jobs_snapshot = list(self.bg_jobs)
                for job in jobs_snapshot:
                    pid = job.get('pid')
                    proj = job.get('project_dir')
                    pred = job.get('predicted_app_dir')
                    cmd = job.get('command')
                    if not pid:
                        try:
                            self.bg_jobs.remove(job)
                        except ValueError:
                            pass
                        continue

                    if not pid_running(pid):
                        # Background process finished
                        try:
                            self.bg_jobs.remove(job)
                        except ValueError:
                            pass
                        colored_print(f"MONITOR: Background job finished (PID {pid}): {cmd}", Colors.BRIGHT_GREEN)

                        # Try to run deferred commands if any
                        queue = self.deferred_cmds.get(proj) or []
                        if not queue:
                            continue

                        app_dir = find_app_dir(proj, pred)
                        if not app_dir:
                            # No app dir detected yet; keep commands queued for next cycle
                            colored_print(f"MONITOR: App dir not ready; deferrals remain queued for {proj}", Colors.YELLOW)
                            # Re-append job marker with no pid to retry later (lightweight)
                            continue

                        # Run deferred commands sequentially
                        log_dir = os.path.join(proj, '.agent_logs')
                        os.makedirs(log_dir, exist_ok=True)
                        ts = time.strftime('%Y%m%d_%H%M%S')
                        log_file = os.path.join(log_dir, f'deferred_{ts}.log')
                        colored_print(f"MONITOR: Running {len(queue)} deferred command(s) in {app_dir}", Colors.CYAN)
                        with open(log_file, 'a') as lf:
                            for dcmd in list(queue):
                                try:
                                    lf.write(f"\n$ {dcmd}\n")
                                    result = subprocess.run(shlex.split(dcmd), cwd=app_dir, stdout=lf, stderr=lf, text=True)
                                    if result.returncode == 0:
                                        colored_print(f"   OK (deferred): {dcmd}", Colors.GREEN)
                                    else:
                                        colored_print(f"   ERROR (deferred {result.returncode}): {dcmd}", Colors.RED)
                                except FileNotFoundError:
                                    colored_print(f"   NOT FOUND (deferred): {dcmd.split()[0]}", Colors.RED)
                                except Exception as e:
                                    colored_print(f"   FAILED (deferred): {dcmd} ({e})", Colors.RED)
                                finally:
                                    # pop processed command regardless of success
                                    try:
                                        self.deferred_cmds[proj].pop(0)
                                    except Exception:
                                        pass

                        # Notify coordinator about completion
                        try:
                            self.comm.send_message(self.agent_id, 'coordinator', 
                                f"Deferred commands executed for project at {proj}. Log: {os.path.relpath(log_file, proj)}",
                                message_type='info')
                        except Exception:
                            pass

                time.sleep(3)
            except Exception as e:
                colored_print(f"MONITOR ERROR: {e}", Colors.RED)
                time.sleep(5)
    
    def _parse_ai_files_payload(self, text: str) -> list:
        """Parse AI output to a list of {path, content} dicts.

        Accepted forms:
        - Strict JSON: {"files":[{"path":"...","content":"..."}, ...]}
        - JSON object keyed by file paths: {"src/App.js":"...", ...}
        - Fallback: none (returns [])
        """
        import json, re

        if not text or not isinstance(text, str):
            return []

        candidates = []

        # Try to extract JSON blocks first
        code_blocks = re.findall(r"```(?:json)?\n(.*?)```", text, flags=re.S)
        if code_blocks:
            for block in code_blocks:
                try:
                    obj = json.loads(block)
                    candidates.append(obj)
                except Exception:
                    continue

        # If no fenced blocks, try the whole text as JSON
        if not candidates:
            try:
                candidates.append(json.loads(text))
            except Exception:
                pass

        files = []
        for obj in candidates:
            if not isinstance(obj, dict):
                continue
            if 'files' in obj and isinstance(obj['files'], list):
                for f in obj['files']:
                    if isinstance(f, dict) and 'path' in f and 'content' in f:
                        files.append({'path': f['path'], 'content': f.get('content', '')})
            else:
                # Map-style: {"path":"content"}
                all_strings = all(isinstance(k, str) and isinstance(v, str) for k, v in obj.items())
                if all_strings:
                    for k, v in obj.items():
                        files.append({'path': k, 'content': v})

        return files
    
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
            colored_print(f"   WARNING: AI model unavailable for component creation; skipping hard-coded fallbacks by design.", Colors.YELLOW)
            files_created = []
        
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
            
            if content:
                with open(full_path, 'w') as f:
                    f.write(content)
                colored_print(f"   SUCCESS: Created: {file_path}", Colors.GREEN)
            else:
                colored_print(f"   SKIP: No AI content for {file_path} (AI unavailable)", Colors.YELLOW)
    
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
            return ai_result.get('implementation', '')
        # AI-only policy: no hard-coded fallbacks
        return ""
    
    # NOTE: Removed universal hard-coded fallback content. AI-only generation is enforced.
    
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
            "src/styles/App.css": self.generate_react_css()
        }
        
        # Create component files for specific components
        for component in project_info["components"]:
            if component in ["TimeDisplay", "DateDisplay", "WeekDisplay"]:
                component_file = f"src/components/{component}.js"
                comp_content = self.generate_react_component(component)
                if comp_content:
                    files_to_create[component_file] = comp_content
        
        # Write all files
        for file_path, content in list(files_to_create.items()):
            full_file_path = os.path.join(project_path, file_path)
            with open(full_file_path, 'w') as f:
                if content:
                    f.write(content)
                    colored_print(f"    Created: {file_path}", Colors.GREEN)
                else:
                    colored_print(f"    SKIP: No AI content for {file_path}", Colors.YELLOW)
    
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
            return ai_result.get('implementation', '')
        # AI-only policy: no hard-coded fallback
        return ""
    
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
            return ai_result.get('implementation', '')
        return ""
    
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
            return ai_result.get('implementation', '')
        return ""
    
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
            return ai_result.get('implementation', '')
        return ""
    
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
            return ai_result.get('implementation', '')
        return ""
    
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
            return ai_result.get('implementation', '')
        return ""
    
    def generate_react_component(self, component_name: str) -> str:
        """Generate React component using AI collaboration with project context (AI-only)."""
        
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
            return ai_result.get('implementation', '')
        return ""
    
    def handle_git_management_task(self, task: Dict) -> Dict:
        """Handle git management tasks"""
        # Get the correct working directory from project context
        working_dir = self._get_working_directory()
        colored_print(f"GIT: Operating in directory: {working_dir}", Colors.CYAN)
        
        return {"message": f"Git management task handled: {task['description']}"}
    
    def handle_research_task(self, task: Dict) -> Dict:
        """Handle research tasks"""
        return {"message": f"Research task completed: {task['description']}"}
    
    def handle_testing_task(self, task: Dict) -> Dict:
        """Handle testing tasks"""
        return {"message": f"Testing task completed: {task['description']}"}
    
    def handle_code_rewriter_task(self, task: Dict) -> Dict:
        """Handle code rewriting tasks from code reviewer reports"""
        
        # Get the correct working directory from project context
        working_dir = self._get_working_directory()
        
        description = task["description"]
        colored_print(f"CONFIG: CODE REWRITER: Processing code fixes", Colors.BRIGHT_CYAN)
        colored_print(f"   Task: {description}", Colors.CYAN)
        colored_print(f"   Working Directory: {working_dir}", Colors.CYAN)
        
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
    
    def show_all_agents_status(self):
        """Show real-time status of all agents and their current activity"""
        import time
        
        colored_print("\n" + "=" * 80, Colors.BRIGHT_CYAN)
        colored_print("AGENT STATUS DASHBOARD", Colors.BRIGHT_CYAN)
        colored_print("=" * 80, Colors.BRIGHT_CYAN)
        
        agents = self.comm.load_agents()
        active_agents = [a for a in agents if a.get('status') == 'active']
        inactive_agents = [a for a in agents if a.get('status') != 'active']
        
        # Summary
        colored_print(f"\nTotal Agents: {len(agents)} | Active: {len(active_agents)} | Inactive: {len(inactive_agents)}", 
                     Colors.WHITE)
        
        if not agents:
            colored_print("\nNo agents registered.", Colors.YELLOW)
            return
        
        # Show active agents with their current tasks
        if active_agents:
            colored_print("\n" + "─" * 80, Colors.CYAN)
            colored_print("ACTIVE AGENTS:", Colors.BRIGHT_GREEN)
            colored_print("─" * 80, Colors.CYAN)
            
            for agent_info in active_agents:
                agent_id = agent_info['id']
                agent_role = agent_info['role']
                pid = agent_info.get('pid', 'N/A')
                last_seen = agent_info.get('last_seen', 'unknown')
                
                # Check if process is running
                process_status = "●"  # Running indicator
                process_color = Colors.GREEN
                if pid and pid != 'N/A':
                    try:
                        os.kill(pid, 0)
                        process_status = "● RUNNING"
                    except ProcessLookupError:
                        process_status = "○ STOPPED"
                        process_color = Colors.RED
                    except PermissionError:
                        process_status = "◐ UNKNOWN"
                        process_color = Colors.YELLOW
                
                # Agent header
                colored_print(f"\n{agent_role:20} [{agent_id}]", Colors.BRIGHT_GREEN)
                print(f"  {colored_text(process_status, process_color):30} PID: {pid}")
                print(f"  Last Activity: {last_seen}")
                
                # Show current tasks
                tasks = self.comm.get_pending_tasks(agent_id)
                all_tasks = self.comm.load_tasks()
                
                # Find tasks assigned to this agent (both pending and in-progress)
                agent_tasks = [t for t in all_tasks if t.get('assigned_to') == agent_id]
                in_progress = [t for t in agent_tasks if t.get('status') == 'in_progress']
                pending = [t for t in agent_tasks if t.get('status') == 'pending']
                completed_recent = [t for t in agent_tasks if t.get('status') == 'completed'][-3:]  # Last 3 completed
                
                if in_progress:
                    colored_print(f"  📋 WORKING ON:", Colors.BRIGHT_YELLOW)
                    for task in in_progress:
                        desc = task.get('description', 'No description')
                        if len(desc) > 60:
                            desc = desc[:57] + "..."
                        print(f"     ▸ {desc}")
                        if 'started_at' in task:
                            print(f"       Started: {task['started_at']}")
                
                if pending:
                    colored_print(f"  📝 QUEUED ({len(pending)}):", Colors.CYAN)
                    for task in pending[:2]:  # Show first 2 pending
                        desc = task.get('description', 'No description')
                        if len(desc) > 60:
                            desc = desc[:57] + "..."
                        print(f"     • {desc}")
                    if len(pending) > 2:
                        print(f"     ... and {len(pending) - 2} more")
                
                if completed_recent:
                    colored_print(f"  ✓ RECENT COMPLETIONS:", Colors.GREEN)
                    for task in completed_recent:
                        desc = task.get('description', 'No description')
                        if len(desc) > 50:
                            desc = desc[:47] + "..."
                        print(f"     ✓ {desc}")
                
                if not in_progress and not pending:
                    colored_print(f"  💤 IDLE - No active tasks", Colors.WHITE)
        
        # Show inactive agents summary
        if inactive_agents:
            colored_print("\n" + "─" * 80, Colors.YELLOW)
            colored_print(f"INACTIVE AGENTS ({len(inactive_agents)}):", Colors.YELLOW)
            colored_print("─" * 80, Colors.YELLOW)
            for agent_info in inactive_agents[:5]:  # Show first 5 inactive
                print(f"  {agent_info['role']:20} [{agent_info['id']}] - {agent_info.get('status', 'unknown')}")
            if len(inactive_agents) > 5:
                print(f"  ... and {len(inactive_agents) - 5} more")
            colored_print("  TIP: Use 'cleanup' to remove inactive agents", Colors.CYAN)
        
        colored_print("\n" + "=" * 80, Colors.BRIGHT_CYAN)
        colored_print(f"Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}", Colors.WHITE)
        colored_print("=" * 80 + "\n", Colors.BRIGHT_CYAN)
    
    def enrich_task_description(self, description: str, target_agent: str) -> Dict:
        """
        ENHANCED: Use AI to enrich task description with comprehensive context and best practices
        
        This method makes the delegate command intelligent by:
        1. Analyzing the task requirements
        2. Adding framework-specific context
        3. Including tool/command suggestions (like npx, npm scripts)
        4. Providing implementation guidance
        5. Suggesting project structure
        """
        colored_print(f"\nAI: Analyzing and enriching task description...", Colors.CYAN)
        
        # Build comprehensive context for AI
        context_info = []
        if hasattr(self, 'current_project_process') and self.current_project_process:
            context_info.append(f"Current Project: {self.current_project_process}")
            context_info.append(f"Project Path: {self.project_process_workspace}")
        
        context_str = "\n".join(context_info) if context_info else "No active project"
        
        # Create intelligent prompt for AI
        prompt = f"""You are assisting a multi-agent development system. Analyze this task and provide enhanced instructions.

ORIGINAL TASK: {description}
TARGET AGENT: {target_agent}
CONTEXT: {context_str}

Your job is to ENRICH this task description with comprehensive details so the {target_agent} agent can execute it perfectly.

Analyze what the user wants and provide:

1. **Enhanced Description**: A detailed, actionable description including:
   - Exact steps to take
   - Tools/commands to use (npx create-react-app, npm init, pip install, etc.)
   - Framework best practices
   - Project structure suggestions
   - All necessary files and configurations

2. **Implementation Guidance**: For example:
   - For React projects: Use npx create-react-app or Vite, include package.json, src structure, components
   - For Python projects: Include requirements.txt, proper module structure, virtual environment setup
   - For Node projects: Include package.json, proper script definitions (start, dev, build, test)

3. **Specific Requirements**: Break down into concrete tasks:
   - Files to create
   - Dependencies to include
   - Configuration files needed
   - Component/module structure

Return your response in this JSON format:
{{
    "enhanced_description": "Comprehensive task description with all details, tools, commands, and best practices...",
    "framework_detected": "react|vue|python|node|etc",
    "suggested_tools": ["npx create-react-app", "npm install", "etc"],
    "required_files": ["package.json", "src/App.js", "etc"],
    "best_practices": ["Use functional components", "Include error handling", "etc"],
    "task_data": {{
        "framework": "detected_framework",
        "use_tools": true,
        "generate_complete_project": true,
        "additional_context": "any extra info"
    }}
}}

IMPORTANT: Make the enhanced_description extremely detailed and actionable. Include ALL necessary context for creating a complete, production-ready result.

Return ONLY valid JSON, no markdown or explanations."""

        # Try to get AI enhancement using the correct method
        ai_result = self.try_ai_implementation(prompt)
        
        if ai_result.get('status') != 'success':
            colored_print(f"AI: Enhancement unavailable, using original description", Colors.YELLOW)
            return {
                'enhanced_description': description,
                'was_enhanced': False,
                'task_data': {}
            }
        
        # Parse AI response
        try:
            import re
            import json
            response = ai_result.get('implementation', '')
            
            # Clean up the response - remove control characters and fix common issues
            # Remove control characters except newlines and tabs
            response = ''.join(char for char in response if ord(char) >= 32 or char in '\n\t')
            
            # Extract JSON from response
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            else:
                # Try to find JSON object boundaries more carefully
                start = response.find('{')
                if start != -1:
                    # Count braces to find matching closing brace
                    brace_count = 0
                    end = start
                    for i in range(start, len(response)):
                        if response[i] == '{':
                            brace_count += 1
                        elif response[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end = i + 1
                                break
                    response = response[start:end]
            
            # Additional cleaning - escape unescaped quotes in strings if needed
            enrichment = json.loads(response)
            
            colored_print(f"AI: Task enhanced successfully", Colors.GREEN)
            if enrichment.get('framework_detected'):
                colored_print(f"AI: Detected framework: {enrichment['framework_detected']}", Colors.CYAN)
            if enrichment.get('suggested_tools'):
                colored_print(f"AI: Suggested tools: {', '.join(enrichment['suggested_tools'][:3])}", Colors.CYAN)
            
            return {
                'enhanced_description': enrichment.get('enhanced_description', description),
                'was_enhanced': True,
                'task_data': enrichment.get('task_data', {}),
                'framework': enrichment.get('framework_detected'),
                'tools': enrichment.get('suggested_tools', []),
                'best_practices': enrichment.get('best_practices', [])
            }
            
        except (json.JSONDecodeError, Exception) as e:
            colored_print(f"AI: JSON parsing failed ({str(e)[:50]}), using enhanced text mode", Colors.YELLOW)
            # Fallback: Use the raw response as enhanced description
            # This way the file manager can still parse it as structured instructions
            response = ai_result.get('implementation', '')
            if response and len(response) > len(description):
                colored_print(f"AI: Using enhanced text description (not JSON)", Colors.CYAN)
                return {
                    'enhanced_description': response,
                    'was_enhanced': True,
                    'task_data': {'format': 'text_instructions'},
                }
            return {
                'enhanced_description': description,
                'was_enhanced': False,
                'task_data': {}
            }
    
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
                        print("  set_workspace <path> - Set BASE workspace directory (for multi-project setups)")
                        print("      WARNING: This changes the base workspace for ALL agents")
                        print("      NOTE: For creating projects, use the guided wizard instead")
                        print("  stats - Show delegation statistics")
                        print("  workflows - Show active workflows")
                        print()
                    colored_print("Agent Management Commands:", Colors.BRIGHT_YELLOW)
                    print("  kill <agent_name> - Kill and remove a faulty agent")
                    print("  restart <agent_name> - Restart a specific agent")
                    print("  status - Show real-time status dashboard for all agents")
                    print("  status <agent_name> - Check detailed status of specific agent")
                    print("  spawn <role> <name> - Create new agent with role and name")
                    print("  cleanup - Remove all inactive agents")
                    print()
                    print("  quit - Exit the terminal")
                elif user_input.lower() == 'agents':
                    agents = agent.comm.get_active_agents()
                    colored_print(f"\nActive Agents ({len(agents)}):", Colors.BRIGHT_CYAN)
                    colored_print("=" * 70, Colors.CYAN)
                    for a in agents:
                        status_color = Colors.GREEN if a.get('status') == 'active' else Colors.YELLOW
                        role_str = f"{a['role']:20}"
                        id_str = f"{a['id']:20}"
                        pid_str = f"PID: {str(a.get('pid', 'N/A')):8}"
                        status_str = f"Status: {a.get('status', 'unknown'):10}"
                        
                        print(f"{colored_text(role_str, Colors.BRIGHT_GREEN)} {colored_text(id_str, Colors.CYAN)} {colored_text(pid_str, status_color)} {colored_text(status_str, status_color)}")
                        
                        # Show last seen if available
                        if 'last_seen' in a:
                            print(f"    Last seen: {a['last_seen']}")
                        if 'registered_at' in a:
                            print(f"    Registered: {a['registered_at']}")
                    
                    # Also show total agent count from all agents (not just active)
                    all_agents = agent.comm.load_agents()
                    inactive_count = len([ag for ag in all_agents if ag.get('status') != 'active'])
                    if inactive_count > 0:
                        colored_print(f"\nInactive Agents: {inactive_count}", Colors.YELLOW)
                        colored_print("TIP: Use 'cleanup' to remove inactive agents", Colors.CYAN)
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
                elif user_input.lower() == 'status':
                    # Show status of all agents (no specific agent name)
                    agent.show_all_agents_status()
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
                    # Set workspace directory - IMPORTANT: This changes the base workspace location
                    # For project creation, projects will be created INSIDE this workspace
                    if role == AgentRole.COORDINATOR:
                        new_workspace = user_input[14:].strip()
                        
                        # IMPORTANT: If user provides just a project name (no path separators),
                        # create it under the standard workspace directory
                        if '/' not in new_workspace and '\\' not in new_workspace:
                            # It's just a project name - create under standard workspace
                            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                            multi_agent_workspace = os.path.join(script_dir, 'workspace')
                            new_workspace = os.path.join(multi_agent_workspace, new_workspace)
                            colored_print(f"INFO: Creating project under standard workspace: {new_workspace}", Colors.CYAN)
                        else:
                            # Full path provided - expand and use as-is
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
                            
                            # ENHANCED: Use AI to enrich the task description with context
                            enriched_description = agent.enrich_task_description(description, target_agent)
                            
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

                            # If delegating to file manager, enrich and split into structured subtasks
                            if assigned_to in ['files', 'file_manager']:
                                proj_name = agent.current_project_process if hasattr(agent, 'current_project_process') else None
                                proj_path = str(agent.project_process_workspace) if hasattr(agent, 'project_process_workspace') and agent.project_process_workspace else None
                                created = agent.split_and_delegate_enriched_task(description, proj_name, proj_path)
                                colored_print(f"Created {len(created)} task(s) from enriched plan and delegated to appropriate agents", Colors.GREEN)
                            else:
                                # IMPORTANT: Include current project context in task data
                                task_data = enriched_description.get('task_data', {})
                                if hasattr(agent, 'current_project_process') and agent.current_project_process:
                                    task_data['project_name'] = agent.current_project_process
                                    task_data['project_workspace'] = str(agent.project_process_workspace)
                                    colored_print(f"Including project context: {agent.current_project_process}", Colors.CYAN)

                                # Use enriched description if AI enhancement succeeded
                                final_description = enriched_description.get('enhanced_description', description)

                                task_id = agent.comm.create_task(
                                    task_type="general",
                                    description=final_description,
                                    assigned_to=assigned_to,
                                    created_by=agent_id,
                                    data=task_data
                                )
                                colored_print(f"Task {task_id} created and delegated to {target_agent}!", Colors.GREEN)
                                if enriched_description.get('was_enhanced'):
                                    colored_print(f"AI: Task description enhanced with best practices", Colors.CYAN)
                        else:
                            colored_print("Invalid format. Use: delegate \"description\" to agent_name", Colors.RED)
                    else:
                        # Old format: just delegate description (default to coder)
                        description = command_part
                        if description:
                            # Enrich description for coder
                            enriched_description = agent.enrich_task_description(description, 'coder')
                            
                            # Include project context
                            task_data = enriched_description.get('task_data', {})
                            if hasattr(agent, 'current_project_process') and agent.current_project_process:
                                task_data['project_name'] = agent.current_project_process
                                task_data['project_workspace'] = str(agent.project_process_workspace)
                            
                            final_description = enriched_description.get('enhanced_description', description)
                            
                            task_id = agent.comm.create_task(
                                task_type="general",
                                description=final_description,
                                assigned_to="coder",  # Default to coder
                                created_by=agent_id,
                                data=task_data
                            )
                            colored_print(f"Task {task_id} created and delegated to coder!", Colors.GREEN)
                            if enriched_description.get('was_enhanced'):
                                colored_print(f"AI: Task description enhanced with best practices", Colors.CYAN)
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
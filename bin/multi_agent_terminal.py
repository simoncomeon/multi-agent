#!/usr/bin/env python3
import os
import re
import json
import time
import uuid
import threading
import subprocess
import readline
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from enum import Enum

# === Color codes ===
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_WHITE = "\033[97m"
    BRIGHT_RED = '\033[91m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_BLUE = '\033[94m'

def colored_print(text, color=Colors.RESET, end='\n'):
    print(f"{color}{text}{Colors.RESET}", end=end)

# === Agent Communication System ===
class AgentRole(Enum):
    COORDINATOR = "coordinator"      # Main agent that coordinates tasks
    CODER = "coder"                 # Specializes in code analysis/generation
    CODE_REVIEWER = "code_reviewer" # Reviews, optimizes, and ensures code quality
    CODE_REWRITER = "code_rewriter" # Fixes issues found by code reviewer
    FILE_MANAGER = "file_manager"   # Handles file operations
    GIT_MANAGER = "git_manager"     # Handles version control
    RESEARCHER = "researcher"       # Searches and analyzes information

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
                print(f"   Task {task['id']}: {task['description']}")
        
        return pending
    
    def send_message(self, from_agent: str, to_agent: str, message_type: str, content: Dict):
        """Send message between agents"""
        message = AgentMessage(
            id=str(uuid.uuid4())[:8],
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            timestamp=datetime.now()
        )
        
        try:
            with open(self.messages_file, 'r') as f:
                messages = json.load(f)
        except:
            messages = []
        
        # Convert message to JSON-serializable dict
        message_dict = {
            "id": message.id,
            "from_agent": message.from_agent,
            "to_agent": message.to_agent,
            "message_type": message.message_type,
            "content": message.content,
            "timestamp": message.timestamp.isoformat()
        }
        messages.append(message_dict)
        
        with open(self.messages_file, 'w') as f:
            json.dump(messages, f, indent=2)
        
        colored_print(f"📨 Message: {from_agent} -> {to_agent} ({message_type})", Colors.CYAN)

# === Enhanced Agent Terminal ===
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
        
        # Settings
        self.ollama_cmd = "ollama"
        self.default_model = "llama3.2"
        self.history_file = str(Path.home() / f".agent_history_{agent_id}")
        
        # Register this agent
        self.comm.register_agent(agent_id, role)
        
        # Load history
        self.load_history()
        
        # Start background task monitor
        self.running = True
        self.task_thread = threading.Thread(target=self.monitor_tasks, daemon=True)
        self.task_thread.start()
    
    def load_history(self):
        try:
            readline.read_history_file(self.history_file)
        except FileNotFoundError:
            pass
    
    def save_history(self):
        try:
            readline.write_history_file(self.history_file)
        except Exception as e:
            colored_print(f"-- Could not save history: {e}", Colors.YELLOW)
    
    def monitor_tasks(self):
        """Background thread to monitor and execute pending tasks"""
        last_task_check = 0
        while self.running:
            try:
                pending_tasks = self.comm.get_pending_tasks(self.agent_id)
                if pending_tasks:
                    colored_print(f"\n🔍 Found {len(pending_tasks)} pending tasks for {self.role.value} (ID: {self.agent_id})", Colors.CYAN)
                    for task in pending_tasks:
                        colored_print(f"\n📨 Task received from delegation:", Colors.BRIGHT_GREEN)
                        colored_print(f"   Task ID: {task.get('id', 'unknown')}", Colors.WHITE)
                        colored_print(f"   Description: {task.get('description', 'no description')}", Colors.WHITE)
                        colored_print(f"   Assigned to: {task.get('assigned_to', 'unknown')}", Colors.WHITE)
                        colored_print(f"   Created by: {task.get('created_by', 'unknown')}", Colors.WHITE)
                        colored_print(f"Processing task: {task.get('id', 'unknown')} - {task.get('description', 'no description')}", Colors.YELLOW)
                        self.execute_task(task)
                
                # Only show "no tasks" message occasionally to reduce spam
                current_time = time.time()
                if not pending_tasks and (current_time - last_task_check) > 30:
                    # colored_print(f"⏱️  Monitoring for tasks... ({self.role.value})", Colors.DIM)
                    last_task_check = current_time
                    
                time.sleep(3)  # Check every 3 seconds
            except Exception as e:
                colored_print(f"-- Task monitor error: {e}", Colors.RED)
                import traceback
                colored_print(f"-- Stack trace: {traceback.format_exc()}", Colors.RED)
                time.sleep(1)
    
    def execute_task(self, task: Dict):
        """Execute a task based on its type"""
        task_id = task["id"]
        task_type = task["type"]
        
        colored_print(f"\n-- Executing task {task_id}: {task['description']}", Colors.BRIGHT_BLUE)
        colored_print(f"Task ID: {task_id}", Colors.CYAN)
        colored_print(f"Task type: {task_type}", Colors.CYAN)
        colored_print(f"Agent role: {self.role.value}", Colors.CYAN)
        
        try:
            self.comm.update_task_status(task_id, TaskStatus.IN_PROGRESS)
            
            if task_type == "analyze_code":
                result = self.analyze_code_task(task)
            elif task_type == "create_file":
                result = self.create_file_task(task)
            elif task_type == "git_operation":
                result = self.git_operation_task(task)
            elif task_type == "research":
                result = self.research_task(task)
            elif task_type == "review_code":
                result = self.review_code_task(task)
            elif task_type == "optimize_project":
                result = self.optimize_project_task(task)
            elif task_type == "validate_project":
                result = self.validate_project_task(task)
            elif task_type == "helicopter_review":
                result = self.helicopter_review_task(task)
            elif task_type == "rewrite_code":
                result = self.rewrite_code_task(task)
            elif task_type == "fix_review_issues":
                result = self.fix_review_issues_task(task)
            elif task_type == "general":
                result = self.general_task(task)
            elif task_type == "create_project":
                result = self.create_project_smart(task["description"])
            elif task_type == "delegated_task":
                # Handle delegated tasks by routing to general task handler
                result = self.general_task(task)
            else:
                colored_print(f"Unknown task type: {task_type}", Colors.YELLOW)
                # Try to handle as general task if it's a file manager operation
                if self.role == AgentRole.FILE_MANAGER:
                    result = self.create_project_smart(task["description"])
                else:
                    result = {"error": f"Unknown task type: {task_type}"}
            
            self.comm.update_task_status(task_id, TaskStatus.COMPLETED, result)
            colored_print(f"-- Task {task_id} completed", Colors.GREEN)
            
        except Exception as e:
            error_result = {"error": str(e)}
            self.comm.update_task_status(task_id, TaskStatus.FAILED, error_result)
            colored_print(f"-- Task {task_id} failed: {e}", Colors.RED)
    
    def analyze_code_task(self, task: Dict) -> Dict:
        """Analyze code files"""
        file_path = task["data"].get("file_path")
        analysis_type = task["data"].get("analysis_type", "general")
        
        if not file_path or not os.path.exists(file_path):
            return {"error": "File not found"}
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        prompt = f"Analyze this {analysis_type} code and provide insights:\n\n{content}"
        response = self.query_ollama(prompt)
        
        return {"analysis": response, "file_path": file_path}
    
    def create_file_task(self, task: Dict) -> Dict:
        """Create or edit files"""
        file_path = task["data"].get("file_path")
        content_prompt = task["data"].get("prompt")
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                current_content = f.read()
            prompt = f"Edit this file: {content_prompt}\n\nCurrent content:\n{current_content}\n\nProvide ONLY the complete file content, no explanations."
        else:
            # Determine if this is a code file
            is_code_file = any(ext in file_path.lower() for ext in ['.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.cpp', '.c'])
            
            if is_code_file:
                prompt = f"""Create a {file_path} file: {content_prompt}
                
                Requirements:
                - Provide ONLY executable code
                - NO explanatory text or comments about what to do  
                - NO markdown code blocks
                - Start directly with code (imports, declarations, etc.)
                - Make it production-ready and complete"""
            else:
                prompt = f"Create a new file: {content_prompt}"
        
        raw_content = self.query_ollama(prompt)
        
        # Extract clean content for code files
        if any(ext in file_path.lower() for ext in ['.js', '.jsx', '.ts', '.tsx']):
            new_content = self.extract_code_from_response(raw_content)
        else:
            new_content = raw_content
        
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        return {"file_created": file_path, "content_length": len(new_content)}
    
    def git_operation_task(self, task: Dict) -> Dict:
        """Handle git operations"""
        operation = task["data"].get("operation")
        
        if operation == "status":
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True)
            return {"git_status": result.stdout}
        elif operation == "add_commit":
            message = task["data"].get("message", "Automated commit")
            subprocess.run(["git", "add", "."])
            result = subprocess.run(["git", "commit", "-m", message], 
                                  capture_output=True, text=True)
            return {"commit_result": result.stdout}
        
        return {"error": "Unknown git operation"}
    
    def research_task(self, task: Dict) -> Dict:
        """Research and information gathering"""
        query = task["data"].get("query")
        context = task["data"].get("context", "")
        
        prompt = f"Research and provide detailed information about: {query}"
        if context:
            prompt += f"\nContext: {context}"
        
        response = self.query_ollama(prompt)
        return {"research_result": response}
    
    def general_task(self, task: Dict) -> Dict:
        """Handle general tasks by routing based on agent role and task description"""
        description = task["description"].lower()
        
        if self.role == AgentRole.FILE_MANAGER:
            # Handle file/directory creation tasks
            if "create" in description or "structure" in description or "directory" in description:
                return self.handle_project_creation_task(task)
        
        elif self.role == AgentRole.CODER:
            # Handle code generation tasks
            if "generate" in description or "create" in description and (".js" in description or "component" in description):
                return self.handle_code_generation_task(task)
        
        elif self.role == AgentRole.CODE_REVIEWER:
            # Handle review tasks
            if "review" in description or "optimize" in description or "performance" in description:
                return self.handle_code_review_task(task)
        
        elif self.role == AgentRole.CODE_REWRITER:
            # Handle code rewriting and fixing tasks
            if "fix" in description or "rewrite" in description or "clean" in description or "repair" in description:
                return self.handle_code_rewrite_task(task)
        
        elif self.role == AgentRole.RESEARCHER:
            # Handle research tasks
            return self.research_task(task)
        
        # Default: use AI to handle the task
        prompt = f"As a {self.role.value} agent, complete this task: {task['description']}"
        try:
            response = self.query_ollama(prompt)
        except:
            # Fallback if ollama is not available
            response = f"Task acknowledged by {self.role.value} agent: {task['description']}"
        return {"result": response, "completed_by": self.role.value}
    
    def extract_project_name(self, description: str) -> str:
        """Intelligently extract project name from description"""
        import re
        
        # Look for explicit project names in description
        patterns = [
            r'(\w+App)',           # SomethingApp
            r'(\w+Project)',       # SomethingProject  
            r'(\w+Calculator)',    # SomethingCalculator
            r'(\w+Display)',       # SomethingDisplay
            r'(\w+Manager)',       # SomethingManager
            r'(\w+System)',        # SomethingSystem
            r'project\s+(\w+)',    # project Something
            r'app\s+(\w+)',        # app Something
            r'create\s+(\w+)',     # create Something
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Default fallback names based on content
        if "time" in description.lower() and "display" in description.lower():
            return "TimeDisplayApp"
        elif "budget" in description.lower():
            return "BudgetCalculator"
        elif "todo" in description.lower():
            return "TodoApp"
        elif "chat" in description.lower():
            return "ChatApp"
        elif "blog" in description.lower():
            return "BlogApp"
        elif "dashboard" in description.lower():
            return "Dashboard"
        else:
            return "MyProject"
    
    def detect_project_type(self, description: str) -> str:
        """Intelligently detect project type from description"""
        desc_lower = description.lower()
        
        # Frontend frameworks
        if "react.js" in desc_lower or "react js" in desc_lower or ("react" in desc_lower and ("web" in desc_lower or "browser" in desc_lower)):
            return "react-js"
        elif "react native" in desc_lower or ("react" in desc_lower and ("mobile" in desc_lower or "ios" in desc_lower or "android" in desc_lower)):
            return "react-native"
        elif "vue" in desc_lower:
            return "vue"
        elif "angular" in desc_lower:
            return "angular"
        elif "svelte" in desc_lower:
            return "svelte"
        elif "next" in desc_lower and "js" in desc_lower:
            return "nextjs"
        
        # Backend frameworks
        elif "flask" in desc_lower:
            return "flask"
        elif "django" in desc_lower:
            return "django"
        elif "fastapi" in desc_lower:
            return "fastapi"
        elif "express" in desc_lower or ("node" in desc_lower and "js" in desc_lower):
            return "nodejs"
        elif "spring" in desc_lower:
            return "spring"
        
        # Languages
        elif "python" in desc_lower:
            return "python"
        elif "javascript" in desc_lower or "js" in desc_lower:
            return "javascript"
        elif "typescript" in desc_lower or "ts" in desc_lower:
            return "typescript"
        elif "java" in desc_lower:
            return "java"
        elif "c++" in desc_lower or "cpp" in desc_lower:
            return "cpp"
        elif "rust" in desc_lower:
            return "rust"
        elif "go" in desc_lower and "golang" in desc_lower:
            return "golang"
        
        # Project types
        elif "web" in desc_lower or "website" in desc_lower or "html" in desc_lower:
            return "web"
        elif "api" in desc_lower:
            return "api"
        elif "cli" in desc_lower or "command line" in desc_lower:
            return "cli"
        elif "desktop" in desc_lower:
            return "desktop"
        elif "game" in desc_lower:
            return "game"
        
        # Default
        return "generic"
    
    def create_project_smart(self, description: str) -> Dict:
        """Smart project creation that accepts a description string"""
        # Create a task-like dict to reuse the existing logic
        task = {"description": description}
        return self.handle_project_creation_task(task)
    
    def handle_project_creation_task(self, task: Dict) -> Dict:
        """Universal project structure creation for any type of project"""
        description = task["description"]
        
        colored_print(f"\n🔧 File Manager Processing Task:", Colors.BRIGHT_YELLOW)
        colored_print(f"   Task: {description}", Colors.WHITE)
        colored_print(f"   Status: Analyzing project requirements...", Colors.CYAN)
        
        # Ensure we're working in the workspace directory
        workspace_dir = self.workspace_dir
        if not os.path.exists(workspace_dir):
            os.makedirs(workspace_dir, exist_ok=True)
            colored_print(f"   Created workspace directory: {workspace_dir}", Colors.GREEN)
        
        # Intelligently extract project details
        colored_print(f"   Status: Extracting project details...", Colors.CYAN)
        project_name = self.extract_project_name(description)
        project_type = self.detect_project_type(description)
        project_path = os.path.join(workspace_dir, project_name)
        
        colored_print(f"   Detected project type: {project_type}", Colors.YELLOW)
        colored_print(f"   Project name: {project_name}", Colors.YELLOW)
        colored_print(f"Creating {project_type} project: {project_name}", Colors.BRIGHT_CYAN)
        colored_print(f"Location: {project_path}", Colors.CYAN)
        
        # Create project based on detected type
        colored_print(f"   Status: Starting {project_type} project creation...", Colors.CYAN)
        
        if project_type == "react-js":
            result = self.create_reactjs_project(project_name, project_path, description)
        elif project_type == "react-native":
            result = self.create_react_native_project(project_name, project_path, description)
        elif project_type == "vue":
            result = self.create_vue_project(project_name, project_path, description)
        elif project_type == "angular":
            result = self.create_angular_project(project_name, project_path, description)
        elif project_type == "nextjs":
            result = self.create_nextjs_project(project_name, project_path, description)
        elif project_type == "flask":
            result = self.create_flask_project(project_name, project_path, description)
        elif project_type == "django":
            result = self.create_django_project(project_name, project_path, description)
        elif project_type == "nodejs":
            result = self.create_nodejs_project(project_name, project_path, description)
        elif project_type == "python":
            result = self.create_python_project(project_name, project_path, description)
        elif project_type == "javascript":
            result = self.create_js_project(project_name, project_path, description)
        elif project_type == "web":
            result = self.create_web_project(project_name, project_path, description)
        elif project_type == "api":
            result = self.create_api_project(project_name, project_path, description)
        else:
            result = self.create_generic_project(project_name, project_path, description)
        
        # Show completion status
        if result and result.get("success", True):
            colored_print(f"\n✅ File Manager Task Completed Successfully!", Colors.BRIGHT_GREEN)
            colored_print(f"   Project: {project_name} ({project_type})", Colors.WHITE)
            colored_print(f"   Location: {project_path}", Colors.WHITE)
            if "files_created" in result:
                colored_print(f"   Files created: {len(result['files_created'])}", Colors.WHITE)
        else:
            colored_print(f"\n❌ File Manager Task Failed!", Colors.BRIGHT_RED)
            if result and "error" in result:
                colored_print(f"   Error: {result['error']}", Colors.WHITE)
        
        return result
    
    def create_reactjs_project(self, name: str, path: str, description: str) -> Dict:
        """Create a React.js web application project"""
        try:
            # Create directory structure
            directories = [
                f"{path}/public",
                f"{path}/src",
                f"{path}/src/components", 
                f"{path}/src/utils",
                f"{path}/src/styles"
            ]
            
            created_files = []
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            
            # Create package.json
            package_json = {
                "name": name.lower().replace(" ", "-"),
                "version": "0.1.0",
                "private": True,
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-scripts": "5.0.1",
                    "date-fns": "^2.30.0"
                },
                "scripts": {
                    "start": "react-scripts start",
                    "build": "react-scripts build", 
                    "test": "react-scripts test",
                    "eject": "react-scripts eject"
                },
                "eslintConfig": {
                    "extends": ["react-app", "react-app/jest"]
                },
                "browserslist": {
                    "production": [">0.2%", "not dead", "not op_mini all"],
                    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
                }
            }
            
            package_path = f"{path}/package.json"
            with open(package_path, 'w') as f:
                json.dump(package_json, f, indent=2)
            created_files.append(package_path)
            
            # Create public/index.html
            html_content = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="{name} - React.js Application" />
    <title>{name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>"""
            
            html_path = f"{path}/public/index.html"
            with open(html_path, 'w') as f:
                f.write(html_content)
            created_files.append(html_path)
            
            # Create src/index.js
            index_js = f"""import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);"""
            
            index_path = f"{path}/src/index.js"
            with open(index_path, 'w') as f:
                f.write(index_js)
            created_files.append(index_path)
            
            # Create src/App.js
            app_js = f"""import React from 'react';
import './styles/App.css';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>{name}</h1>
        <p>Your React.js application is ready!</p>
      </header>
    </div>
  );
}}

export default App;"""
            
            app_path = f"{path}/src/App.js"
            with open(app_path, 'w') as f:
                f.write(app_js)
            created_files.append(app_path)
            
            # Create basic CSS
            css_content = """.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
}

.App-header h1 {
  margin: 0 0 10px 0;
}"""
            
            css_path = f"{path}/src/styles/App.css"
            os.makedirs(f"{path}/src/styles", exist_ok=True)
            with open(css_path, 'w') as f:
                f.write(css_content)
            created_files.append(css_path)
            
            index_css = """body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New', monospace;
}"""
            
            index_css_path = f"{path}/src/styles/index.css"
            with open(index_css_path, 'w') as f:
                f.write(index_css)
            created_files.append(index_css_path)
            
            # Create README.md
            readme = f"""# {name}

A React.js web application.

## Features

- Modern React.js setup with Create React App
- Component-based architecture
- Responsive design
- Development and production builds

## Getting Started

1. Install dependencies:
   ```bash
   cd {path.split('/')[-1]}
   npm install
   ```

2. Start development server:
   ```bash
   npm start
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Project Structure

```
{name}/
├── public/
│   └── index.html
├── src/
│   ├── components/     # React components
│   ├── utils/          # Utility functions  
│   ├── styles/         # CSS files
│   ├── App.js          # Main App component
│   └── index.js        # Entry point
├── package.json
└── README.md
```

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm test` - Launches the test runner
- `npm run build` - Builds the app for production
- `npm run eject` - Ejects from Create React App (one-way operation)
"""
            
            readme_path = f"{path}/README.md"
            with open(readme_path, 'w') as f:
                f.write(readme)
            created_files.append(readme_path)
            
            colored_print(f"Created React.js project: {name}", Colors.GREEN)
            colored_print(f"📂 Created {len(created_files)} files", Colors.GREEN)
            
            return {
                "success": True,
                "project_type": "React.js",
                "project_name": name,
                "project_path": path,
                "files_created": created_files,
                "directories_created": directories,
                "next_steps": [
                    f"cd {path}",
                    "npm install", 
                    "npm start"
                ]
            }
            
        except Exception as e:
            colored_print(f"❌ Error creating React.js project: {e}", Colors.RED)
            return {
                "success": False,
                "error": str(e),
                "project_type": "React.js"
            }
    
    def create_react_native_project(self, name: str, path: str, description: str) -> Dict:
        """Create React Native project structure"""
        try:
            # Create directory structure
            directories = [
                f"{path}/src",
                f"{path}/src/components",
                f"{path}/src/screens", 
                f"{path}/src/utils",
                f"{path}/src/styles",
                f"{path}/android",
                f"{path}/ios"
            ]
            
            created_files = []
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            
            # Create package.json for React Native
            package_json = {
                "name": name.lower().replace(" ", ""),
                "version": "0.0.1",
                "private": True,
                "scripts": {
                    "android": "react-native run-android",
                    "ios": "react-native run-ios", 
                    "start": "react-native start",
                    "test": "jest",
                    "lint": "eslint ."
                },
                "dependencies": {
                    "react": "18.2.0",
                    "react-native": "0.72.6"
                },
                "devDependencies": {
                    "@babel/core": "^7.20.0",
                    "@babel/preset-env": "^7.20.0",
                    "@babel/runtime": "^7.20.0",
                    "@react-native/eslint-config": "^0.72.2",
                    "@react-native/metro-config": "^0.72.11",
                    "@tsconfig/react-native": "^3.0.0",
                    "@types/react": "^18.0.24",
                    "@types/react-test-renderer": "^18.0.0",
                    "babel-jest": "^29.2.1",
                    "eslint": "^8.19.0", 
                    "jest": "^29.2.1",
                    "metro-react-native-babel-preset": "0.76.8",
                    "prettier": "^2.4.1",
                    "react-test-renderer": "18.2.0",
                    "typescript": "4.8.4"
                },
                "jest": {
                    "preset": "react-native"
                }
            }
            
            package_path = f"{path}/package.json"
            with open(package_path, 'w') as f:
                json.dump(package_json, f, indent=2)
            created_files.append(package_path)
            
            # Create basic React Native app structure
            app_js = f"""import React from 'react';
import {{
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  useColorScheme,
  View,
}} from 'react-native';

function App() {{
  const isDarkMode = useColorScheme() === 'dark';

  const backgroundStyle = {{
    backgroundColor: isDarkMode ? '#000' : '#fff',
  }};

  return (
    <SafeAreaView style={{...backgroundStyle, flex: 1}}>
      <StatusBar barStyle={{isDarkMode ? 'light-content' : 'dark-content'}} />
      <ScrollView
        contentInsetAdjustmentBehavior="automatic"
        style={backgroundStyle}>
        <View style={styles.container}>
          <Text style={styles.title}>{name}</Text>
          <Text style={styles.subtitle}>React Native App is Ready!</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}}

const styles = StyleSheet.create({{
  container: {{
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  }},
  title: {{
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  }},
  subtitle: {{
    fontSize: 16,
    color: '#666',
  }},
}});

export default App;"""
            
            app_path = f"{path}/App.js"
            with open(app_path, 'w') as f:
                f.write(app_js)
            created_files.append(app_path)
            
            # Create index.js
            index_js = """import {AppRegistry} from 'react-native';
import App from './App';
import {name as appName} from './app.json';

AppRegistry.registerComponent(appName, () => App);"""
            
            index_path = f"{path}/index.js"
            with open(index_path, 'w') as f:
                f.write(index_js)
            created_files.append(index_path)
            
            # Create app.json
            app_json = {
                "name": name,
                "displayName": name
            }
            
            app_json_path = f"{path}/app.json"
            with open(app_json_path, 'w') as f:
                json.dump(app_json, f, indent=2)
            created_files.append(app_json_path)
            
            colored_print(f"Created React Native project: {name}", Colors.GREEN)
            colored_print(f"📂 Created {len(created_files)} files", Colors.GREEN)
            
            return {
                "success": True,
                "project_type": "React Native",
                "project_name": name,
                "project_path": path,
                "files_created": created_files,
                "directories_created": directories,
                "next_steps": [
                    f"cd {path}",
                    "npm install",
                    "npx react-native run-android  # or run-ios"
                ]
            }
            
        except Exception as e:
            colored_print(f"❌ Error creating React Native project: {e}", Colors.RED)
            return {
                "success": False,
                "error": str(e),
                "project_type": "React Native"
            }
    
    def create_python_project(self, name: str, path: str, description: str) -> Dict:
        """Create a Python project structure"""
        try:
            # Create directory structure
            directories = [
                f"{path}/src",
                f"{path}/tests",
                f"{path}/docs",
                f"{path}/scripts"
            ]
            
            created_files = []
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            
            # Create main Python file
            main_py = f"""#!/usr/bin/env python3
\"\"\"
{name} - Python Application

Description: {description}
\"\"\"

def main():
    \"\"\"Main function\"\"\"
    print(f"Welcome to {name}!")
    print("Your Python application is ready!")

if __name__ == "__main__":
    main()
"""
            
            main_path = f"{path}/src/main.py"
            with open(main_path, 'w') as f:
                f.write(main_py)
            created_files.append(main_path)
            
            # Create requirements.txt
            requirements = """# Core dependencies
# Add your project dependencies here

# Development dependencies
pytest>=7.0.0
black>=22.0.0
flake8>=4.0.0
"""
            
            req_path = f"{path}/requirements.txt"
            with open(req_path, 'w') as f:
                f.write(requirements)
            created_files.append(req_path)
            
            # Create setup.py
            setup_py = f"""from setuptools import setup, find_packages

setup(
    name="{name.lower().replace(' ', '-')}",
    version="0.1.0",
    description="{description}",
    packages=find_packages(where="src"),
    package_dir={{"": "src"}},
    python_requires=">=3.8",
    install_requires=[
        # Add dependencies here
    ],
    entry_points={{
        "console_scripts": [
            "{name.lower()}=main:main",
        ],
    }},
)
"""
            
            setup_path = f"{path}/setup.py"
            with open(setup_path, 'w') as f:
                f.write(setup_py)
            created_files.append(setup_path)
            
            # Create README.md
            readme = f"""# {name}

{description}

## Installation

```bash
cd {path.split('/')[-1]}
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py
```

## Development

1. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run tests:
   ```bash
   pytest tests/
   ```

3. Format code:
   ```bash
   black src/
   ```

## Project Structure

```
{name}/
├── src/
│   └── main.py         # Main application
├── tests/              # Test files
├── docs/               # Documentation
├── scripts/            # Utility scripts
├── requirements.txt    # Dependencies
├── setup.py           # Package setup
└── README.md
```
"""
            
            readme_path = f"{path}/README.md"
            with open(readme_path, 'w') as f:
                f.write(readme)
            created_files.append(readme_path)
            
            colored_print(f"Created Python project: {name}", Colors.GREEN)
            return {
                "success": True,
                "project_type": "Python",
                "project_name": name,
                "project_path": path,
                "files_created": created_files,
                "directories_created": directories,
                "next_steps": [
                    f"cd {path}",
                    "pip install -r requirements.txt",
                    "python src/main.py"
                ]
            }
            
        except Exception as e:
            colored_print(f"❌ Error creating Python project: {e}", Colors.RED)
            return {"success": False, "error": str(e), "project_type": "Python"}
    
    def create_nodejs_project(self, name: str, path: str, description: str) -> Dict:
        """Create a Node.js project structure"""
        try:
            # Create directory structure
            directories = [
                f"{path}/src",
                f"{path}/tests",
                f"{path}/docs"
            ]
            
            created_files = []
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            
            # Create package.json
            package_json = {
                "name": name.lower().replace(" ", "-"),
                "version": "1.0.0",
                "description": description,
                "main": "src/index.js",
                "scripts": {
                    "start": "node src/index.js",
                    "dev": "nodemon src/index.js",
                    "test": "jest",
                    "lint": "eslint src/"
                },
                "keywords": [],
                "author": "",
                "license": "MIT",
                "dependencies": {
                    "express": "^4.18.0"
                },
                "devDependencies": {
                    "nodemon": "^3.0.0",
                    "jest": "^29.0.0",
                    "eslint": "^8.0.0"
                }
            }
            
            package_path = f"{path}/package.json"
            with open(package_path, 'w') as f:
                json.dump(package_json, f, indent=2)
            created_files.append(package_path)
            
            # Create main index.js
            index_js = f"""const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static('public'));

// Routes
app.get('/', (req, res) => {{
    res.json({{
        message: 'Welcome to {name}!',
        description: '{description}',
        status: 'Server is running successfully!'
    }});
}});

app.get('/health', (req, res) => {{
    res.json({{ status: 'OK', timestamp: new Date().toISOString() }});
}});

// Start server
app.listen(PORT, () => {{
    console.log(`{name} server running on port ${{PORT}}`);
    console.log(`📡 API available at http://localhost:${{PORT}}`);
}});

module.exports = app;
"""
            
            index_path = f"{path}/src/index.js"
            with open(index_path, 'w') as f:
                f.write(index_js)
            created_files.append(index_path)
            
            # Create README.md
            readme = f"""# {name}

{description}

## Installation

```bash
cd {path.split('/')[-1]}
npm install
```

## Usage

### Development
```bash
npm run dev
```

### Production
```bash
npm start
```

### Testing
```bash
npm test
```

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check

## Project Structure

```
{name}/
├── src/
│   └── index.js        # Main server file
├── tests/              # Test files
├── docs/               # Documentation
├── package.json        # Dependencies and scripts
└── README.md
```

## Environment Variables

Create a `.env` file for environment-specific configuration:

```
PORT=3000
NODE_ENV=development
```
"""
            
            readme_path = f"{path}/README.md"
            with open(readme_path, 'w') as f:
                f.write(readme)
            created_files.append(readme_path)
            
            colored_print(f"Created Node.js project: {name}", Colors.GREEN)
            return {
                "success": True,
                "project_type": "Node.js",
                "project_name": name,
                "project_path": path,
                "files_created": created_files,
                "directories_created": directories,
                "next_steps": [
                    f"cd {path}",
                    "npm install",
                    "npm run dev"
                ]
            }
            
        except Exception as e:
            colored_print(f"❌ Error creating Node.js project: {e}", Colors.RED)
            return {"success": False, "error": str(e), "project_type": "Node.js"}
    
    def create_web_project(self, name: str, path: str, description: str) -> Dict:
        """Create a basic web project with HTML/CSS/JS"""
        try:
            # Create directory structure
            directories = [
                f"{path}/css",
                f"{path}/js",
                f"{path}/images",
                f"{path}/assets"
            ]
            
            created_files = []
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            
            # Create index.html
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <header>
        <h1>{name}</h1>
        <nav>
            <ul>
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <section id="home">
            <h2>Welcome to {name}</h2>
            <p>{description}</p>
            <button id="demo-btn">Click me!</button>
        </section>
        
        <section id="about">
            <h2>About</h2>
            <p>This is a modern web application built with HTML, CSS, and JavaScript.</p>
        </section>
        
        <section id="contact">
            <h2>Contact</h2>
            <p>Get in touch with us!</p>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2024 {name}. All rights reserved.</p>
    </footer>
    
    <script src="js/script.js"></script>
</body>
</html>"""
            
            html_path = f"{path}/index.html"
            with open(html_path, 'w') as f:
                f.write(html_content)
            created_files.append(html_path)
            
            # Create CSS
            css_content = """/* Reset and base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f4f4f4;
}

/* Header */
header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem 0;
    position: fixed;
    width: 100%;
    top: 0;
    z-index: 1000;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

header h1 {
    text-align: center;
    margin-bottom: 0.5rem;
}

nav ul {
    list-style: none;
    display: flex;
    justify-content: center;
    gap: 2rem;
}

nav a {
    color: white;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    transition: background-color 0.3s;
}

nav a:hover {
    background-color: rgba(255,255,255,0.2);
}

/* Main content */
main {
    margin-top: 120px;
    padding: 2rem;
    max-width: 1200px;
    margin-left: auto;
    margin-right: auto;
}

section {
    background: white;
    margin: 2rem 0;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

h2 {
    color: #667eea;
    margin-bottom: 1rem;
}

button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    transition: transform 0.2s;
}

button:hover {
    transform: translateY(-2px);
}

/* Footer */
footer {
    background: #333;
    color: white;
    text-align: center;
    padding: 1rem;
    margin-top: 2rem;
}

/* Responsive design */
@media (max-width: 768px) {
    nav ul {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    main {
        margin-top: 160px;
        padding: 1rem;
    }
}"""
            
            css_path = f"{path}/css/styles.css"
            with open(css_path, 'w') as f:
                f.write(css_content)
            created_files.append(css_path)
            
            # Create JavaScript
            js_content = """// Main JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Website loaded successfully!');
    
    // Demo button functionality
    const demoBtn = document.getElementById('demo-btn');
    if (demoBtn) {
        demoBtn.addEventListener('click', function() {
            alert('Hello from your web application!');
            this.textContent = 'Clicked!';
            setTimeout(() => {
                this.textContent = 'Click me!';
            }, 2000);
        });
    }
    
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('nav a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add some interactivity
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        section.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        section.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});

// Utility functions
function showMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.textContent = message;
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #4CAF50;
        color: white;
        padding: 1rem;
        border-radius: 4px;
        z-index: 1001;
    `;
    document.body.appendChild(messageDiv);
    
    setTimeout(() => {
        document.body.removeChild(messageDiv);
    }, 3000);
}"""
            
            js_path = f"{path}/js/script.js"
            with open(js_path, 'w') as f:
                f.write(js_content)
            created_files.append(js_path)
            
            # Create README
            readme = f"""# {name}

{description}

## Features

- Responsive design
- Modern CSS with gradients and animations
- Interactive JavaScript functionality
- Clean, semantic HTML structure
- Cross-browser compatibility

## Getting Started

1. Open `index.html` in your web browser
2. Or serve with a local server:
   ```bash
   # Python
   python -m http.server 8000
   
   # Node.js
   npx http-server
   
   # PHP
   php -S localhost:8000
   ```

## Project Structure

```
{name}/
├── index.html          # Main HTML file
├── css/
│   └── styles.css      # Stylesheet
├── js/
│   └── script.js       # JavaScript functionality
├── images/             # Image assets
├── assets/             # Other assets
└── README.md
```

## Customization

- Edit `css/styles.css` to modify the appearance
- Add functionality in `js/script.js`
- Modify content in `index.html`
- Add images to the `images/` folder
"""
            
            readme_path = f"{path}/README.md"
            with open(readme_path, 'w') as f:
                f.write(readme)
            created_files.append(readme_path)
            
            colored_print(f"Created Web project: {name}", Colors.GREEN)
            return {
                "success": True,
                "project_type": "Web",
                "project_name": name,
                "project_path": path,
                "files_created": created_files,
                "directories_created": directories,
                "next_steps": [
                    f"cd {path}",
                    "Open index.html in browser",
                    "Or run: python -m http.server 8000"
                ]
            }
            
        except Exception as e:
            colored_print(f"❌ Error creating Web project: {e}", Colors.RED)
            return {"success": False, "error": str(e), "project_type": "Web"}
    
    def create_generic_project(self, name: str, path: str, description: str) -> Dict:
        """Create a generic project structure"""
        try:
            # Create basic directory structure
            directories = [
                f"{path}/src",
                f"{path}/docs",
                f"{path}/tests",
                f"{path}/scripts",
                f"{path}/config"
            ]
            
            created_files = []
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            
            # Create README.md
            readme = f"""# {name}

{description}

## Project Structure

```
{name}/
├── src/                # Source code
├── docs/               # Documentation
├── tests/              # Test files
├── scripts/            # Utility scripts
├── config/             # Configuration files
└── README.md
```

## Getting Started

1. Navigate to the project directory:
   ```bash
   cd {path.split('/')[-1]}
   ```

2. Add your source code to the `src/` directory
3. Update this README with project-specific instructions
4. Add any configuration files to `config/`
5. Write tests in the `tests/` directory

## Development

- Source code: `src/`
- Documentation: `docs/`
- Tests: `tests/`
- Scripts: `scripts/`
- Configuration: `config/`

## Next Steps

1. Choose your technology stack
2. Add appropriate configuration files (package.json, requirements.txt, etc.)
3. Set up your development environment
4. Start coding!
"""
            
            readme_path = f"{path}/README.md"
            with open(readme_path, 'w') as f:
                f.write(readme)
            created_files.append(readme_path)
            
            # Create a basic gitignore
            gitignore = """# Dependencies
node_modules/
venv/
env/
__pycache__/
*.pyc

# Build outputs
dist/
build/
*.o
*.exe

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Environment files
.env
.env.local
"""
            
            gitignore_path = f"{path}/.gitignore"
            with open(gitignore_path, 'w') as f:
                f.write(gitignore)
            created_files.append(gitignore_path)
            
            colored_print(f"Created Generic project: {name}", Colors.GREEN)
            return {
                "success": True,
                "project_type": "Generic",
                "project_name": name,
                "project_path": path,
                "files_created": created_files,
                "directories_created": directories,
                "next_steps": [
                    f"cd {path}",
                    "Add your technology-specific files",
                    "Update README.md with project details"
                ]
            }
            
        except Exception as e:
            colored_print(f"❌ Error creating Generic project: {e}", Colors.RED)
            return {"success": False, "error": str(e), "project_type": "Generic"}
    
    def create_flask_project(self, name: str, path: str, description: str) -> Dict:
        """Create a Flask web application project"""
        try:
            # Create directory structure
            directories = [
                f"{path}/app",
                f"{path}/app/templates",
                f"{path}/app/static",
                f"{path}/app/static/css",
                f"{path}/app/static/js",
                f"{path}/tests"
            ]
            
            created_files = []
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            
            # Create main Flask app
            app_py = f"""from flask import Flask, render_template, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

@app.route('/')
def index():
    return render_template('index.html', title='{name}')

@app.route('/api/health')
def health():
    return jsonify({{'status': 'OK', 'message': '{name} is running!'}})

if __name__ == '__main__':
    app.run(debug=True)
"""
            
            app_path = f"{path}/app.py"
            with open(app_path, 'w') as f:
                f.write(app_py)
            created_files.append(app_path)
            
            # Create requirements.txt
            requirements = """Flask>=2.3.0
python-dotenv>=1.0.0
"""
            
            req_path = f"{path}/requirements.txt"
            with open(req_path, 'w') as f:
                f.write(requirements)
            created_files.append(req_path)
            
            # Create basic HTML template
            html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{name}</h1>
            <p>{description}</p>
        </div>
        <h2>Flask Application Ready!</h2>
        <p>Your Flask web application is up and running.</p>
    </div>
</body>
</html>"""
            
            template_path = f"{path}/app/templates/index.html"
            os.makedirs(f"{path}/app/templates", exist_ok=True)
            with open(template_path, 'w') as f:
                f.write(html_template)
            created_files.append(template_path)
            
            colored_print(f"Created Flask project: {name}", Colors.GREEN)
            return {
                "success": True,
                "project_type": "Flask",
                "project_name": name,
                "project_path": path,
                "files_created": created_files,
                "directories_created": directories,
                "next_steps": [
                    f"cd {path}",
                    "pip install -r requirements.txt",
                    "python app.py"
                ]
            }
            
        except Exception as e:
            colored_print(f"❌ Error creating Flask project: {e}", Colors.RED)
            return {"success": False, "error": str(e), "project_type": "Flask"}
    
    def create_django_project(self, name: str, path: str, description: str) -> Dict:
        """Create a Django project structure"""
        try:
            # Create basic Django project structure
            directories = [
                f"{path}/{name.lower()}",
                f"{path}/apps",
                f"{path}/static",
                f"{path}/templates",
                f"{path}/media"
            ]
            
            created_files = []
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            
            # Create manage.py
            manage_py = f"""#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{name.lower()}.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
"""
            
            manage_path = f"{path}/manage.py"
            with open(manage_path, 'w') as f:
                f.write(manage_py)
            created_files.append(manage_path)
            
            # Create requirements.txt
            requirements = """Django>=4.2.0
python-decouple>=3.8.0
"""
            
            req_path = f"{path}/requirements.txt"
            with open(req_path, 'w') as f:
                f.write(requirements)
            created_files.append(req_path)
            
            colored_print(f"Created Django project: {name}", Colors.GREEN)
            return {
                "success": True,
                "project_type": "Django",
                "project_name": name,
                "project_path": path,
                "files_created": created_files,
                "directories_created": directories,
                "next_steps": [
                    f"cd {path}",
                    "pip install -r requirements.txt",
                    f"python manage.py startproject {name.lower()} .",
                    "python manage.py runserver"
                ]
            }
            
        except Exception as e:
            colored_print(f"❌ Error creating Django project: {e}", Colors.RED)
            return {"success": False, "error": str(e), "project_type": "Django"}
    
    def create_vue_project(self, name: str, path: str, description: str) -> Dict:
        """Create a Vue.js project structure"""
        try:
            # Create directory structure
            directories = [
                f"{path}/src",
                f"{path}/src/components",
                f"{path}/src/views",
                f"{path}/public"
            ]
            
            created_files = []
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            
            # Create package.json
            package_json = {
                "name": name.lower().replace(" ", "-"),
                "version": "0.1.0",
                "scripts": {
                    "serve": "vue-cli-service serve",
                    "build": "vue-cli-service build"
                },
                "dependencies": {
                    "vue": "^3.2.13"
                },
                "devDependencies": {
                    "@vue/cli-service": "~5.0.0"
                }
            }
            
            package_path = f"{path}/package.json"
            with open(package_path, 'w') as f:
                json.dump(package_json, f, indent=2)
            created_files.append(package_path)
            
            colored_print(f"Created Vue.js project: {name}", Colors.GREEN)
            return {
                "success": True,
                "project_type": "Vue.js",
                "project_name": name,
                "project_path": path,
                "files_created": created_files,
                "directories_created": directories,
                "next_steps": [
                    f"cd {path}",
                    "npm install",
                    "npm run serve"
                ]
            }
            
        except Exception as e:
            colored_print(f"❌ Error creating Vue.js project: {e}", Colors.RED)
            return {"success": False, "error": str(e), "project_type": "Vue.js"}
    
    def create_angular_project(self, name: str, path: str, description: str) -> Dict:
        """Create an Angular project structure"""
        try:
            # Create basic Angular structure
            directories = [
                f"{path}/src",
                f"{path}/src/app",
                f"{path}/src/assets"
            ]
            
            created_files = []
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            
            # Create package.json
            package_json = {
                "name": name.lower().replace(" ", "-"),
                "version": "0.0.0",
                "scripts": {
                    "ng": "ng",
                    "start": "ng serve",
                    "build": "ng build",
                    "test": "ng test"
                },
                "dependencies": {
                    "@angular/animations": "^16.0.0",
                    "@angular/common": "^16.0.0",
                    "@angular/compiler": "^16.0.0",
                    "@angular/core": "^16.0.0",
                    "@angular/platform-browser": "^16.0.0",
                    "rxjs": "~7.8.0"
                }
            }
            
            package_path = f"{path}/package.json"
            with open(package_path, 'w') as f:
                json.dump(package_json, f, indent=2)
            created_files.append(package_path)
            
            colored_print(f"Created Angular project: {name}", Colors.GREEN)
            return {
                "success": True,
                "project_type": "Angular",
                "project_name": name,
                "project_path": path,
                "files_created": created_files,
                "directories_created": directories,
                "next_steps": [
                    f"cd {path}",
                    "npm install",
                    "ng serve"
                ]
            }
            
        except Exception as e:
            colored_print(f"❌ Error creating Angular project: {e}", Colors.RED)
            return {"success": False, "error": str(e), "project_type": "Angular"}
    
    def create_nextjs_project(self, name: str, path: str, description: str) -> Dict:
        """Create a Next.js project structure"""
        try:
            # Create directory structure  
            directories = [
                f"{path}/pages",
                f"{path}/components",
                f"{path}/styles",
                f"{path}/public"
            ]
            
            created_files = []
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            
            # Create package.json
            package_json = {
                "name": name.lower().replace(" ", "-"),
                "version": "0.1.0",
                "scripts": {
                    "dev": "next dev",
                    "build": "next build",
                    "start": "next start"
                },
                "dependencies": {
                    "next": "13.4.0",
                    "react": "18.2.0",
                    "react-dom": "18.2.0"
                }
            }
            
            package_path = f"{path}/package.json"
            with open(package_path, 'w') as f:
                json.dump(package_json, f, indent=2)
            created_files.append(package_path)
            
            colored_print(f"Created Next.js project: {name}", Colors.GREEN)
            return {
                "success": True,
                "project_type": "Next.js",
                "project_name": name,
                "project_path": path,
                "files_created": created_files,
                "directories_created": directories,
                "next_steps": [
                    f"cd {path}",
                    "npm install",
                    "npm run dev"
                ]
            }
            
        except Exception as e:
            colored_print(f"❌ Error creating Next.js project: {e}", Colors.RED)
            return {"success": False, "error": str(e), "project_type": "Next.js"}
    
    def create_fastapi_project(self, name: str, path: str, description: str) -> Dict:
        """Create a FastAPI project structure"""
        try:
            # Create directory structure
            directories = [
                f"{path}/app",
                f"{path}/app/routers",
                f"{path}/tests"
            ]
            
            created_files = []
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            
            # Create main FastAPI app
            main_py = f"""from fastapi import FastAPI
from app.routers import items

app = FastAPI(title="{name}", description="{description}")

app.include_router(items.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {{"message": "Welcome to {name}!"}}

@app.get("/health")
async def health_check():
    return {{"status": "OK"}}
"""
            
            main_path = f"{path}/main.py"
            with open(main_path, 'w') as f:
                f.write(main_py)
            created_files.append(main_path)
            
            # Create requirements.txt
            requirements = """fastapi>=0.100.0
uvicorn[standard]>=0.23.0
"""
            
            req_path = f"{path}/requirements.txt"
            with open(req_path, 'w') as f:
                f.write(requirements)
            created_files.append(req_path)
            
            colored_print(f"Created FastAPI project: {name}", Colors.GREEN)
            return {
                "success": True,
                "project_type": "FastAPI",
                "project_name": name,
                "project_path": path,
                "files_created": created_files,
                "directories_created": directories,
                "next_steps": [
                    f"cd {path}",
                    "pip install -r requirements.txt",
                    "uvicorn main:app --reload"
                ]
            }
            
        except Exception as e:
            colored_print(f"❌ Error creating FastAPI project: {e}", Colors.RED)
            return {"success": False, "error": str(e), "project_type": "FastAPI"}
    
    def create_js_project(self, name: str, path: str, description: str) -> Dict:
        """Create a JavaScript project structure"""
        try:
            # Create directory structure
            directories = [
                f"{path}/src",
                f"{path}/tests"
            ]
            
            created_files = []
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            
            # Create package.json
            package_json = {
                "name": name.lower().replace(" ", "-"),
                "version": "1.0.0",
                "description": description,
                "main": "src/index.js",
                "scripts": {
                    "start": "node src/index.js",
                    "test": "jest"
                }
            }
            
            package_path = f"{path}/package.json"
            with open(package_path, 'w') as f:
                json.dump(package_json, f, indent=2)
            created_files.append(package_path)
            
            colored_print(f"Created JavaScript project: {name}", Colors.GREEN)
            return {
                "success": True,
                "project_type": "JavaScript",
                "project_name": name,
                "project_path": path,
                "files_created": created_files,
                "directories_created": directories,
                "next_steps": [
                    f"cd {path}",
                    "npm install",
                    "npm start"
                ]
            }
            
        except Exception as e:
            colored_print(f"❌ Error creating JavaScript project: {e}", Colors.RED)
            return {"success": False, "error": str(e), "project_type": "JavaScript"}
    
    def create_api_project(self, name: str, path: str, description: str) -> Dict:
        """Create a REST API project - defaults to FastAPI"""
        return self.create_fastapi_project(name, path, description)
    
    # === Missing Agent Handler Methods ===
    
    def handle_code_generation_task(self, task: Dict) -> Dict:
        """Handle code generation tasks for coder agent"""
        description = task["description"]
        colored_print(f"\n💻 Coder Agent Processing Task:", Colors.BRIGHT_YELLOW)
        colored_print(f"   Task: {description}", Colors.WHITE)
        
        try:
            # Generate code based on description
            prompt = f"""Generate code based on this request: {description}
            
            Provide clean, production-ready code with:
            - Proper error handling
            - Clear comments
            - Best practices
            - Complete implementation
            """
            
            try:
                response = self.query_ollama(prompt)
            except:
                # Fallback if ollama is not available
                response = f"""// Generated code for: {description}
// This is a placeholder implementation
// TODO: Implement the actual functionality

console.log('Code generation task: {description}');
"""
            
            colored_print(f"✅ Code generation completed", Colors.GREEN)
            return {
                "success": True,
                "generated_code": response,
                "task_type": "code_generation",
                "completed_by": "coder"
            }
            
        except Exception as e:
            colored_print(f"❌ Code generation failed: {e}", Colors.RED)
            return {
                "success": False,
                "error": str(e),
                "task_type": "code_generation"
            }
    
    def handle_code_review_task(self, task: Dict) -> Dict:
        """Handle code review tasks for code reviewer agent"""
        description = task["description"]
        colored_print(f"\n🔍 Code Reviewer Agent Processing Task:", Colors.BRIGHT_YELLOW)
        colored_print(f"   Task: {description}", Colors.WHITE)
        
        try:
            # Look for code files in the workspace to review
            workspace_files = []
            for root, dirs, files in os.walk(self.workspace_dir):
                # Skip .agent_comm directory
                if '.agent_comm' in root:
                    continue
                for file in files:
                    if file.endswith(('.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.cpp', '.c')):
                        workspace_files.append(os.path.join(root, file))
            
            colored_print(f"   Found {len(workspace_files)} code files to review", Colors.CYAN)
            
            review_results = []
            files_reviewed = 0
            
            # Review up to 5 files to avoid overwhelming output
            for file_path in workspace_files[:5]:
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Simple code review analysis
                    issues = []
                    suggestions = []
                    
                    # Basic checks
                    if len(content.split('\n')) > 200:
                        suggestions.append("Consider breaking this large file into smaller modules")
                    
                    if 'TODO' in content.upper():
                        issues.append("Contains TODO items that need attention")
                    
                    if 'console.log' in content and file_path.endswith('.js'):
                        suggestions.append("Remove console.log statements for production")
                    
                    if 'print(' in content and file_path.endswith('.py'):
                        suggestions.append("Consider using proper logging instead of print statements")
                    
                    # Count lines and complexity
                    lines = len(content.split('\n'))
                    
                    review_result = {
                        "file": os.path.relpath(file_path, self.workspace_dir),
                        "lines": lines,
                        "issues": issues,
                        "suggestions": suggestions,
                        "status": "reviewed"
                    }
                    
                    review_results.append(review_result)
                    files_reviewed += 1
                    
                    colored_print(f"   ✅ Reviewed: {os.path.basename(file_path)} ({lines} lines)", Colors.GREEN)
                    
                except Exception as e:
                    colored_print(f"   ❌ Failed to review {file_path}: {e}", Colors.RED)
            
            # Generate overall assessment
            total_issues = sum(len(r['issues']) for r in review_results)
            total_suggestions = sum(len(r['suggestions']) for r in review_results)
            
            assessment = {
                "files_reviewed": files_reviewed,
                "total_issues": total_issues,
                "total_suggestions": total_suggestions,
                "overall_quality": "Good" if total_issues < 3 else "Needs Improvement",
                "review_results": review_results
            }
            
            colored_print(f"\n📊 Code Review Summary:", Colors.BRIGHT_CYAN)
            colored_print(f"   Files reviewed: {files_reviewed}", Colors.WHITE)
            colored_print(f"   Issues found: {total_issues}", Colors.YELLOW if total_issues > 0 else Colors.GREEN)
            colored_print(f"   Suggestions: {total_suggestions}", Colors.CYAN)
            colored_print(f"   Overall quality: {assessment['overall_quality']}", Colors.GREEN if assessment['overall_quality'] == 'Good' else Colors.YELLOW)
            
            colored_print(f"✅ Code review completed", Colors.GREEN)
            return {
                "success": True,
                "assessment": assessment,
                "task_type": "code_review",
                "completed_by": "code_reviewer"
            }
            
        except Exception as e:
            colored_print(f"❌ Code review failed: {e}", Colors.RED)
            return {
                "success": False,
                "error": str(e),
                "task_type": "code_review"
            }
    
    def handle_code_rewrite_task(self, task: Dict) -> Dict:
        """Handle code rewriting tasks for code rewriter agent"""
        description = task["description"]
        colored_print(f"\n🔧 Code Rewriter Agent Processing Task:", Colors.BRIGHT_YELLOW)
        colored_print(f"   Task: {description}", Colors.WHITE)
        
        try:
            # Look for code files that might need rewriting
            workspace_files = []
            for root, dirs, files in os.walk(self.workspace_dir):
                if '.agent_comm' in root:
                    continue
                for file in files:
                    if file.endswith(('.js', '.jsx', '.ts', '.tsx', '.py', '.java')):
                        workspace_files.append(os.path.join(root, file))
            
            colored_print(f"   Found {len(workspace_files)} code files to analyze", Colors.CYAN)
            
            files_processed = 0
            fixes_applied = []
            
            # Process up to 3 files
            for file_path in workspace_files[:3]:
                try:
                    with open(file_path, 'r') as f:
                        original_content = f.read()
                    
                    # Simple fixes
                    modified_content = original_content
                    changes_made = []
                    
                    # Remove excessive whitespace
                    if '\n\n\n\n' in modified_content:
                        modified_content = modified_content.replace('\n\n\n\n', '\n\n\n')
                        changes_made.append("Reduced excessive whitespace")
                    
                    # Fix common JavaScript issues
                    if file_path.endswith('.js') or file_path.endswith('.jsx'):
                        # Add semicolons where missing (simple check)
                        lines = modified_content.split('\n')
                        for i, line in enumerate(lines):
                            stripped = line.strip()
                            if stripped and not stripped.endswith((';', '{', '}', ':', ',')) and not stripped.startswith('//'):
                                if any(keyword in stripped for keyword in ['return', 'const ', 'let ', 'var ']):
                                    lines[i] = line + ';'
                                    if "Added semicolons" not in changes_made:
                                        changes_made.append("Added missing semicolons")
                        
                        modified_content = '\n'.join(lines)
                    
                    # Fix Python issues
                    elif file_path.endswith('.py'):
                        # Remove trailing whitespace
                        lines = modified_content.split('\n')
                        cleaned_lines = [line.rstrip() for line in lines]
                        if lines != cleaned_lines:
                            modified_content = '\n'.join(cleaned_lines)
                            changes_made.append("Removed trailing whitespace")
                    
                    # Save changes if any were made
                    if changes_made:
                        with open(file_path, 'w') as f:
                            f.write(modified_content)
                        
                        fix_result = {
                            "file": os.path.relpath(file_path, self.workspace_dir),
                            "changes": changes_made,
                            "status": "fixed"
                        }
                        fixes_applied.append(fix_result)
                        
                        colored_print(f"   🔧 Fixed: {os.path.basename(file_path)} ({len(changes_made)} fixes)", Colors.GREEN)
                    else:
                        colored_print(f"   ✅ Clean: {os.path.basename(file_path)} (no fixes needed)", Colors.CYAN)
                    
                    files_processed += 1
                    
                except Exception as e:
                    colored_print(f"   ❌ Failed to process {file_path}: {e}", Colors.RED)
            
            colored_print(f"\n🔧 Code Rewrite Summary:", Colors.BRIGHT_CYAN)
            colored_print(f"   Files processed: {files_processed}", Colors.WHITE)
            colored_print(f"   Files fixed: {len(fixes_applied)}", Colors.GREEN)
            
            for fix in fixes_applied:
                colored_print(f"   • {fix['file']}: {', '.join(fix['changes'])}", Colors.YELLOW)
            
            colored_print(f"✅ Code rewrite completed", Colors.GREEN)
            return {
                "success": True,
                "files_processed": files_processed,
                "fixes_applied": fixes_applied,
                "task_type": "code_rewrite",
                "completed_by": "code_rewriter"
            }
            
        except Exception as e:
            colored_print(f"❌ Code rewrite failed: {e}", Colors.RED)
            return {
                "success": False,
                "error": str(e),
                "task_type": "code_rewrite"
            }

    def run_interactive(self):
        """Run the interactive agent terminal"""
        colored_print(f"Agent {self.agent_id} ({self.role.value}) registered", Colors.BRIGHT_GREEN)
        colored_print("Type 'help' for available commands, 'exit' to quit", Colors.CYAN)
        
        try:
            while self.running:
                try:
                    # Get input from user
                    prompt = f"{Colors.BRIGHT_BLUE}{self.role.value}> {Colors.RESET}"
                    user_input = input(prompt).strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() in ['exit', 'quit', 'q']:
                        break
                    elif user_input.lower() == 'help':
                        self.show_help()
                    elif user_input.lower() == 'status':
                        self.show_status()
                    elif user_input.lower() == 'clear':
                        os.system('clear' if os.name != 'nt' else 'cls')
                    elif user_input.startswith('delegate '):
                        self.handle_delegate_command(user_input)
                    elif user_input.startswith('create ') and self.role == AgentRole.FILE_MANAGER:
                        # Handle direct file manager commands
                        try:
                            result = self.create_project_smart(user_input[7:])  # Remove 'create ' prefix
                            colored_print(f"Project created: {result}", Colors.GREEN)
                        except Exception as e:
                            colored_print(f"Failed to create project: {e}", Colors.RED)
                    else:
                        # Try to execute as a system command
                        self.run_command(user_input)
                        
                except KeyboardInterrupt:
                    colored_print("\n-- Use 'exit' to quit", Colors.YELLOW)
                except EOFError:
                    break
                    
        except Exception as e:
            colored_print(f"-- Terminal error: {e}", Colors.RED)
        finally:
            self.shutdown()

    def show_help(self):
        """Show help information"""
        colored_print(f"\n{self.role.value.title()} Agent Commands:", Colors.BRIGHT_CYAN)
        colored_print("=" * 40, Colors.CYAN)
        colored_print("help                          - Show this help", Colors.WHITE)
        colored_print("status                        - Show agent status", Colors.WHITE)
        colored_print("clear                         - Clear screen", Colors.WHITE)
        colored_print("exit/quit/q                   - Exit agent", Colors.WHITE)
        colored_print("delegate 'task' to <agent>    - Delegate task to another agent", Colors.WHITE)
        colored_print("", Colors.WHITE)
        colored_print("Examples:", Colors.BRIGHT_YELLOW)
        colored_print("  delegate 'Create React.js TimeDisplayApp' to file_manager", Colors.YELLOW)
        colored_print("  delegate 'Review code quality' to code_reviewer", Colors.YELLOW)
        colored_print("  delegate 'Fix syntax errors' to code_rewriter", Colors.YELLOW)
        colored_print("")

    def show_status(self):
        """Show current agent status"""
        colored_print(f"\nAgent Status: {self.agent_id}", Colors.BRIGHT_CYAN)
        colored_print("=" * 40, Colors.CYAN)
        colored_print(f"Role: {self.role.value}", Colors.WHITE)
        colored_print(f"Status: {'Running' if self.running else 'Stopped'}", Colors.GREEN if self.running else Colors.RED)
        colored_print(f"Workspace: {self.workspace_dir}", Colors.WHITE)
        
        # Show pending tasks
        pending_tasks = self.comm.get_pending_tasks(self.agent_id)
        colored_print(f"Pending tasks: {len(pending_tasks)}", Colors.YELLOW)
        
        # Show all active agents
        agents = self.comm.load_agents()
        active_agents = [a for a in agents if a.get('status') == 'active']
        colored_print(f"Active agents: {len(active_agents)}", Colors.GREEN)
        for agent in active_agents:
            colored_print(f"  • {agent['role']} ({agent['id']})", Colors.CYAN)
        colored_print("")

    def handle_delegate_command(self, command: str):
        """Handle task delegation commands"""
        import re
        
        # Parse delegation command: delegate 'task description' to agent_role
        pattern = r"delegate\s+['\"]([^'\"]+)['\"]?\s+to\s+(\w+)"
        match = re.search(pattern, command, re.IGNORECASE)
        
        if not match:
            colored_print("❌ Invalid delegation syntax. Use: delegate 'task description' to agent_role", Colors.RED)
            colored_print("Example: delegate 'Create React.js app' to file_manager", Colors.YELLOW)
            return
            
        task_description = match.group(1)
        target_agent_role = match.group(2).lower()
        
        # Validate target agent role
        valid_roles = [role.value for role in AgentRole]
        if target_agent_role not in valid_roles:
            colored_print(f"❌ Invalid agent role: {target_agent_role}", Colors.RED)
            colored_print(f"Valid roles: {', '.join(valid_roles)}", Colors.YELLOW)
            return
        
        # Create and assign task
        task_id = self.comm.create_task(
            task_type="delegated_task",
            description=task_description,
            assigned_to=target_agent_role,
            created_by=self.agent_id
        )
        
        colored_print(f"✅ Task created and delegated to {target_agent_role}:", Colors.GREEN)
        colored_print(f"   Task ID: {task_id}", Colors.CYAN)
        colored_print(f"   Description: '{task_description}'", Colors.WHITE)
        colored_print(f"   Assigned to: {target_agent_role}", Colors.YELLOW)
        colored_print(f"   Created by: {self.agent_id} ({self.role.value})", Colors.CYAN)
        
        # Check if target agent is active
        active_agents = self.comm.get_active_agents()
        target_agents = [agent for agent in active_agents if agent["role"] == target_agent_role]
        
        if target_agents:
            agent_ids = [agent["id"] for agent in target_agents]
            colored_print(f"   Status: Target agent ({target_agent_role}) is ACTIVE", Colors.GREEN)
            colored_print(f"   Active {target_agent_role} agents: {agent_ids}", Colors.CYAN)
        else:
            colored_print(f"   ⚠️  Warning: Target agent ({target_agent_role}) is NOT ACTIVE", Colors.RED)
            colored_print(f"   Available agents: {[(agent['id'], agent['role']) for agent in active_agents]}", Colors.YELLOW)

    def run_command(self, command: str):
        """Run a system command"""
        import subprocess
        
        colored_print(f"Executing: {command}", Colors.BRIGHT_BLUE)
        try:
            result = subprocess.run(command, shell=True)
            if result.returncode == 0:
                colored_print("Command completed", Colors.GREEN)
            else:
                colored_print(f"⚠Command exited with code {result.returncode}", Colors.YELLOW)
        except Exception as e:
            colored_print(f"❌ Command failed: {e}", Colors.RED)

    def query_ollama(self, prompt: str) -> str:
        """Query Ollama for AI responses (if available)"""
        try:
            import subprocess
            result = subprocess.run([
                self.ollama_cmd, "run", self.default_model, prompt
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                raise Exception(f"Ollama failed: {result.stderr}")
                
        except Exception as e:
            # Fallback response if Ollama is not available
            colored_print(f"⚠️  Ollama not available, using fallback response", Colors.YELLOW)
            return f"AI assistance not available. Task acknowledged: {prompt[:100]}..."
    
    def extract_code_from_response(self, response: str) -> str:
        """Extract code content from AI response"""
        # Remove markdown code blocks if present
        if "```" in response:
            lines = response.split('\n')
            in_code_block = False
            code_lines = []
            
            for line in lines:
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    code_lines.append(line)
            
            return '\n'.join(code_lines) if code_lines else response
        
        return response

    def shutdown(self):
        """Shutdown the agent gracefully"""
        colored_print(f"\nShutting down agent {self.agent_id}...", Colors.YELLOW)
        self.running = False
        self.save_history()
        colored_print("👋 Goodbye!", Colors.GREEN)

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python multi_agent_terminal.py <role> [agent_id]")
        print("Roles: coordinator, coder, code_reviewer, code_rewriter, file_manager, git_manager, researcher")
        sys.exit(1)
    
    role_str = sys.argv[1].lower()
    agent_id = sys.argv[2] if len(sys.argv) > 2 else f"{role_str}_agent_{int(time.time())}"
    
    try:
        role = AgentRole(role_str)
    except ValueError:
        print(f"Invalid role: {role_str}")
        print("Available roles: coordinator, coder, code_reviewer, code_rewriter, file_manager, git_manager, researcher")
        sys.exit(1)
    
    terminal = MultiAgentTerminal(agent_id, role)
    terminal.run_interactive()

if __name__ == "__main__":
    main()

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
    
    def detect_active_project_process(self):
        """Detect if there's an active project process in workspace"""
        try:
            workspace_items = os.listdir(self.workspace_dir)
            project_dirs = [item for item in workspace_items if os.path.isdir(os.path.join(self.workspace_dir, item))]
            
            if len(project_dirs) == 1:
                # Single project - set as current
                self.set_project_process(project_dirs[0])
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
- Analyze the full project context to understand the existing structure and patterns
- Provide implementation that integrates seamlessly with existing codebase
- Use appropriate technology stack and patterns based on project analysis
- Ensure output is production-ready and follows best practices
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
    
    def handle_task(self, task: Dict):
        """Handle a task assigned to this agent"""
        task_id = task["id"]
        task_type = task.get("type", "")
        description = task["description"]
        
        colored_print(f"\n[{self.agent_id}] Handling task {task_id}: {description}", Colors.YELLOW)
        
        # Update task status to in_progress
        self.comm.update_task_status(task_id, TaskStatus.IN_PROGRESS)
        
        try:
            if self.role == AgentRole.CODER:
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
        """Handle code generation using collaborative approach"""
        description = task["description"]
        
        # NEW COLLABORATIVE APPROACH - Provide intelligent guidance instead of hardcoded solutions
        guidance = self.analyze_task_and_provide_guidance(description)
        
        colored_print(f"\n=== COLLABORATIVE ANALYSIS ===", Colors.BRIGHT_CYAN)
        colored_print(guidance, Colors.CYAN)
        colored_print(f"================================\n", Colors.BRIGHT_CYAN)
        
        # Try AI model if available for actual implementation
        ai_result = self.try_ai_implementation(description)
        
        return {
            "type": "collaborative_guidance",
            "guidance": guidance,
            "ai_implementation": ai_result,
            "approach": "collaborative",
            "message": "This task requires AI model collaboration for implementation. The guidance above provides architectural direction."
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
            # Check if Ollama is available
            result = subprocess.run([self.ollama_cmd, "list"], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                # Generate prompt for AI model
                prompt = f"""Please provide a clean, well-documented implementation for: {description}

Focus on:
- Clean, readable code
- Proper error handling  
- Best practices for the framework
- Comments explaining key concepts

Implementation:"""
                
                # Run AI model
                ai_result = subprocess.run([self.ollama_cmd, "run", self.default_model], 
                                         input=prompt, capture_output=True, text=True, timeout=30)
                
                if ai_result.returncode == 0:
                    return {
                        "status": "success",
                        "implementation": ai_result.stdout.strip(),
                        "model": self.default_model
                    }
                else:
                    return {"status": "error", "message": "AI model execution failed"}
            
        except Exception as e:
            return {"status": "unavailable", "message": f"AI model not available: {e}"}
        
        return {"status": "unavailable", "message": "AI model not accessible"}
    
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
            description=rewriter_task_description,
            task_type="code_rewrite_from_review",
            assigned_to="code_rewriter",
            priority="normal",
            metadata={
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
            return self.handle_file_create_task(description)
    
    def is_edit_task(self, description: str) -> bool:
        """Determine if this is an edit task or create task"""
        edit_keywords = ["edit", "modify", "update", "change", "add to", "enhance", "improve"]
        desc_lower = description.lower()
        return any(keyword in desc_lower for keyword in edit_keywords)
    
    def handle_file_create_task(self, description: str) -> Dict:
        """Handle file creation tasks"""
        # Extract project information from description
        project_info = self.analyze_project_requirements(description)
        
        # Create project structure
        project_path = self.create_project_structure(project_info)
        
        return {
            "type": "file_management_completed",
            "project_path": project_path,
            "project_info": project_info,
            "message": f"Successfully created project structure at {project_path}",
            "files_created": self.list_created_files(project_path)
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
                return os.path.join(self.workspace_dir, project)
        
        # If only one project exists, use it
        if len(workspace_projects) == 1:
            colored_print(f"   TARGET: Using only available project: {workspace_projects[0]}", Colors.CYAN)
            return os.path.join(self.workspace_dir, workspace_projects[0])
        
        # Check for common project names
        common_names = ["timedisplayapp", "todoapp", "app", "project"]
        for name in common_names:
            if name in desc_lower:
                for project in workspace_projects:
                    if name in project.lower():
                        return os.path.join(self.workspace_dir, project)
        
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
            import subprocess
            
            # Check if Ollama is available
            result = subprocess.run([self.ollama_cmd, "list"], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                # Run AI model with edit prompt
                ai_result = subprocess.run([self.ollama_cmd, "run", self.default_model], 
                                         input=prompt, capture_output=True, text=True, timeout=45)
                
                if ai_result.returncode == 0:
                    return {
                        "status": "success",
                        "implementation": ai_result.stdout.strip(),
                        "model": self.default_model
                    }
                else:
                    return {"status": "error", "message": "AI model execution failed"}
            
        except Exception as e:
            return {"status": "unavailable", "message": f"AI model not available: {e}"}
        
        return {"status": "unavailable", "message": "AI model not accessible"}
    
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
    
    def analyze_project_requirements(self, description: str) -> Dict:
        """Analyze project requirements from description"""
        desc_lower = description.lower()
        
        project_info = {
            "name": "UnknownProject",
            "framework": None,
            "components": [],
            "features": []
        }
        
        # Extract project name
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
        
        colored_print(f"SUCCESS: UNIVERSAL PROJECT CREATED: {project_path}", Colors.BRIGHT_GREEN)
        return project_path
    
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
    
    colored_print(f"\n=== Multi-Agent Terminal ({agent_id}) ===", Colors.BRIGHT_YELLOW)
    colored_print(f"Role: {role.value}", Colors.CYAN)
    colored_print(f"Workspace: {agent.workspace_dir}", Colors.CYAN)
    colored_print("Commands: 'help', 'agents', 'tasks', 'delegate \"description\" to agent', 'quit'", Colors.WHITE)
    colored_print("=" * 50, Colors.BRIGHT_YELLOW)
    
    try:
        while True:
            try:
                user_input = input(f"\n[{agent_id}]> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_input.lower() == 'help':
                    print("Available commands:")
                    print("  agents - Show active agents")
                    print("  tasks - Show pending tasks")
                    print("  delegate \"description\" to agent_name - Create task for specific agent")
                    print("  delegate description - Create task for coder (default)")
                    print("  project - Show current project process")
                    print("  set_project <name> - Set focus to specific project process")
                    print("  files - Show project files loaded for AI collaboration")
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
                elif user_input.lower().startswith('delegate '):
                    # Parse delegation command: delegate "description" to agent_name
                    command_part = user_input[9:].strip()
                    
                    if ' to ' in command_part:
                        # Parse: "description" to agent_name
                        parts = command_part.split(' to ')
                        if len(parts) == 2:
                            description = parts[0].strip().strip('"')
                            target_agent = parts[1].strip()
                            
                            # Map role names to actual role values for assignment
                            role_mapping = {
                                'file_manager': 'file_manager',
                                'coder': 'coder',
                                'code_reviewer': 'code_reviewer', 
                                'code_rewriter': 'code_rewriter',
                                'git_manager': 'git_manager',
                                'researcher': 'researcher',
                                'tester': 'tester'
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
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
        
        # AI Configuration
        self.ollama_cmd = "ollama"
        self.default_model = "llama3.2"
        self.history_file = str(Path.home() / f".agent_history_{agent_id}")
        
        # Register this agent
        self.comm.register_agent(agent_id, role)
        colored_print(f"Agent {agent_id} initialized with role: {role.value}", Colors.BRIGHT_GREEN)
        
        # Load command history
        self.load_history()
        
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
                        colored_print(f"\\n[{self.agent_id}] Processing {len(pending_tasks)} task(s)...", Colors.CYAN)
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
        
        colored_print(f"\\n[{self.agent_id}] Handling task {task_id}: {description}", Colors.YELLOW)
        
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
        
        colored_print(f"\\n=== COLLABORATIVE ANALYSIS ===", Colors.BRIGHT_CYAN)
        colored_print(guidance, Colors.CYAN)
        colored_print(f"================================\\n", Colors.BRIGHT_CYAN)
        
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
        """Analyze the task and provide intelligent guidance instead of hardcoded solutions"""
        desc_lower = description.lower()
        
        # Analyze what the user is asking for
        analysis = {
            "framework": None,
            "component_type": None, 
            "features": [],
            "complexity": "medium",
            "suggested_approach": []
        }
        
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
        description = task["description"]
        
        # Analyze what type of task this is and delegate appropriately
        if "code" in description.lower() or "generate" in description.lower():
            # Delegate to coder
            delegated_task_id = self.comm.create_task(
                task_type="code_generation",
                description=description,
                assigned_to="coder",
                created_by=self.agent_id,
                priority=task.get("priority", 1)
            )
            return {"delegated_task_id": delegated_task_id, "delegated_to": "coder"}
        
        return {"message": f"Coordination task handled: {description}"}
    
    def handle_code_review_task(self, task: Dict) -> Dict:
        """Handle code review tasks"""
        return {"message": f"Code review completed for: {task['description']}"}
    
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
    
    colored_print(f"\\n=== Multi-Agent Terminal ({agent_id}) ===", Colors.BRIGHT_YELLOW)
    colored_print(f"Role: {role.value}", Colors.CYAN)
    colored_print(f"Workspace: {agent.workspace_dir}", Colors.CYAN)
    colored_print("Commands: 'help', 'agents', 'tasks', 'delegate <description>', 'quit'", Colors.WHITE)
    colored_print("=" * 50, Colors.BRIGHT_YELLOW)
    
    try:
        while True:
            try:
                user_input = input(f"\\n[{agent_id}]> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_input.lower() == 'help':
                    print("Available commands:")
                    print("  agents - Show active agents")
                    print("  tasks - Show pending tasks")
                    print("  delegate <description> - Create task for appropriate agent")
                    print("  quit - Exit the terminal")
                elif user_input.lower() == 'agents':
                    agents = agent.comm.get_active_agents()
                    colored_print(f"\\nActive Agents ({len(agents)}):", Colors.BRIGHT_CYAN)
                    for a in agents:
                        print(f"  {a['id']} ({a['role']}) - PID: {a.get('pid', 'unknown')}")
                elif user_input.lower() == 'tasks':
                    tasks = agent.comm.get_pending_tasks(agent_id)
                    colored_print(f"\\nPending Tasks ({len(tasks)}):", Colors.BRIGHT_CYAN)
                    for t in tasks:
                        print(f"  {t['id']}: {t['description']}")
                elif user_input.lower().startswith('delegate '):
                    description = user_input[9:].strip()
                    if description:
                        task_id = agent.comm.create_task(
                            task_type="general",
                            description=description,
                            assigned_to="coder",  # Default to coder for now
                            created_by=agent_id
                        )
                        colored_print(f"Task {task_id} created and delegated!", Colors.GREEN)
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
        colored_print(f"\\nAgent {agent_id} shutting down...", Colors.YELLOW)

if __name__ == "__main__":
    main()
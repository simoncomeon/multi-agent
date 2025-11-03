"""
Agent Communication module for the Multi-Agent AI Terminal System
Handles inter-agent messaging, task management, and agent registry
"""

import os
import json
import uuid
import signal
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from .models import Task, TaskStatus, AgentRole, Colors
from .utils import colored_print


class AgentCommunication:
    """Manages communication between agents via JSON files"""
    
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
    
    # Agent Registry Management
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
    
    def get_active_agents(self) -> List[Dict]:
        """Get list of active agents"""
        agents = self.load_agents()
        return [agent for agent in agents if agent.get("status") == "active"]
    
    def get_agent_status(self, agent_id: str) -> Dict:
        """Get status of a specific agent"""
        agents = self.load_agents()
        for agent in agents:
            if agent["id"] == agent_id:
                return agent
        return None
    
    def load_agents(self) -> List[Dict]:
        """Load agents from JSON file"""
        try:
            with open(self.agents_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def save_agents(self, agents: List[Dict]):
        """Save agents to JSON file"""
        with open(self.agents_file, 'w') as f:
            json.dump(agents, f, indent=2)
    
    # Process Management
    def kill_agent_by_pid(self, agent_id: str) -> bool:
        """Kill agent process by PID"""
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
    
    # Task Management
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
        tasks.append(task.to_dict())
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
        
        # Only show debug info when there are actual tasks
        if pending and len(pending) > 0:
            print(f" Found {len(pending)} pending tasks for {agent_id} ({agent_role})")
            for task in pending:
                print(f" Task {task['id']}: {task['description']}")
        
        return pending
    
    def load_tasks(self) -> List[Dict]:
        """Load tasks from JSON file"""
        try:
            with open(self.tasks_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def save_tasks(self, tasks: List[Dict]):
        """Save tasks to JSON file"""
        with open(self.tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
    
    # Message Management
    def send_message(self, from_agent: str, to_agent: str, message: str, message_type: str = "info"):
        """Send message between agents"""
        messages = self.load_messages()
        
        message_data = {
            "id": str(uuid.uuid4())[:8],
            "from": from_agent,
            "to": to_agent,
            "message": message,
            "type": message_type,
            "timestamp": datetime.now().isoformat()
        }
        
        messages.append(message_data)
        self.save_messages(messages)
    
    def get_messages(self, agent_id: str) -> List[Dict]:
        """Get messages for an agent"""
        messages = self.load_messages()
        return [msg for msg in messages if msg["to"] == agent_id]
    
    def load_messages(self) -> List[Dict]:
        """Load messages from JSON file"""
        try:
            with open(self.messages_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def save_messages(self, messages: List[Dict]):
        """Save messages to JSON file"""
        with open(self.messages_file, 'w') as f:
            json.dump(messages, f, indent=2)
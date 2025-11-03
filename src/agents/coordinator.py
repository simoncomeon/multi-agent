"""
Coordinator Agent - Handles task delegation and agent coordination
"""

from datetime import datetime
from typing import Dict, List

from ..core.models import Colors
from ..core.utils import colored_print


class CoordinatorAgent:
    """Specialized agent for coordinating tasks and delegating to other agents"""
    
    def __init__(self, terminal_instance, comm_instance):
        self.terminal = terminal_instance
        self.comm = comm_instance
        self.agent_id = "coordinator"
    
    def handle_coordination_task(self, task: Dict) -> Dict:
        """Handle coordination tasks - delegate to other agents"""
        description = task["description"].lower()
        
        colored_print(f"COORDINATOR: Analyzing task for delegation", Colors.BRIGHT_CYAN)
        colored_print(f"   Task: {task['description']}", Colors.CYAN)
        
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
            colored_print(f"   DELEGATED: Task {delegated_task_id} -> file_manager", Colors.GREEN)
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
            colored_print(f"   DELEGATED: Task {delegated_task_id} -> git_manager", Colors.GREEN)
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
            colored_print(f"   DELEGATED: Task {delegated_task_id} -> coder", Colors.GREEN)
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
            colored_print(f"   DELEGATED: Task {delegated_task_id} -> code_reviewer", Colors.GREEN)
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
            colored_print(f"   DELEGATED: Task {delegated_task_id} -> tester", Colors.GREEN)
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
            colored_print(f"   DELEGATED: Task {delegated_task_id} -> researcher", Colors.GREEN)
            return {"delegated_task_id": delegated_task_id, "delegated_to": "researcher"}
        
        elif any(keyword in description for keyword in ["fix", "rewrite", "refactor", "improve"]):
            # Code rewriting -> code_rewriter
            delegated_task_id = self.comm.create_task(
                task_type="code_rewrite",
                description=task["description"],
                assigned_to="code_rewriter",
                created_by=self.agent_id,
                priority=task.get("priority", 1)
            )
            colored_print(f"   DELEGATED: Task {delegated_task_id} -> code_rewriter", Colors.GREEN)
            return {"delegated_task_id": delegated_task_id, "delegated_to": "code_rewriter"}
        
        else:
            # Default to coder for general tasks
            delegated_task_id = self.comm.create_task(
                task_type="general",
                description=task["description"],
                assigned_to="coder",
                created_by=self.agent_id,
                priority=task.get("priority", 1)
            )
            colored_print(f"   DELEGATED: Task {delegated_task_id} -> coder (default)", Colors.YELLOW)
            return {"delegated_task_id": delegated_task_id, "delegated_to": "coder"}
    
    def analyze_task_complexity(self, description: str) -> Dict:
        """Analyze task complexity and suggest agent assignment"""
        
        desc_lower = description.lower()
        complexity_score = 0
        required_agents = []
        
        # Calculate complexity based on keywords
        if any(keyword in desc_lower for keyword in ["create", "build", "develop", "implement"]):
            complexity_score += 3
            
        if any(keyword in desc_lower for keyword in ["integrate", "connect", "api", "database"]):
            complexity_score += 2
            
        if any(keyword in desc_lower for keyword in ["test", "deploy", "production"]):
            complexity_score += 2
        
        # Determine required agents
        if "file" in desc_lower or "directory" in desc_lower:
            required_agents.append("file_manager")
            
        if "code" in desc_lower or "implement" in desc_lower:
            required_agents.append("coder")
            
        if "review" in desc_lower or "quality" in desc_lower:
            required_agents.append("code_reviewer")
            
        if "git" in desc_lower or "commit" in desc_lower:
            required_agents.append("git_manager")
            
        if "test" in desc_lower:
            required_agents.append("tester")
            
        if "research" in desc_lower or "find" in desc_lower:
            required_agents.append("researcher")
        
        # Determine complexity level
        if complexity_score >= 6:
            complexity_level = "high"
        elif complexity_score >= 3:
            complexity_level = "medium"
        else:
            complexity_level = "low"
        
        return {
            "complexity_score": complexity_score,
            "complexity_level": complexity_level,
            "required_agents": required_agents,
            "estimated_agents": len(required_agents),
            "parallel_execution": len(required_agents) > 1
        }
    
    def create_workflow_plan(self, task: Dict) -> Dict:
        """Create a detailed workflow plan for complex tasks"""
        
        complexity_analysis = self.analyze_task_complexity(task["description"])
        
        if complexity_analysis["complexity_level"] == "high":
            # Create multi-step workflow
            return self.create_multi_step_workflow(task, complexity_analysis)
        else:
            # Simple single-agent delegation
            return self.handle_coordination_task(task)
    
    def create_multi_step_workflow(self, task: Dict, complexity_analysis: Dict) -> Dict:
        """Create multi-step workflow for complex tasks"""
        
        workflow_steps = []
        required_agents = complexity_analysis["required_agents"]
        
        colored_print(f"COORDINATOR: Creating multi-step workflow", Colors.BRIGHT_YELLOW)
        colored_print(f"   Complexity: {complexity_analysis['complexity_level']}", Colors.YELLOW)
        colored_print(f"   Required agents: {', '.join(required_agents)}", Colors.YELLOW)
        
        # Step 1: Planning and analysis
        if "researcher" in required_agents:
            step1_id = self.comm.create_task(
                task_type="research",
                description=f"Research requirements for: {task['description']}",
                assigned_to="researcher",
                created_by=self.agent_id,
                priority=1
            )
            workflow_steps.append({
                "step": 1,
                "task_id": step1_id,
                "agent": "researcher",
                "description": "Research and analysis phase"
            })
        
        # Step 2: File structure setup
        if "file_manager" in required_agents:
            step2_id = self.comm.create_task(
                task_type="file_management",
                description=f"Set up file structure for: {task['description']}",
                assigned_to="file_manager",
                created_by=self.agent_id,
                priority=2
            )
            workflow_steps.append({
                "step": 2,
                "task_id": step2_id,
                "agent": "file_manager",
                "description": "File structure setup phase"
            })
        
        # Step 3: Implementation
        if "coder" in required_agents:
            step3_id = self.comm.create_task(
                task_type="code_generation",
                description=f"Implement: {task['description']}",
                assigned_to="coder",
                created_by=self.agent_id,
                priority=3
            )
            workflow_steps.append({
                "step": 3,
                "task_id": step3_id,
                "agent": "coder",
                "description": "Implementation phase"
            })
        
        # Step 4: Review and testing
        if "code_reviewer" in required_agents:
            step4_id = self.comm.create_task(
                task_type="code_review",
                description=f"Review implementation of: {task['description']}",
                assigned_to="code_reviewer",
                created_by=self.agent_id,
                priority=4
            )
            workflow_steps.append({
                "step": 4,
                "task_id": step4_id,
                "agent": "code_reviewer",
                "description": "Review and quality assurance phase"
            })
        
        # Step 5: Git management
        if "git_manager" in required_agents:
            step5_id = self.comm.create_task(
                task_type="git_management",
                description=f"Version control for: {task['description']}",
                assigned_to="git_manager",
                created_by=self.agent_id,
                priority=5
            )
            workflow_steps.append({
                "step": 5,
                "task_id": step5_id,
                "agent": "git_manager",
                "description": "Version control phase"
            })
        
        colored_print(f"   WORKFLOW: Created {len(workflow_steps)} steps", Colors.GREEN)
        
        return {
            "type": "multi_step_workflow",
            "workflow_steps": workflow_steps,
            "complexity_analysis": complexity_analysis,
            "total_steps": len(workflow_steps),
            "message": f"Multi-step workflow created with {len(workflow_steps)} phases"
        }
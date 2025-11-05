"""
Integration Example: Using Enhanced Agents in Existing Multi-Agent System

This module shows how to integrate the new enhanced agents with the existing
multi-agent terminal system while maintaining backwards compatibility.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path for imports
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

from core.base_agent import BaseAgent, TaskInput, TaskResult
from agents.code_generator import EnhancedCodeGeneratorAgent
from agents.file_manager import EnhancedFileManagerAgent
from core.communication import AgentCommunication
from core.models import Colors, AgentRole
from core.utils import colored_print


class EnhancedAgentBridge:
 """
 Bridge class to integrate enhanced agents with existing multi-agent system.
 Provides backwards compatibility while enabling new functionality.
 """
 
 def __init__(self, workspace_dir: str):
 self.workspace_dir = workspace_dir
 self.comm = AgentCommunication(workspace_dir)
 
 # Initialize enhanced agents
 self.code_agent = EnhancedCodeGeneratorAgent("enhanced_coder", workspace_dir)
 self.file_agent = EnhancedFileManagerAgent("enhanced_file_manager", workspace_dir)
 
 # Map old agent roles to new agents
 self.agent_mapping = {
 'coder': self.code_agent,
 'code_generator': self.code_agent,
 'file_manager': self.file_agent
 }
 
 colored_print(" Enhanced Agent Bridge initialized", Colors.BRIGHT_GREEN)
 
 def handle_legacy_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
 """
 Handle tasks in the legacy format and convert them to enhanced format.
 Maintains backwards compatibility with existing task structure.
 """
 
 task_type = task.get("type", "general")
 description = task.get("description", "")
 assigned_to = task.get("assigned_to", "")
 
 colored_print(f"Converting legacy task: {task_type}", Colors.CYAN)
 
 # Map legacy task to appropriate enhanced agent
 agent = self._get_agent_for_legacy_task(assigned_to, task_type)
 
 if not agent:
 return {
 "success": False,
 "error": f"No enhanced agent available for task type: {task_type}",
 "agent": assigned_to
 }
 
 # Convert legacy task to TaskInput
 task_input = self._convert_legacy_to_task_input(task)
 
 # Execute with enhanced agent
 result = agent.execute_task(task_input)
 
 # Convert result back to legacy format
 return self._convert_result_to_legacy(result, task)
 
 def execute_enhanced_task(self, task_description: str, agent_role: str = "auto", **kwargs) -> TaskResult:
 """
 Execute task using enhanced agents with new interface.
 Provides access to full enhanced functionality.
 """
 
 # Auto-select agent based on task if not specified
 if agent_role == "auto":
 agent_role = self._auto_select_agent(task_description, kwargs)
 
 agent = self.agent_mapping.get(agent_role)
 if not agent:
 return TaskResult(
 success=False,
 message=f"Agent '{agent_role}' not found"
 )
 
 # Create TaskInput from parameters
 task_input = TaskInput(
 task_description=task_description,
 **kwargs
 )
 
 return agent.execute_task(task_input)
 
 def create_file_with_content(self, file_path: str, description: str, **kwargs) -> TaskResult:
 """
 Convenience method: Create file with AI-generated content.
 Example of new capabilities not available in legacy system.
 """
 
 return self.execute_enhanced_task(
 task_description=description,
 agent_role="code_generator",
 target_file=file_path,
 task_type="code_generation",
 **kwargs
 )
 
 def scaffold_project(self, project_name: str, framework: str, **kwargs) -> TaskResult:
 """
 Convenience method: Create complete project structure.
 Example of new capabilities not available in legacy system.
 """
 
 description = f"Create {framework} project named '{project_name}'"
 
 return self.execute_enhanced_task(
 task_description=description,
 agent_role="file_manager",
 task_type="project_creation",
 **kwargs
 )
 
 def enhance_existing_files(self, files: list, enhancement_description: str, **kwargs) -> TaskResult:
 """
 Convenience method: Enhance multiple existing files.
 Example of new capabilities with context awareness.
 """
 
 return self.execute_enhanced_task(
 task_description=enhancement_description,
 agent_role="code_generator",
 files=files,
 task_type="file_enhancement",
 **kwargs
 )
 
 def _get_agent_for_legacy_task(self, assigned_to: str, task_type: str) -> Optional[BaseAgent]:
 """Get appropriate enhanced agent for legacy task"""
 
 # Direct mapping
 if assigned_to in self.agent_mapping:
 return self.agent_mapping[assigned_to]
 
 # Task type based mapping
 if task_type in ['code_generation', 'implementation', 'coding']:
 return self.code_agent
 elif task_type in ['file_management', 'project_creation', 'structure']:
 return self.file_agent
 
 # Default to code agent for unknown tasks
 return self.code_agent
 
 def _convert_legacy_to_task_input(self, task: Dict[str, Any]) -> TaskInput:
 """Convert legacy task format to TaskInput"""
 
 task_data = task.get("data", {})
 
 # Extract parameters from legacy format
 kwargs = {
 'task_type': task.get("type", "general"),
 'priority': task.get("priority", 1)
 }
 
 # Extract file parameters
 if 'file_path' in task_data:
 kwargs['target_file'] = task_data['file_path']
 
 if 'files' in task_data:
 kwargs['files'] = task_data['files']
 
 if 'directory' in task_data:
 kwargs['target_directory'] = task_data['directory']
 
 # Extract requirements and constraints
 if 'requirements' in task_data:
 kwargs['requirements'] = task_data['requirements']
 
 if 'constraints' in task_data:
 kwargs['constraints'] = task_data['constraints']
 
 # Extract project information
 if 'project_name' in task_data:
 kwargs['metadata'] = {'project_name': task_data['project_name']}
 
 return TaskInput(
 task_description=task.get("description", ""),
 **kwargs
 )
 
 def _convert_result_to_legacy(self, result: TaskResult, original_task: Dict) -> Dict[str, Any]:
 """Convert TaskResult back to legacy format"""
 
 legacy_result = {
 "success": result.success,
 "message": result.message,
 "task_id": original_task.get("id"),
 "type": "enhanced_result"
 }
 
 # Add file information
 if result.files_created:
 legacy_result["files_created"] = result.files_created
 
 if result.files_modified:
 legacy_result["files_modified"] = result.files_modified
 
 # Add output content if available
 if result.output_content:
 legacy_result["output"] = result.output_content
 
 # Add metadata
 if result.metadata:
 legacy_result["metadata"] = result.metadata
 
 return legacy_result
 
 def _auto_select_agent(self, description: str, kwargs: Dict) -> str:
 """Auto-select appropriate agent based on task description and parameters"""
 
 desc_lower = description.lower()
 
 # File management indicators
 if any(keyword in desc_lower for keyword in ['create project', 'scaffold', 'organize files', 'directory']):
 return 'file_manager'
 
 # Code generation indicators
 if any(keyword in desc_lower for keyword in ['generate code', 'create component', 'implement', 'write code']):
 return 'code_generator'
 
 # Parameter based selection
 if kwargs.get('target_file') or kwargs.get('files'):
 return 'code_generator'
 
 if kwargs.get('target_directory') or 'project' in desc_lower:
 return 'file_manager'
 
 # Default to code generator
 return 'code_generator'
 
 def get_agent_status(self) -> Dict[str, Any]:
 """Get status of all enhanced agents"""
 
 return {
 "enhanced_agents": {
 "code_generator": {
 "id": self.code_agent.agent_id,
 "capabilities": list(self.code_agent.capabilities.keys()),
 "supported_file_types": self.code_agent.supported_file_types[:10], # First 10
 "ai_available": self.code_agent.ai_client.is_available()
 },
 "file_manager": {
 "id": self.file_agent.agent_id,
 "capabilities": list(self.file_agent.capabilities.keys()),
 "backup_enabled": self.file_agent.backup_enabled,
 "ai_available": self.file_agent.ai_client.is_available()
 }
 },
 "integration_ready": True
 }
 
 def shutdown(self):
 """Shutdown all enhanced agents"""
 
 colored_print(" Shutting down enhanced agents...", Colors.YELLOW)
 self.code_agent.shutdown()
 self.file_agent.shutdown()
 colored_print("Enhanced agents shutdown complete", Colors.GREEN)


def integration_example():
 """
 Example showing how to use the enhanced agents in existing workflows
 """
 
 workspace_dir = str(Path(__file__).parent / "integration_workspace")
 Path(workspace_dir).mkdir(exist_ok=True)
 
 # Initialize the bridge
 bridge = EnhancedAgentBridge(workspace_dir)
 
 colored_print("Enhanced Agent Integration Example", Colors.BRIGHT_GREEN)
 
 # Example 1: Legacy task compatibility
 print("\n1. Legacy Task Compatibility:")
 legacy_task = {
 "id": "task_001",
 "type": "code_generation",
 "description": "Create a simple calculator class",
 "assigned_to": "coder",
 "data": {
 "file_path": f"{workspace_dir}/calculator.py",
 "requirements": ["Add basic arithmetic operations", "Include error handling"]
 }
 }
 
 result1 = bridge.handle_legacy_task(legacy_task)
 print(f" Result: {result1['success']} - {result1['message']}")
 
 # Example 2: Enhanced functionality
 print("\n2. Enhanced File Creation:")
 result2 = bridge.create_file_with_content(
 file_path=f"{workspace_dir}/components/Button.jsx",
 description="Create a reusable React button component with hover effects",
 requirements=["Use styled-components", "Include accessibility features"],
 constraints=["TypeScript compatible", "Mobile responsive"]
 )
 
 print(f" Result: {result2.success} - {result2.message}")
 if result2.files_created:
 print(f" Created: {[Path(f).name for f in result2.files_created]}")
 
 # Example 3: Project scaffolding
 print("\n3. Project Scaffolding:")
 result3 = bridge.scaffold_project(
 project_name="todo-app",
 framework="react",
 requirements=["Include routing", "Add state management", "Include tests"]
 )
 
 print(f" Result: {result3.success} - {result3.message}")
 if result3.files_created:
 print(f" Created {len(result3.files_created)} files")
 
 # Example 4: File enhancement
 print("\n4. File Enhancement:")
 if result1.get("files_created"):
 result4 = bridge.enhance_existing_files(
 files=result1["files_created"],
 enhancement_description="Add unit tests and improve documentation",
 requirements=["Use pytest framework", "Include type hints", "Add docstrings"]
 )
 
 print(f" Result: {result4.success} - {result4.message}")
 
 # Show agent status
 print("\n5. Agent Status:")
 status = bridge.get_agent_status()
 for agent_name, agent_info in status["enhanced_agents"].items():
 print(f" {agent_name}: {len(agent_info['capabilities'])} capabilities, AI: {agent_info['ai_available']}")
 
 # Cleanup
 bridge.shutdown()
 colored_print("\nIntegration example completed!", Colors.BRIGHT_GREEN)


if __name__ == "__main__":
 try:
 integration_example()
 except KeyboardInterrupt:
 colored_print("\n Example interrupted by user", Colors.YELLOW)
 except Exception as e:
 colored_print(f"\n Example failed: {e}", Colors.RED)
 import traceback
 traceback.print_exc()
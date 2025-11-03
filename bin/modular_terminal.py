"""
Modular Multi-Agent Terminal - Main Entry Point

This is the new modular version that uses the extracted components.
The original multi_agent_terminal.py is preserved for backward compatibility.
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Dict

# Add the project root to Python path to find src directory
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from src.core import AgentRole, AgentCommunication, colored_print, Colors
from src.agents import CodeReviewerAgent, FileManagerAgent
from src.lifecycle import AgentLifecycleManager
from src.project import ProjectManager


class ModularMultiAgentTerminal:
    """
    Modular version of the Multi-Agent Terminal System
    Uses extracted components for better maintainability
    """
    
    def __init__(self, workspace_dir: str = None, agent_id: str = None, role: str = None):
        self.workspace_dir = workspace_dir or os.getcwd()
        self.agent_id = agent_id or "terminal_main"
        self.role = role or "coordinator"
        
        # Initialize core communication
        self.comm = AgentCommunication(self.workspace_dir)
        
        # Initialize specialized agents
        self.code_reviewer = CodeReviewerAgent(self, self.comm)
        self.file_manager = FileManagerAgent(self, self.comm)
        
        # Initialize management systems
        self.lifecycle_manager = AgentLifecycleManager(self, self.comm)
        self.project_manager = ProjectManager(self, self.comm)
        
        # Register this terminal instance
        try:
            agent_role = AgentRole(self.role)
        except ValueError:
            agent_role = AgentRole.COORDINATOR
            
        self.comm.register_agent(self.agent_id, agent_role)
        
        colored_print(f"Modular Multi-Agent Terminal initialized", Colors.BRIGHT_GREEN)
        colored_print(f"  Workspace: {self.workspace_dir}", Colors.GREEN)
        colored_print(f"  Agent ID: {self.agent_id}", Colors.GREEN)
        colored_print(f"  Role: {self.role}", Colors.GREEN)
    
    def run_interactive_mode(self):
        """Run the terminal in interactive mode"""
        
        colored_print("\\n=== MODULAR MULTI-AGENT TERMINAL ===", Colors.BRIGHT_CYAN)
        colored_print("Enhanced modular architecture for better maintainability", Colors.CYAN)
        colored_print("Type 'help' for available commands or 'exit' to quit\\n", Colors.WHITE)
        
        while True:
            try:
                user_input = input(f"{Colors.BRIGHT_YELLOW}multi-agent> {Colors.RESET}").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    self.shutdown()
                    break
                
                elif user_input.lower() in ['help', 'h']:
                    self.show_help()
                
                elif user_input.startswith('agent '):
                    self.handle_agent_command(user_input)
                
                elif user_input.startswith('project '):
                    self.handle_project_command(user_input)
                
                elif user_input.startswith('delegate '):
                    self.handle_delegation_command(user_input)
                
                else:
                    colored_print(f"Unknown command: {user_input}. Type 'help' for available commands.", Colors.RED)
                    
            except KeyboardInterrupt:
                colored_print("\\n\\nShutting down...", Colors.YELLOW)
                self.shutdown()
                break
            except EOFError:
                self.shutdown()
                break
            except Exception as e:
                colored_print(f"Error: {str(e)}", Colors.RED)
    
    def show_help(self):
        """Show available commands"""
        
        colored_print("\\n=== MODULAR MULTI-AGENT TERMINAL COMMANDS ===", Colors.BRIGHT_WHITE)
        colored_print("\\nAgent Management:", Colors.BRIGHT_CYAN)
        colored_print("  agent status              - Show all agent status", Colors.WHITE)
        colored_print("  agent kill <agent_id>     - Kill specific agent", Colors.WHITE)
        colored_print("  agent restart <agent_id>  - Restart specific agent", Colors.WHITE)
        colored_print("  agent spawn <role>        - Spawn new agent with role", Colors.WHITE)
        colored_print("  agent cleanup             - Remove inactive agents", Colors.WHITE)
        colored_print("  agent health              - Perform health check", Colors.WHITE)
        
        colored_print("\\nProject Management:", Colors.BRIGHT_CYAN)
        colored_print("  project create <name>     - Create new project", Colors.WHITE)
        colored_print("  project list              - List existing projects", Colors.WHITE)
        colored_print("  project analyze <path>    - Analyze project structure", Colors.WHITE)
        
        colored_print("\\nTask Delegation:", Colors.BRIGHT_CYAN)
        colored_print("  delegate to <agent> <task> - Delegate task to specific agent", Colors.WHITE)
        colored_print("  delegate review <project>  - Request code review", Colors.WHITE)
        colored_print("  delegate file <operation>  - Request file operation", Colors.WHITE)
        
        colored_print("\\nSystem:", Colors.BRIGHT_CYAN)
        colored_print("  help, h                   - Show this help", Colors.WHITE)
        colored_print("  exit, quit, q             - Exit terminal", Colors.WHITE)
        colored_print("")
    
    def handle_agent_command(self, command: str):
        """Handle agent management commands"""
        
        parts = command.split()
        if len(parts) < 2:
            colored_print("Invalid agent command. Use: agent <action> [args]", Colors.RED)
            return
        
        action = parts[1]
        
        if action == "status":
            self.lifecycle_manager.show_agent_status()
            
        elif action == "kill" and len(parts) >= 3:
            agent_id = parts[2]
            result = self.lifecycle_manager.kill_agent(agent_id)
            colored_print(f"Result: {result.get('message', 'Command completed')}", Colors.CYAN)
            
        elif action == "restart" and len(parts) >= 3:
            agent_id = parts[2]
            result = self.lifecycle_manager.restart_agent(agent_id)
            colored_print(f"Result: {result.get('message', 'Command completed')}", Colors.CYAN)
            
        elif action == "spawn" and len(parts) >= 3:
            role = parts[2]
            result = self.lifecycle_manager.spawn_new_agent(role)
            colored_print(f"Result: {result.get('message', 'Command completed')}", Colors.CYAN)
            
        elif action == "cleanup":
            result = self.lifecycle_manager.cleanup_inactive_agents()
            colored_print(f"Result: {result.get('message', 'Command completed')}", Colors.CYAN)
            
        elif action == "health":
            result = self.lifecycle_manager.health_check_agents()
            colored_print(f"Result: {result.get('message', 'Command completed')}", Colors.CYAN)
            
        else:
            colored_print(f"Unknown agent action: {action}", Colors.RED)
    
    def handle_project_command(self, command: str):
        """Handle project management commands"""
        
        parts = command.split()
        if len(parts) < 2:
            colored_print("Invalid project command. Use: project <action> [args]", Colors.RED)
            return
        
        action = parts[1]
        
        if action == "create" and len(parts) >= 3:
            project_name = parts[2]
            project_info = {"name": project_name, "framework": "react"}
            project_path = self.project_manager.create_project_structure(project_info)
            colored_print(f"Created project at: {project_path}", Colors.GREEN)
            
        elif action == "list":
            self.list_projects()
            
        elif action == "analyze" and len(parts) >= 3:
            project_path = parts[2]
            self.analyze_project(project_path)
            
        else:
            colored_print(f"Unknown project action: {action}", Colors.RED)
    
    def handle_delegation_command(self, command: str):
        """Handle task delegation commands"""
        
        parts = command.split(' ', 3)  # Split into max 4 parts
        if len(parts) < 3:
            colored_print("Invalid delegation command. Use: delegate <to/review/file> <target> <task>", Colors.RED)
            return
        
        delegation_type = parts[1]
        
        if delegation_type == "to" and len(parts) >= 4:
            agent_id = parts[2]
            task_description = parts[3]
            
            task_id = self.comm.create_task(
                task_type="delegated_task",
                description=task_description,
                assigned_to=agent_id,
                created_by=self.agent_id,
                priority=1
            )
            
            colored_print(f"Task {task_id} delegated to {agent_id}", Colors.GREEN)
            
        elif delegation_type == "review":
            task_description = " ".join(parts[2:])
            
            # Create code review task
            review_task = {
                "description": task_description,
                "type": "code_review"
            }
            
            result = self.code_reviewer.handle_code_review_task(review_task)
            colored_print(f"Code review result: {result.get('message', 'Review completed')}", Colors.CYAN)
            
        elif delegation_type == "file":
            task_description = " ".join(parts[2:])
            
            # Create file management task
            file_task = {
                "description": task_description,
                "type": "file_management"
            }
            
            result = self.file_manager.handle_file_management_task(file_task)
            colored_print(f"File operation result: {result.get('message', 'Operation completed')}", Colors.CYAN)
            
        else:
            colored_print(f"Unknown delegation type: {delegation_type}", Colors.RED)
    
    def list_projects(self):
        """List existing projects in workspace"""
        
        colored_print("\\n=== EXISTING PROJECTS ===", Colors.BRIGHT_WHITE)
        
        project_count = 0
        for item in os.listdir(self.workspace_dir):
            item_path = os.path.join(self.workspace_dir, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                # Check if it's a valid project
                if self.is_project_directory(item_path):
                    project_info = self.analyze_project_type(item_path)
                    colored_print(f"  📁 {item} ({project_info.get('type', 'unknown')})", Colors.CYAN)
                    project_count += 1
        
        if project_count == 0:
            colored_print("  No projects found in workspace", Colors.YELLOW)
        else:
            colored_print(f"\\nTotal: {project_count} projects", Colors.WHITE)
    
    def is_project_directory(self, path: str) -> bool:
        """Check if directory appears to be a project"""
        
        try:
            files = os.listdir(path)
            project_indicators = [
                'package.json', 'requirements.txt', 'setup.py', 
                'pom.xml', 'Cargo.toml', 'README.md'
            ]
            return any(indicator in files for indicator in project_indicators)
        except:
            return False
    
    def analyze_project_type(self, path: str) -> Dict:
        """Analyze project type from directory contents"""
        
        try:
            files = os.listdir(path)
            
            if 'package.json' in files:
                return {"type": "JavaScript/Node.js"}
            elif 'requirements.txt' in files or 'setup.py' in files:
                return {"type": "Python"}
            elif 'pom.xml' in files:
                return {"type": "Java/Maven"}
            elif 'Cargo.toml' in files:
                return {"type": "Rust"}
            elif any(f.endswith('.js') or f.endswith('.jsx') for f in files):
                return {"type": "JavaScript"}
            elif any(f.endswith('.py') for f in files):
                return {"type": "Python"}
            else:
                return {"type": "Generic"}
        except:
            return {"type": "Unknown"}
    
    def analyze_project(self, project_path: str):
        """Analyze a specific project"""
        
        if not os.path.exists(project_path):
            colored_print(f"Project path does not exist: {project_path}", Colors.RED)
            return
        
        colored_print(f"\\n=== PROJECT ANALYSIS: {os.path.basename(project_path)} ===", Colors.BRIGHT_WHITE)
        
        # Basic info
        project_type = self.analyze_project_type(project_path)
        colored_print(f"Type: {project_type.get('type', 'Unknown')}", Colors.CYAN)
        colored_print(f"Path: {project_path}", Colors.WHITE)
        
        # Structure analysis
        try:
            file_count = sum(len(files) for _, _, files in os.walk(project_path))
            dir_count = sum(len(dirs) for _, dirs, _ in os.walk(project_path))
            colored_print(f"Files: {file_count}, Directories: {dir_count}", Colors.WHITE)
        except:
            colored_print("Could not analyze project structure", Colors.YELLOW)
    
    def shutdown(self):
        """Clean shutdown of the terminal"""
        
        colored_print("\\nShutting down Modular Multi-Agent Terminal...", Colors.YELLOW)
        
        # Unregister this terminal
        self.comm.unregister_agent(self.agent_id)
        
        colored_print("Goodbye!", Colors.GREEN)


def main():
    """Main entry point for the modular multi-agent terminal"""
    
    parser = argparse.ArgumentParser(description="Modular Multi-Agent AI Terminal System")
    parser.add_argument("--workspace", "-w", default=None, help="Workspace directory")
    parser.add_argument("--agent-id", default=None, help="Agent ID for this instance")
    parser.add_argument("--role", default="coordinator", help="Agent role")
    parser.add_argument("--version", action="version", version="Multi-Agent Terminal v3.0.0 (Modular)")
    
    args = parser.parse_args()
    
    # Initialize terminal
    terminal = ModularMultiAgentTerminal(
        workspace_dir=args.workspace,
        agent_id=args.agent_id,
        role=args.role
    )
    
    # Run interactive mode
    terminal.run_interactive_mode()


if __name__ == "__main__":
    main()
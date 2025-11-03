"""
Git Manager Agent - Handles version control operations
"""

import subprocess
import os
from datetime import datetime
from typing import Dict, List

from ..core.models import Colors
from ..core.utils import colored_print


class GitManagerAgent:
    """Specialized agent for Git version control operations"""
    
    def __init__(self, terminal_instance, comm_instance):
        self.terminal = terminal_instance
        self.comm = comm_instance
        self.agent_id = "git_manager"
        self.workspace_dir = terminal_instance.workspace_dir
    
    def handle_git_management_task(self, task: Dict) -> Dict:
        """Handle git management tasks"""
        
        description = task["description"]
        colored_print(f"GIT MANAGER: Processing version control task", Colors.BRIGHT_CYAN)
        colored_print(f"   Task: {description}", Colors.CYAN)
        
        desc_lower = description.lower()
        
        try:
            if "init" in desc_lower:
                return self.initialize_repository()
            elif "commit" in desc_lower:
                return self.commit_changes(description)
            elif "push" in desc_lower:
                return self.push_changes()
            elif "pull" in desc_lower:
                return self.pull_changes()
            elif "branch" in desc_lower:
                return self.manage_branches(description)
            elif "status" in desc_lower:
                return self.get_git_status()
            elif "add" in desc_lower:
                return self.add_files(description)
            else:
                return self.general_git_operation(description)
                
        except Exception as e:
            colored_print(f"   ERROR: Git operation failed: {str(e)}", Colors.RED)
            return {
                "status": "failed",
                "message": f"Git operation failed: {str(e)}",
                "error": str(e)
            }
    
    def initialize_repository(self) -> Dict:
        """Initialize a new Git repository"""
        
        try:
            # Check if already a git repository
            if os.path.exists(os.path.join(self.workspace_dir, ".git")):
                colored_print(f"   INFO: Repository already initialized", Colors.YELLOW)
                return {
                    "status": "success",
                    "message": "Repository already initialized",
                    "action": "git_init_existing"
                }
            
            # Initialize repository
            result = subprocess.run(
                ["git", "init"],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            colored_print(f"   SUCCESS: Git repository initialized", Colors.GREEN)
            
            return {
                "status": "success", 
                "message": "Git repository initialized successfully",
                "action": "git_init",
                "output": result.stdout
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "status": "failed",
                "message": f"Failed to initialize repository: {e.stderr}",
                "error": e.stderr
            }
    
    def commit_changes(self, description: str) -> Dict:
        """Commit changes with appropriate message"""
        
        try:
            # Get git status first
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            if not status_result.stdout.strip():
                colored_print(f"   INFO: No changes to commit", Colors.YELLOW)
                return {
                    "status": "success",
                    "message": "No changes to commit",
                    "action": "git_commit_empty"
                }
            
            # Add all changes
            subprocess.run(
                ["git", "add", "."],
                cwd=self.workspace_dir,
                check=True
            )
            
            # Extract or generate commit message
            commit_message = self.extract_commit_message(description)
            
            # Commit changes
            commit_result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            colored_print(f"   SUCCESS: Changes committed: {commit_message}", Colors.GREEN)
            
            return {
                "status": "success",
                "message": f"Changes committed successfully",
                "action": "git_commit",
                "commit_message": commit_message,
                "output": commit_result.stdout
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "status": "failed",
                "message": f"Failed to commit changes: {e.stderr}",
                "error": e.stderr
            }
    
    def extract_commit_message(self, description: str) -> str:
        """Extract or generate appropriate commit message"""
        
        # Look for explicit commit message patterns
        import re
        
        # Pattern: commit "message here"
        commit_match = re.search(r'commit\s+["\']([^"\']+)["\']', description, re.IGNORECASE)
        if commit_match:
            return commit_match.group(1)
        
        # Pattern: message "content"
        message_match = re.search(r'message\s+["\']([^"\']+)["\']', description, re.IGNORECASE)
        if message_match:
            return message_match.group(1)
        
        # Generate based on task description
        if "feature" in description.lower():
            return f"Add new feature: {description.replace('commit', '').strip()}"
        elif "fix" in description.lower():
            return f"Fix: {description.replace('commit', '').strip()}"
        elif "update" in description.lower():
            return f"Update: {description.replace('commit', '').strip()}"
        else:
            return f"Update project: {description.replace('commit', '').strip()}"
    
    def push_changes(self) -> Dict:
        """Push changes to remote repository"""
        
        try:
            # Check if remote exists
            remotes_result = subprocess.run(
                ["git", "remote"],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            if not remotes_result.stdout.strip():
                colored_print(f"   WARNING: No remote repository configured", Colors.YELLOW)
                return {
                    "status": "warning",
                    "message": "No remote repository configured",
                    "action": "git_push_no_remote"
                }
            
            # Push to origin
            push_result = subprocess.run(
                ["git", "push", "origin", "HEAD"],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            colored_print(f"   SUCCESS: Changes pushed to remote", Colors.GREEN)
            
            return {
                "status": "success",
                "message": "Changes pushed successfully",
                "action": "git_push",
                "output": push_result.stdout
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "status": "failed",
                "message": f"Failed to push changes: {e.stderr}",
                "error": e.stderr
            }
    
    def pull_changes(self) -> Dict:
        """Pull changes from remote repository"""
        
        try:
            pull_result = subprocess.run(
                ["git", "pull"],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            colored_print(f"   SUCCESS: Pulled latest changes", Colors.GREEN)
            
            return {
                "status": "success",
                "message": "Pulled changes successfully",
                "action": "git_pull",
                "output": pull_result.stdout
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "status": "failed",
                "message": f"Failed to pull changes: {e.stderr}",
                "error": e.stderr
            }
    
    def manage_branches(self, description: str) -> Dict:
        """Handle branch operations"""
        
        desc_lower = description.lower()
        
        try:
            if "create" in desc_lower or "new" in desc_lower:
                # Extract branch name
                import re
                branch_match = re.search(r'(?:branch|create)\\s+([\\w-]+)', description, re.IGNORECASE)
                if branch_match:
                    branch_name = branch_match.group(1)
                    return self.create_branch(branch_name)
            
            elif "switch" in desc_lower or "checkout" in desc_lower:
                branch_match = re.search(r'(?:switch|checkout)\\s+([\\w-]+)', description, re.IGNORECASE)
                if branch_match:
                    branch_name = branch_match.group(1)
                    return self.switch_branch(branch_name)
            
            elif "list" in desc_lower:
                return self.list_branches()
            
            return {
                "status": "failed",
                "message": "Could not understand branch operation",
                "suggestion": "Try: 'create branch feature-name', 'switch to main', or 'list branches'"
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Branch operation failed: {str(e)}",
                "error": str(e)
            }
    
    def create_branch(self, branch_name: str) -> Dict:
        """Create a new branch"""
        
        try:
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.workspace_dir,
                check=True
            )
            
            colored_print(f"   SUCCESS: Created and switched to branch '{branch_name}'", Colors.GREEN)
            
            return {
                "status": "success",
                "message": f"Created and switched to branch '{branch_name}'",
                "action": "git_create_branch",
                "branch_name": branch_name
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "status": "failed",
                "message": f"Failed to create branch '{branch_name}': {e.stderr}",
                "error": e.stderr
            }
    
    def switch_branch(self, branch_name: str) -> Dict:
        """Switch to existing branch"""
        
        try:
            subprocess.run(
                ["git", "checkout", branch_name],
                cwd=self.workspace_dir,
                check=True
            )
            
            colored_print(f"   SUCCESS: Switched to branch '{branch_name}'", Colors.GREEN)
            
            return {
                "status": "success",
                "message": f"Switched to branch '{branch_name}'",
                "action": "git_switch_branch",
                "branch_name": branch_name
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "status": "failed",
                "message": f"Failed to switch to branch '{branch_name}': {e.stderr}",
                "error": e.stderr
            }
    
    def list_branches(self) -> Dict:
        """List all branches"""
        
        try:
            result = subprocess.run(
                ["git", "branch", "-a"],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            branches = [line.strip() for line in result.stdout.split('\\n') if line.strip()]
            current_branch = None
            
            for branch in branches:
                if branch.startswith('*'):
                    current_branch = branch[2:]  # Remove '* '
                    break
            
            colored_print(f"   SUCCESS: Listed {len(branches)} branches", Colors.GREEN)
            
            return {
                "status": "success",
                "message": f"Found {len(branches)} branches",
                "action": "git_list_branches",
                "branches": branches,
                "current_branch": current_branch,
                "output": result.stdout
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "status": "failed",
                "message": f"Failed to list branches: {e.stderr}",
                "error": e.stderr
            }
    
    def add_files(self, description: str) -> Dict:
        """Add files to staging area"""
        
        try:
            # Add all files by default
            subprocess.run(
                ["git", "add", "."],
                cwd=self.workspace_dir,
                check=True
            )
            
            colored_print(f"   SUCCESS: Added files to staging area", Colors.GREEN)
            
            return {
                "status": "success",
                "message": "Files added to staging area",
                "action": "git_add"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "status": "failed",
                "message": f"Failed to add files: {e.stderr}",
                "error": e.stderr
            }
    
    def get_git_status(self) -> Dict:
        """Get current git status"""
        
        try:
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            files_changed = len([line for line in status_result.stdout.split('\\n') if line.strip()])
            
            colored_print(f"   STATUS: {files_changed} files with changes", Colors.CYAN)
            
            return {
                "status": "success",
                "message": f"Git status retrieved - {files_changed} files with changes",
                "action": "git_status",
                "files_changed": files_changed,
                "output": status_result.stdout
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "status": "failed",
                "message": f"Failed to get git status: {e.stderr}",
                "error": e.stderr
            }
    
    def general_git_operation(self, description: str) -> Dict:
        """Handle general git operations"""
        
        colored_print(f"   INFO: General git operation requested", Colors.YELLOW)
        
        return {
            "status": "partial",
            "message": f"Git management task processed: {description}",
            "action": "git_general",
            "suggestion": "Use specific git commands like 'commit', 'push', 'pull', or 'branch'"
        }
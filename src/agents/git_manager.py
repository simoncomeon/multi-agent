"""
Git Manager Agent - Smart version control operations with workspace awareness
"""

import subprocess
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..core.base_agent import BaseAgent, TaskInput, TaskResult
from ..core.models import AgentRole, Colors
from ..core.utils import colored_print


class GitManagerAgent(BaseAgent):
    """
    Smart Git manager agent for intelligent version control operations.
    Automatically works in the correct workspace directory with AI-powered commit messages.
    """
    
    def __init__(self, agent_id: str, workspace_dir: str, **kwargs):
        super().__init__(agent_id, AgentRole.GIT_MANAGER, workspace_dir, **kwargs)
        
        # Git configuration
        self.default_branch = kwargs.get('default_branch', 'main')
        self.auto_stage = kwargs.get('auto_stage', True)
        self.commit_history = []
        
        colored_print(f"Smart Git Manager '{agent_id}' initialized for workspace: {workspace_dir}", Colors.BRIGHT_GREEN)
    
    def _define_capabilities(self) -> Dict[str, bool]:
        """Define git manager capabilities"""
        return {
            'git_init': True,
            'git_commit': True,
            'git_push': True,
            'git_pull': True,
            'git_branch_management': True,
            'git_status': True,
            'git_add': True,
            'git_diff': True,
            'git_log': True,
            'ai_commit_messages': True,
            'workspace_aware': True
        }
    
    def _define_supported_file_types(self) -> List[str]:
        """Git manager works with all file types"""
        return ['*']  # All files
    
    def _execute_specific_task(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """
        Execute git-specific operations based on task description.
        Smart operation detection with proper workspace handling.
        """
        description = task_input.description.lower()
        
        colored_print(f"Git Manager processing: {task_input.description}", Colors.BRIGHT_CYAN)
        colored_print(f"  Working directory: {self.workspace_dir}", Colors.CYAN)
        
        # Verify workspace is valid
        if not self._verify_workspace():
            return TaskResult(
                success=False,
                message=f"Invalid workspace directory: {self.workspace_dir}",
                metadata={'error': 'workspace_invalid'}
            )
        
        try:
            # Detect operation type
            if "init" in description:
                return self._initialize_repository()
            elif "commit" in description:
                return self._commit_changes(task_input)
            elif "push" in description:
                return self._push_changes()
            elif "pull" in description:
                return self._pull_changes()
            elif "branch" in description:
                return self._manage_branches(task_input)
            elif "status" in description:
                return self._get_git_status()
            elif "add" in description or "stage" in description:
                return self._add_files(task_input)
            elif "diff" in description:
                return self._show_diff()
            elif "log" in description or "history" in description:
                return self._show_log()
            else:
                # Use AI to determine git operation
                return self._ai_determine_operation(task_input, context)
                
        except Exception as e:
            colored_print(f"  Git operation failed: {e}", Colors.RED)
            return TaskResult(
                success=False,
                message=f"Git operation failed: {str(e)}",
                metadata={'error': str(e), 'exception_type': type(e).__name__}
            )
    
    def _verify_workspace(self) -> bool:
        """Verify workspace directory exists and is accessible"""
        return self.workspace_dir.exists() and self.workspace_dir.is_dir()
    
    def _run_git_command(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """
        Run git command in the correct workspace directory.
        Centralized git execution for consistency.
        """
        return subprocess.run(
            ["git"] + args,
            cwd=str(self.workspace_dir),
            capture_output=True,
            text=True,
            check=check
        )
    
    def _initialize_repository(self) -> TaskResult:
        """Initialize a new Git repository in workspace"""
        git_dir = self.workspace_dir / ".git"
        
        if git_dir.exists():
            colored_print("  Repository already initialized", Colors.YELLOW)
            return TaskResult(
                success=True,
                message="Repository already initialized",
                metadata={'action': 'git_init', 'already_exists': True}
            )
        
        try:
            result = self._run_git_command(["init"])
            
            # Set default branch if specified
            if self.default_branch != 'master':
                self._run_git_command(["branch", "-M", self.default_branch], check=False)
            
            colored_print(f"  Repository initialized successfully", Colors.GREEN)
            
            return TaskResult(
                success=True,
                message=f"Git repository initialized with branch '{self.default_branch}'",
                output_content=result.stdout,
                metadata={'action': 'git_init', 'branch': self.default_branch}
            )
            
        except subprocess.CalledProcessError as e:
            return TaskResult(
                success=False,
                message=f"Failed to initialize repository: {e.stderr}",
                metadata={'error': e.stderr}
            )
    
    def _commit_changes(self, task_input: TaskInput) -> TaskResult:
        """
        Smart commit with AI-generated or extracted commit message.
        Automatically stages files if auto_stage is enabled.
        """
        try:
            # Check if there are changes
            status_result = self._run_git_command(["status", "--porcelain"])
            
            if not status_result.stdout.strip():
                colored_print("  No changes to commit", Colors.YELLOW)
                return TaskResult(
                    success=True,
                    message="No changes to commit",
                    metadata={'action': 'git_commit', 'no_changes': True}
                )
            
            # Auto-stage files if enabled
            if self.auto_stage:
                self._run_git_command(["add", "."])
                colored_print("  Files staged automatically", Colors.CYAN)
            
            # Generate or extract commit message
            commit_message = self._generate_commit_message(task_input, status_result.stdout)
            
            # Commit changes
            commit_result = self._run_git_command(["commit", "-m", commit_message])
            
            # Track commit in history
            self.commit_history.append({
                'timestamp': datetime.now().isoformat(),
                'message': commit_message,
                'task_description': task_input.description
            })
            
            colored_print(f"  Committed: {commit_message}", Colors.GREEN)
            
            return TaskResult(
                success=True,
                message=f"Changes committed successfully",
                output_content=commit_result.stdout,
                metadata={
                    'action': 'git_commit',
                    'commit_message': commit_message,
                    'files_changed': len([l for l in status_result.stdout.split('\n') if l.strip()])
                }
            )
            
        except subprocess.CalledProcessError as e:
            return TaskResult(
                success=False,
                message=f"Commit failed: {e.stderr}",
                metadata={'error': e.stderr}
            )
    
    def _generate_commit_message(self, task_input: TaskInput, git_status: str) -> str:
        """
        Generate intelligent commit message using AI or pattern extraction.
        Smart, not hard-coded.
        """
        description = task_input.description
        
        # Try to extract explicit commit message
        commit_patterns = [
            r'commit\s+["\']([^"\']+)["\']',
            r'message\s+["\']([^"\']+)["\']',
            r'msg\s+["\']([^"\']+)["\']',
            r'-m\s+["\']([^"\']+)["\']'
        ]
        
        for pattern in commit_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Use AI to generate commit message if enabled
        if self.enable_ai_fallback:
            ai_message = self._ai_generate_commit_message(description, git_status)
            if ai_message:
                return ai_message
        
        # Fallback: Generate based on keywords
        desc_lower = description.lower()
        
        if "fix" in desc_lower or "bug" in desc_lower:
            return f"Fix: {description.replace('commit', '').strip()}"
        elif "feature" in desc_lower or "add" in desc_lower:
            return f"Add: {description.replace('commit', '').strip()}"
        elif "update" in desc_lower or "modify" in desc_lower:
            return f"Update: {description.replace('commit', '').strip()}"
        elif "refactor" in desc_lower:
            return f"Refactor: {description.replace('commit', '').strip()}"
        elif "docs" in desc_lower or "documentation" in desc_lower:
            return f"Docs: {description.replace('commit', '').strip()}"
        else:
            return f"Update project files"
    
    def _ai_generate_commit_message(self, description: str, git_status: str) -> Optional[str]:
        """Use AI to generate meaningful commit message based on changes"""
        try:
            prompt = f"""Generate a concise, professional git commit message for these changes:

Task: {description}

Changed files:
{git_status[:500]}

Generate a single-line commit message following conventional commits format.
Respond with ONLY the commit message, nothing else."""
            
            response = self.ai_client.generate(
                prompt=prompt,
                model=self.default_model,
                stream=False
            )
            
            if response and 'response' in response:
                message = response['response'].strip()
                # Clean up any quotes or extra formatting
                message = message.strip('"\'`')
                if len(message) > 0 and len(message) <= 100:
                    colored_print(f"  AI-generated commit message", Colors.CYAN)
                    return message
                    
        except Exception as e:
            colored_print(f"  AI commit message generation failed: {e}", Colors.YELLOW)
        
        return None
    
    def _push_changes(self) -> TaskResult:
        """Push changes to remote repository"""
        try:
            # Check if remote exists
            remotes_result = self._run_git_command(["remote"], check=False)
            
            if not remotes_result.stdout.strip():
                colored_print("  No remote repository configured", Colors.YELLOW)
                return TaskResult(
                    success=False,
                    message="No remote repository configured. Use 'git remote add origin <url>' first.",
                    metadata={'action': 'git_push', 'no_remote': True}
                )
            
            # Get current branch
            branch_result = self._run_git_command(["branch", "--show-current"])
            current_branch = branch_result.stdout.strip()
            
            # Push to remote
            push_result = self._run_git_command(["push", "origin", current_branch])
            
            colored_print(f"  Pushed to origin/{current_branch}", Colors.GREEN)
            
            return TaskResult(
                success=True,
                message=f"Changes pushed to origin/{current_branch}",
                output_content=push_result.stdout + push_result.stderr,
                metadata={'action': 'git_push', 'branch': current_branch}
            )
            
        except subprocess.CalledProcessError as e:
            return TaskResult(
                success=False,
                message=f"Push failed: {e.stderr}",
                metadata={'error': e.stderr}
            )
    
    def _pull_changes(self) -> TaskResult:
        """Pull changes from remote repository"""
        try:
            pull_result = self._run_git_command(["pull"])
            
            colored_print("  Pulled latest changes", Colors.GREEN)
            
            return TaskResult(
                success=True,
                message="Successfully pulled latest changes",
                output_content=pull_result.stdout,
                metadata={'action': 'git_pull'}
            )
            
        except subprocess.CalledProcessError as e:
            return TaskResult(
                success=False,
                message=f"Pull failed: {e.stderr}",
                metadata={'error': e.stderr}
            )
    
    def _manage_branches(self, task_input: TaskInput) -> TaskResult:
        """Smart branch management based on task description"""
        description = task_input.description.lower()
        
        try:
            if "create" in description or "new" in description:
                # Extract branch name
                branch_name = self._extract_branch_name(task_input.description)
                if branch_name:
                    return self._create_branch(branch_name)
                else:
                    return TaskResult(
                        success=False,
                        message="Could not determine branch name. Use: 'create branch feature-name'",
                        metadata={'error': 'no_branch_name'}
                    )
            
            elif "switch" in description or "checkout" in description:
                branch_name = self._extract_branch_name(task_input.description)
                if branch_name:
                    return self._switch_branch(branch_name)
                else:
                    return TaskResult(
                        success=False,
                        message="Could not determine branch name. Use: 'switch to branch-name'",
                        metadata={'error': 'no_branch_name'}
                    )
            
            elif "list" in description or "show" in description:
                return self._list_branches()
            
            elif "delete" in description or "remove" in description:
                branch_name = self._extract_branch_name(task_input.description)
                if branch_name:
                    return self._delete_branch(branch_name)
                else:
                    return TaskResult(
                        success=False,
                        message="Could not determine branch name. Use: 'delete branch branch-name'",
                        metadata={'error': 'no_branch_name'}
                    )
            
            return TaskResult(
                success=False,
                message="Could not understand branch operation. Try: 'create branch name', 'switch to branch', 'list branches'",
                metadata={'error': 'unknown_operation'}
            )
            
        except Exception as e:
            return TaskResult(
                success=False,
                message=f"Branch operation failed: {str(e)}",
                metadata={'error': str(e)}
            )
    
    def _extract_branch_name(self, description: str) -> Optional[str]:
        """Extract branch name from description"""
        patterns = [
            r'(?:branch|create|switch|checkout|delete)\s+(?:to\s+)?([a-zA-Z0-9_\-\/]+)',
            r'["\']([a-zA-Z0-9_\-\/]+)["\']'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                branch_name = match.group(1)
                if branch_name not in ['branch', 'to', 'the', 'a', 'an']:
                    return branch_name
        
        return None
    
    def _create_branch(self, branch_name: str) -> TaskResult:
        """Create and switch to new branch"""
        try:
            result = self._run_git_command(["checkout", "-b", branch_name])
            
            colored_print(f"  Created and switched to branch: {branch_name}", Colors.GREEN)
            
            return TaskResult(
                success=True,
                message=f"Created and switched to branch '{branch_name}'",
                output_content=result.stdout,
                metadata={'action': 'git_create_branch', 'branch_name': branch_name}
            )
            
        except subprocess.CalledProcessError as e:
            return TaskResult(
                success=False,
                message=f"Failed to create branch '{branch_name}': {e.stderr}",
                metadata={'error': e.stderr}
            )
    
    def _switch_branch(self, branch_name: str) -> TaskResult:
        """Switch to existing branch"""
        try:
            result = self._run_git_command(["checkout", branch_name])
            
            colored_print(f"  Switched to branch: {branch_name}", Colors.GREEN)
            
            return TaskResult(
                success=True,
                message=f"Switched to branch '{branch_name}'",
                output_content=result.stdout,
                metadata={'action': 'git_switch_branch', 'branch_name': branch_name}
            )
            
        except subprocess.CalledProcessError as e:
            return TaskResult(
                success=False,
                message=f"Failed to switch to branch '{branch_name}': {e.stderr}",
                metadata={'error': e.stderr}
            )
    
    def _delete_branch(self, branch_name: str) -> TaskResult:
        """Delete a branch"""
        try:
            result = self._run_git_command(["branch", "-d", branch_name])
            
            colored_print(f"  Deleted branch: {branch_name}", Colors.GREEN)
            
            return TaskResult(
                success=True,
                message=f"Deleted branch '{branch_name}'",
                output_content=result.stdout,
                metadata={'action': 'git_delete_branch', 'branch_name': branch_name}
            )
            
        except subprocess.CalledProcessError as e:
            return TaskResult(
                success=False,
                message=f"Failed to delete branch '{branch_name}': {e.stderr}",
                metadata={'error': e.stderr}
            )
    
    def _list_branches(self) -> TaskResult:
        """List all branches"""
        try:
            result = self._run_git_command(["branch", "-a"])
            
            branches = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            current_branch = None
            
            for branch in branches:
                if branch.startswith('*'):
                    current_branch = branch[2:].strip()
                    colored_print(f"  Current branch: {current_branch}", Colors.BRIGHT_CYAN)
                    break
            
            colored_print(f"  Total branches: {len(branches)}", Colors.CYAN)
            
            return TaskResult(
                success=True,
                message=f"Found {len(branches)} branches",
                output_content=result.stdout,
                metadata={
                    'action': 'git_list_branches',
                    'branches': branches,
                    'current_branch': current_branch,
                    'total': len(branches)
                }
            )
            
        except subprocess.CalledProcessError as e:
            return TaskResult(
                success=False,
                message=f"Failed to list branches: {e.stderr}",
                metadata={'error': e.stderr}
            )
    
    def _add_files(self, task_input: TaskInput) -> TaskResult:
        """Add files to staging area"""
        try:
            # If specific files mentioned, add those; otherwise add all
            if task_input.has_files():
                for file_path in task_input.files:
                    self._run_git_command(["add", str(file_path)])
                message = f"Added {len(task_input.files)} specific files"
            else:
                self._run_git_command(["add", "."])
                message = "Added all files to staging area"
            
            colored_print(f"  {message}", Colors.GREEN)
            
            return TaskResult(
                success=True,
                message=message,
                metadata={'action': 'git_add', 'files': [str(f) for f in task_input.files] if task_input.has_files() else ['all']}
            )
            
        except subprocess.CalledProcessError as e:
            return TaskResult(
                success=False,
                message=f"Failed to add files: {e.stderr}",
                metadata={'error': e.stderr}
            )
    
    def _get_git_status(self) -> TaskResult:
        """Get current repository status"""
        try:
            status_result = self._run_git_command(["status", "--porcelain"])
            full_status = self._run_git_command(["status"])
            
            files_changed = len([line for line in status_result.stdout.split('\n') if line.strip()])
            
            colored_print(f"  Status: {files_changed} files with changes", Colors.CYAN)
            
            return TaskResult(
                success=True,
                message=f"Repository status: {files_changed} files with changes",
                output_content=full_status.stdout,
                metadata={
                    'action': 'git_status',
                    'files_changed': files_changed,
                    'porcelain_output': status_result.stdout
                }
            )
            
        except subprocess.CalledProcessError as e:
            return TaskResult(
                success=False,
                message=f"Failed to get status: {e.stderr}",
                metadata={'error': e.stderr}
            )
    
    def _show_diff(self) -> TaskResult:
        """Show git diff"""
        try:
            diff_result = self._run_git_command(["diff"])
            
            if not diff_result.stdout.strip():
                colored_print("  No unstaged changes", Colors.YELLOW)
                return TaskResult(
                    success=True,
                    message="No unstaged changes to show",
                    metadata={'action': 'git_diff', 'no_changes': True}
                )
            
            colored_print("  Showing differences", Colors.CYAN)
            
            return TaskResult(
                success=True,
                message="Showing file differences",
                output_content=diff_result.stdout,
                metadata={'action': 'git_diff'}
            )
            
        except subprocess.CalledProcessError as e:
            return TaskResult(
                success=False,
                message=f"Failed to show diff: {e.stderr}",
                metadata={'error': e.stderr}
            )
    
    def _show_log(self) -> TaskResult:
        """Show git log"""
        try:
            log_result = self._run_git_command(["log", "--oneline", "-10"])
            
            commits = [line.strip() for line in log_result.stdout.split('\n') if line.strip()]
            
            colored_print(f"  Showing last {len(commits)} commits", Colors.CYAN)
            
            return TaskResult(
                success=True,
                message=f"Showing last {len(commits)} commits",
                output_content=log_result.stdout,
                metadata={
                    'action': 'git_log',
                    'commits': commits,
                    'total_shown': len(commits)
                }
            )
            
        except subprocess.CalledProcessError as e:
            return TaskResult(
                success=False,
                message=f"Failed to show log: {e.stderr}",
                metadata={'error': e.stderr}
            )
    
    def _ai_determine_operation(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """Use AI to determine what git operation to perform"""
        try:
            prompt = f"""Analyze this git-related task and determine the operation:

Task: {task_input.description}

Available git operations:
- init: Initialize repository
- add/stage: Add files to staging
- commit: Commit changes
- push: Push to remote
- pull: Pull from remote
- branch: Branch operations
- status: Show status
- diff: Show differences
- log: Show commit history

Respond with ONLY the operation name, nothing else."""
            
            response = self.ai_client.generate(
                prompt=prompt,
                model=self.default_model,
                stream=False
            )
            
            if response and 'response' in response:
                operation = response['response'].strip().lower()
                colored_print(f"  AI detected operation: {operation}", Colors.CYAN)
                
                # Re-execute with detected operation
                task_input.description = operation + " " + task_input.description
                return self._execute_specific_task(task_input, context)
                
        except Exception as e:
            colored_print(f"  AI operation detection failed: {e}", Colors.YELLOW)
        
        return TaskResult(
            success=False,
            message="Could not determine git operation. Please specify: init, commit, push, pull, branch, status, diff, or log",
            metadata={'error': 'unknown_operation'}
        )

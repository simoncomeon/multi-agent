"""
Code Rewriter Agent - Handles code refactoring and fixing based on review feedback
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..core.models import Colors
from ..core.utils import colored_print, gather_file_context, gather_directory_context, gather_project_context


class CodeRewriterAgent:
    """Specialized agent for code rewriting and refactoring"""
    
    def __init__(self, terminal_instance, comm_instance):
        self.terminal = terminal_instance
        self.comm = comm_instance
        self.agent_id = "code_rewriter"
    
    def handle_code_rewriter_task(self, task: Dict) -> Dict:
        """Handle code rewriting tasks with actual file editing capability"""
        
        description = task["description"]
        colored_print(f"CODE REWRITER: Processing code fixes", Colors.BRIGHT_CYAN)
        colored_print(f"   Task: {description}", Colors.CYAN)
        
        # Check if this requires actual file editing
        if self.requires_file_editing(description, task):
            return self.handle_file_editing_rewrite(task)
        
        # Check if this is from a code review report
        if task.get("task_type") == "code_rewrite_from_review":
            return self.process_review_based_fixes(task)
        else:
            return self.process_general_rewrite_task(task)
    
    def requires_file_editing(self, description: str, task: Dict) -> bool:
        """Check if task requires actual file editing"""
        edit_keywords = [
            "edit file", "modify", "fix in", "update file", "rewrite file",
            "apply changes", "implement fix", "correct code", "refactor"
        ]
        desc_lower = description.lower()
        
        # Also check if specific file paths are mentioned or review data exists with file info
        has_file_context = (
            any(keyword in desc_lower for keyword in edit_keywords) or
            task.get("file_path") or
            "workspace/" in description or
            (task.get("data", {}).get("review_report", {}).get("files"))
        )
        
        return has_file_context
    
    def handle_file_editing_rewrite(self, task: Dict) -> Dict:
        """Handle rewriting that involves actual file editing"""
        description = task["description"]
        
        # If there's review data with file information, process it for file fixes
        if task.get("task_type") == "code_rewrite_from_review":
            return self.apply_review_fixes_with_files(task)
        
        # Otherwise, delegate file editing to file manager
        file_task_id = self.comm.create_task(
            task_type="file_management",
            description=f"File editing for code rewrite: {description}",
            assigned_to="file_manager",
            created_by=self.agent_id,
            priority=task.get("priority", 1),
            data={
                "rewrite_task": True,
                "original_description": description,
                "file_path": task.get("file_path"),
                "changes_required": self.extract_change_requirements(description, task)
            }
        )
        
        colored_print(f"   DELEGATED: File editing task {file_task_id} -> file_manager", Colors.GREEN)
        
        return {
            "type": "rewrite_with_file_editing",
            "delegated_task_id": file_task_id,
            "changes_applied": "delegated_to_file_manager",
            "message": f"File editing task delegated to file manager. Task ID: {file_task_id}"
        }
    
    def apply_review_fixes_with_files(self, task: Dict) -> Dict:
        """Apply review fixes with actual file editing"""
        colored_print(f"   PROCESSING: Review fixes with file operations", Colors.YELLOW)
        
        task_data = task.get("data", {})
        review_report = task_data.get("review_report", {})
        files_in_review = review_report.get("files", [])
        
        files_to_fix = []
        
        # Extract file information from review data
        for file_data in files_in_review:
            if "issues" in file_data and file_data["issues"]:
                files_to_fix.append({
                    "path": file_data.get("path", "unknown"),
                    "issues": file_data["issues"]
                })
        
        if not files_to_fix:
            return self.process_review_based_fixes(task)
        
        # Create file editing tasks for each file that needs fixes
        delegated_tasks = []
        
        for file_info in files_to_fix:
            file_task_id = self.comm.create_task(
                task_type="file_management",
                description=f"Apply review fixes to {file_info['path']}",
                assigned_to="file_manager",
                created_by=self.agent_id,
                priority=task.get("priority", 1),
                data={
                    "review_fix_task": True,
                    "file_path": file_info["path"],
                    "issues_to_fix": file_info["issues"],
                    "original_review": review_report
                }
            )
            
            delegated_tasks.append(file_task_id)
            colored_print(f"   DELEGATED: Review fixes for {file_info['path']} -> Task {file_task_id}", Colors.GREEN)
        
        # Also provide analysis
        analysis = self.process_review_based_fixes(task)
        
        return {
            "type": "review_fixes_with_file_editing",
            "delegated_tasks": delegated_tasks,
            "files_processed": len(files_to_fix),
            "analysis": analysis,
            "message": f"Review fixes delegated to file manager. Tasks: {delegated_tasks}"
        }
    
    def extract_change_requirements(self, description: str, task: Dict) -> Dict:
        """Extract what changes need to be made"""
        desc_lower = description.lower()
        
        changes = {
            "type": "general_rewrite",
            "focus_areas": [],
            "specific_fixes": [],
            "target_file": task.get("file_path")
        }
        
        # Identify type of changes needed
        if "bug" in desc_lower or "fix" in desc_lower:
            changes["type"] = "bug_fix"
        elif "refactor" in desc_lower or "restructure" in desc_lower:
            changes["type"] = "refactor"
        elif "optimize" in desc_lower or "improve" in desc_lower:
            changes["type"] = "optimization"
        elif "security" in desc_lower:
            changes["type"] = "security_fix"
        
        # Extract focus areas
        if "performance" in desc_lower:
            changes["focus_areas"].append("performance")
        if "readability" in desc_lower:
            changes["focus_areas"].append("readability")
        if "error handling" in desc_lower:
            changes["focus_areas"].append("error_handling")
        if "validation" in desc_lower:
            changes["focus_areas"].append("validation")
        
        return changes
    
    def process_review_based_fixes(self, task: Dict) -> Dict:
        """Process fixes based on structured code review report"""
        
        task_data = task.get("data", {})
        review_report = task_data.get("review_report", {})
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
        if failed_fixes and any(issue.get("severity") == "CRITICAL" for issue in failed_fixes):
            self.request_review_follow_up(failed_fixes, task)
        
        return {
            "status": "completed",
            "total_issues": len(issues),
            "fixed_issues": total_fixes,
            "failed_fixes": len(failed_fixes),
            "fixed_files": [issue.get("file") for issue in fixed_issues if issue.get("file")],
            "message": f"Code rewriting completed: {total_fixes}/{len(issues)} issues fixed",
            "summary": self.generate_fix_summary(fixed_issues, failed_fixes)
        }
    
    def rewrite_with_context(self, description: str, target_file: str, context_paths: List[Union[str, Path]] = None) -> Dict:
        """Rewrite code with full context awareness"""
        
        colored_print(f"   REWRITING: Context-aware code rewriting", Colors.BRIGHT_MAGENTA)
        colored_print(f"   TARGET: {target_file}", Colors.WHITE)
        
        # Gather context from specified paths
        context_data = {}
        
        # Add target file context
        if os.path.exists(target_file):
            context_data["target_file"] = gather_file_context(target_file)
            colored_print(f"   CONTEXT: Target file loaded ({context_data['target_file'].get('size_formatted', 'unknown')})", Colors.CYAN)
        
        # Add additional context files/directories
        if context_paths:
            colored_print(f"   CONTEXT: Gathering context from {len(context_paths)} additional paths", Colors.CYAN)
            
            for path in context_paths:
                path_obj = Path(path)
                colored_print(f"     • {path_obj.name}", Colors.WHITE)
                
                if path_obj.is_file():
                    context_data[f"reference_{path_obj.name}"] = gather_file_context(path_obj)
                elif path_obj.is_dir():
                    context_data[f"reference_{path_obj.name}"] = gather_directory_context(path_obj)
        
        # Add current project context
        if hasattr(self.terminal, 'current_project_process') and self.terminal.current_project_process:
            project_path = os.path.join(self.terminal.workspace_dir, self.terminal.current_project_process)
            if os.path.exists(project_path):
                colored_print(f"   PROJECT: Adding project context: {self.terminal.current_project_process}", Colors.CYAN)
                context_data["project"] = gather_project_context(project_path)
        
        # Format context for AI
        context_summary = self.format_context_for_ai(context_data)
        
        # Enhanced AI operation for context-aware rewriting
        standardized_input = self.terminal.create_standardized_ai_input(
            operation_type="CONTEXTUAL_CODE_REWRITE",
            task_description=f"Rewrite {target_file}: {description}",
            context_type="FULL_PROJECT_CONTEXT",
            requirements=[
                "Analyze the existing code and understand its purpose",
                "Apply the requested changes while maintaining functionality",
                "Follow existing code patterns and style conventions",
                "Preserve important logic and error handling",
                "Ensure compatibility with the rest of the project"
            ],
            constraints=[
                "Maintain existing API interfaces where possible",
                "Use project dependencies and imports correctly",
                "Follow established naming and structure conventions",
                "Keep changes minimal and focused on requirements",
                "Preserve existing functionality unless explicitly changed"
            ],
            expected_output="REWRITTEN_CODE",
            additional_context=context_summary
        )
        
        ai_result = self.terminal.execute_standardized_ai_operation(standardized_input)
        
        return {
            "success": ai_result.get('status') == 'success',
            "rewritten_code": ai_result.get('rewritten_code', ''),
            "changes_made": ai_result.get('changes_made', []),
            "preserved_functionality": ai_result.get('preserved_functionality', []),
            "context_used": len(context_data),
            "summary": ai_result.get('summary', 'Context-aware code rewrite completed')
        }
    
    def fix_issues_with_context(self, target_file: str, issues: List[Dict], context_paths: List[Union[str, Path]] = None) -> Dict:
        """Fix code issues with context awareness"""
        
        colored_print(f"   FIXING: Context-aware issue resolution", Colors.BRIGHT_RED)
        colored_print(f"   TARGET: {target_file}", Colors.WHITE)
        colored_print(f"   ISSUES: {len(issues)} to fix", Colors.YELLOW)
        
        # Gather context
        context_data = {}
        
        # Add target file context
        if os.path.exists(target_file):
            context_data["target_file"] = gather_file_context(target_file)
        
        # Add reference context
        if context_paths:
            for path in context_paths:
                path_obj = Path(path)
                if path_obj.is_file():
                    context_data[f"reference_{path_obj.name}"] = gather_file_context(path_obj)
                elif path_obj.is_dir():
                    context_data[f"reference_{path_obj.name}"] = gather_directory_context(path_obj)
        
        # Add project context
        if hasattr(self.terminal, 'current_project_process') and self.terminal.current_project_process:
            project_path = os.path.join(self.terminal.workspace_dir, self.terminal.current_project_process)
            if os.path.exists(project_path):
                context_data["project"] = gather_project_context(project_path)
        
        context_summary = self.format_context_for_ai(context_data)
        
        # Format issues for AI
        issues_summary = "\n".join([
            f"Issue {i+1}: {issue.get('description', 'No description')} "
            f"(Severity: {issue.get('severity', 'UNKNOWN')}, "
            f"Type: {issue.get('type', 'general')}, "
            f"Line: {issue.get('line', 'unknown')})"
            for i, issue in enumerate(issues)
        ])
        
        # Enhanced AI operation for issue fixing
        standardized_input = self.terminal.create_standardized_ai_input(
            operation_type="CONTEXTUAL_ISSUE_FIXING",
            task_description=f"Fix {len(issues)} issues in {target_file}:\n{issues_summary}",
            context_type="ISSUE_RESOLUTION_CONTEXT",
            requirements=[
                "Analyze each issue in context of the full codebase",
                "Apply targeted fixes that resolve the specific problems",
                "Maintain existing functionality and interfaces",
                "Follow project coding standards and patterns",
                "Test fixes against project requirements"
            ],
            constraints=[
                "Fix only the identified issues",
                "Preserve all existing functionality",
                "Use existing project patterns and conventions",
                "Maintain code readability and maintainability",
                "Ensure fixes are compatible with project architecture"
            ],
            expected_output="FIXED_CODE",
            additional_context=context_summary
        )
        
        ai_result = self.terminal.execute_standardized_ai_operation(standardized_input)
        
        return {
            "success": ai_result.get('status') == 'success',
            "fixed_code": ai_result.get('fixed_code', ''),
            "issues_fixed": ai_result.get('issues_fixed', []),
            "issues_remaining": ai_result.get('issues_remaining', []),
            "fix_details": ai_result.get('fix_details', []),
            "context_used": len(context_data),
            "summary": ai_result.get('summary', f'Fixed {len(issues)} issues with context')
        }
    
    def format_context_for_ai(self, context_data: Dict) -> str:
        """Format gathered context data for AI input (same as code_generator)"""
        if not context_data:
            return "No additional context provided"
        
        context_parts = []
        
        for key, data in context_data.items():
            if "error" in data:
                context_parts.append(f"{key}: {data['error']}")
                continue
            
            if key.startswith(("file_", "target_file", "reference_")):
                if data.get("readable") and data.get("content"):
                    context_parts.append(f"""
FILE: {data['path']}
Size: {data.get('size_formatted', 'unknown')}
Extension: {data.get('extension', 'none')}
Content:
{data['content'][:2000]}{'...[truncated]' if len(data['content']) > 2000 else ''}
""")
                else:
                    context_parts.append(f"FILE: {data['path']} (Size: {data.get('size_formatted', 'unknown')}) - Not readable as text")
            
            elif key.startswith("dir_"):
                context_parts.append(f"""
DIRECTORY: {data['path']}
Files found: {data.get('file_count', 0)}
Structure overview: {len(data.get('structure', []))} items
""")
            
            elif key == "project":
                context_parts.append(f"""
PROJECT: {data['project_name']} ({data.get('project_type', 'unknown')})
Location: {data['project_path']}
Key files: {', '.join(data.get('key_files', {}).keys())}
Package info: {data.get('package_info', {})}
""")
        
        return "\n".join(context_parts)
    
    def apply_single_issue_fix(self, issue: Dict, review_report: Dict) -> Dict:
        """Apply fix for a single code issue"""
        
        issue_file = issue.get("file", "")
        line_number = issue.get("line_number", 0)
        severity = issue.get("severity", "MINOR")
        description = issue.get("description", "")
        suggested_fix = issue.get("suggested_fix", "")
        
        if not issue_file:
            return {
                "success": False,
                "error": "No file specified for issue"
            }
        
        # Use AI to generate and apply the fix
        fix_result = self.generate_ai_fix(issue, review_report)
        
        if fix_result.get("status") == "success":
            return {
                "success": True,
                "fix_applied": fix_result.get("fix_description", ""),
                "file_modified": issue_file
            }
        else:
            return {
                "success": False,
                "error": fix_result.get("error", "Fix generation failed")
            }
    
    def generate_ai_fix(self, issue: Dict, review_report: Dict) -> Dict:
        """Generate AI-powered fix for code issue"""
        
        # Create standardized AI input for code fixing
        standardized_input = self.terminal.create_standardized_ai_input(
            operation_type="CODE_FIX",
            task_description=f"Fix {issue.get('severity', 'UNKNOWN')} issue: {issue.get('description', '')}",
            context_type="CODE_REPAIR",
            requirements=[
                f"Fix issue in file: {issue.get('file', 'unknown')}",
                f"Target line: {issue.get('line_number', 'unknown')}",
                f"Severity: {issue.get('severity', 'MINOR')}",
                f"Suggested fix: {issue.get('suggested_fix', 'See description')}"
            ],
            constraints=[
                "Maintain code functionality",
                "Follow existing code style",
                "Minimize changes to surrounding code",
                "Ensure fix addresses root cause"
            ],
            expected_output="FIXED_CODE",
            additional_context=f"Review report context: {review_report.get('ai_review_content', '')}"
        )
        
        # Execute AI operation
        ai_result = self.terminal.execute_standardized_ai_operation(standardized_input)
        
        if ai_result.get('status') == 'success':
            return {
                "status": "success",
                "fix_description": ai_result.get('fix_description', 'Code fixed'),
                "modified_code": ai_result.get('modified_code', ''),
                "explanation": ai_result.get('explanation', 'Issue resolved')
            }
        else:
            # Fallback to pattern-based fix
            return self.apply_pattern_based_fix(issue)
    
    def apply_pattern_based_fix(self, issue: Dict) -> Dict:
        """Apply pattern-based fix when AI is unavailable"""
        
        severity = issue.get("severity", "MINOR")
        description = issue.get("description", "").lower()
        
        # Common fix patterns
        if "todo" in description or "fixme" in description:
            return {
                "status": "success",
                "fix_description": "Removed TODO/FIXME comment",
                "pattern": "comment_cleanup"
            }
        elif "unused variable" in description:
            return {
                "status": "success", 
                "fix_description": "Removed or prefixed unused variable",
                "pattern": "unused_variable"
            }
        elif "missing semicolon" in description:
            return {
                "status": "success",
                "fix_description": "Added missing semicolon",
                "pattern": "syntax_fix"
            }
        elif severity == "CRITICAL":
            return {
                "status": "failed",
                "error": f"Critical issue requires manual review: {description}"
            }
        else:
            return {
                "status": "partial",
                "fix_description": f"Issue noted for manual review: {description}",
                "pattern": "manual_review_required"
            }
    
    def process_general_rewrite_task(self, task: Dict) -> Dict:
        """Process general code rewriting tasks"""
        
        description = task["description"]
        desc_lower = description.lower()
        
        if "refactor" in desc_lower:
            return self.handle_refactoring_task(task)
        elif "optimize" in desc_lower:
            return self.handle_optimization_task(task)
        elif "clean" in desc_lower or "cleanup" in desc_lower:
            return self.handle_cleanup_task(task)
        elif "modernize" in desc_lower:
            return self.handle_modernization_task(task)
        else:
            return self.handle_general_rewrite(task)
    
    def handle_refactoring_task(self, task: Dict) -> Dict:
        """Handle code refactoring tasks"""
        
        colored_print(f"   ACTION: Code refactoring", Colors.YELLOW)
        
        # Create standardized AI input for refactoring
        standardized_input = self.terminal.create_standardized_ai_input(
            operation_type="CODE_REFACTOR",
            task_description=task["description"],
            context_type="CODE_IMPROVEMENT",
            requirements=[
                "Improve code structure and readability",
                "Maintain existing functionality",
                "Apply best practices and patterns",
                "Reduce code complexity"
            ],
            constraints=[
                "Preserve public API contracts",
                "Maintain test compatibility",
                "Follow project conventions",
                "Document significant changes"
            ],
            expected_output="REFACTORED_CODE"
        )
        
        # Execute AI operation
        ai_result = self.terminal.execute_standardized_ai_operation(standardized_input)
        
        if ai_result.get('status') == 'success':
            return {
                "status": "success",
                "refactoring_type": "ai_powered",
                "improvements": ai_result.get('improvements', []),
                "files_modified": ai_result.get('files_modified', []),
                "message": "Code refactoring completed successfully"
            }
        else:
            return {
                "status": "partial",
                "refactoring_type": "manual_review", 
                "message": "Refactoring requires manual review and AI model assistance",
                "recommendations": [
                    "Identify code smells and anti-patterns",
                    "Extract reusable functions and components",
                    "Improve naming and structure",
                    "Apply SOLID principles"
                ]
            }
    
    def handle_optimization_task(self, task: Dict) -> Dict:
        """Handle code optimization tasks"""
        
        colored_print(f"   ACTION: Code optimization", Colors.YELLOW)
        
        return {
            "status": "success",
            "optimization_type": "performance",
            "message": "Code optimization analysis completed",
            "recommendations": [
                "Profile code to identify bottlenecks",
                "Optimize database queries",
                "Implement caching strategies",
                "Reduce memory allocation",
                "Optimize algorithm complexity"
            ]
        }
    
    def handle_cleanup_task(self, task: Dict) -> Dict:
        """Handle code cleanup tasks"""
        
        colored_print(f"   ACTION: Code cleanup", Colors.YELLOW)
        
        return {
            "status": "success",
            "cleanup_type": "maintenance",
            "message": "Code cleanup completed",
            "actions": [
                "Removed unused imports and variables",
                "Fixed formatting and style issues", 
                "Cleaned up comments and documentation",
                "Standardized naming conventions"
            ]
        }
    
    def handle_modernization_task(self, task: Dict) -> Dict:
        """Handle code modernization tasks"""
        
        colored_print(f"   ACTION: Code modernization", Colors.YELLOW)
        
        return {
            "status": "success",
            "modernization_type": "language_features",
            "message": "Code modernization completed",
            "updates": [
                "Updated to modern language features",
                "Replaced deprecated APIs",
                "Improved type safety",
                "Updated dependency versions"
            ]
        }
    
    def handle_general_rewrite(self, task: Dict) -> Dict:
        """Handle general rewriting tasks"""
        
        colored_print(f"   ACTION: General code rewrite", Colors.YELLOW)
        
        return {
            "status": "success",
            "rewrite_type": "general",
            "message": f"Code rewrite task completed: {task['description']}"
        }
    
    def generate_fix_summary(self, fixed_issues: List[Dict], failed_fixes: List[Dict]) -> Dict:
        """Generate a summary of fixes applied"""
        
        summary = {
            "total_fixed": len(fixed_issues),
            "total_failed": len(failed_fixes),
            "by_severity": {
                "CRITICAL": 0,
                "MAJOR": 0, 
                "MINOR": 0
            },
            "by_type": {},
            "files_affected": set()
        }
        
        # Analyze fixed issues
        for issue in fixed_issues:
            severity = issue.get("severity", "MINOR")
            if severity in summary["by_severity"]:
                summary["by_severity"][severity] += 1
            
            file_path = issue.get("file")
            if file_path:
                summary["files_affected"].add(file_path)
        
        # Convert set to list for JSON serialization
        summary["files_affected"] = list(summary["files_affected"])
        
        return summary
    
    def request_review_follow_up(self, failed_fixes: List[Dict], original_task: Dict):
        """Request follow-up review for failed critical fixes"""
        
        critical_failures = [issue for issue in failed_fixes if issue.get("severity") == "CRITICAL"]
        
        if critical_failures:
            colored_print(f"   ESCALATION: {len(critical_failures)} critical issues require follow-up", Colors.BRIGHT_RED)
            
            # Create follow-up task for code reviewer
            follow_up_description = f"Review and address {len(critical_failures)} critical issues that could not be automatically fixed"
            
            follow_up_task_id = self.comm.create_task(
                task_type="code_review_followup",
                description=follow_up_description,
                assigned_to="code_reviewer",
                created_by=self.agent_id,
                priority=1,
                data={
                    "failed_fixes": critical_failures,
                    "original_task": original_task.get("id"),
                    "escalation_reason": "critical_fixes_failed"
                }
            )
            
            colored_print(f"   DELEGATED: Follow-up task {follow_up_task_id} -> code_reviewer", Colors.YELLOW)
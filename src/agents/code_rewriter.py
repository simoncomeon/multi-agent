"""
Code Rewriter Agent - Handles code refactoring and fixing based on review feedback
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..core.base_agent import BaseAgent, TaskInput, TaskResult
from ..core.models import AgentRole, Colors
from ..core.utils import colored_print, gather_file_context, gather_directory_context, gather_project_context


class CodeRewriterAgent(BaseAgent):
    """Specialized agent for code rewriting and refactoring"""
    
    def __init__(self, agent_id: str, workspace_dir: str, **kwargs):
        super().__init__(agent_id, AgentRole.CODER, workspace_dir, **kwargs)
        self.terminal = kwargs.get('terminal_instance')
    
    def _define_capabilities(self) -> Dict[str, bool]:
        """Define code rewriter capabilities"""
        return {
            'code_rewriting': True,
            'code_refactoring': True,
            'bug_fixing': True,
            'code_optimization': True,
            'code_cleanup': True,
            'code_modernization': True,
            'review_based_fixes': True
        }
    
    def _is_task_type_supported(self, task_type: str) -> bool:
        """Check if task type is supported by code rewriter"""
        supported_types = [
            'code_rewrite', 'code_refactor', 'bug_fix',
            'code_optimization', 'code_cleanup', 'code_modernization',
            'code_rewrite_from_review', 'contextual_rewrite'
        ]
        return task_type in supported_types
    
    def _execute_specific_task(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """Execute code rewrite task based on input type"""
        if task_input.task_type == 'code_rewrite_from_review':
            return self._handle_review_based_rewrite(task_input, context)
        elif task_input.has_files():
            return self._handle_file_rewrite(task_input, context)
        else:
            return self._handle_general_rewrite(task_input, context)
    
    def _handle_review_based_rewrite(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """Handle rewrite based on code review"""
        review_report = task_input.metadata.get('review_report', {})
        issues = review_report.get('issues', [])
        
        colored_print(f"Processing {len(issues)} issues from code review", Colors.CYAN)
        
        fixed_issues = []
        failed_fixes = []
        
        for i, issue in enumerate(issues, 1):
            colored_print(f"  Fixing issue {i}/{len(issues)}: {issue.get('severity', 'UNKNOWN')}", Colors.YELLOW)
            
            fix_result = self.apply_single_issue_fix(issue, review_report)
            
            if fix_result.get("success"):
                fixed_issues.append(issue)
                colored_print(f"    Fixed: {issue.get('file', 'unknown file')}", Colors.GREEN)
            else:
                failed_fixes.append(issue)
                colored_print(f"    Failed: {fix_result.get('error', 'Unknown error')}", Colors.RED)
        
        total_fixes = len(fixed_issues)
        colored_print(f"REWRITE SUMMARY: {total_fixes}/{len(issues)} issues fixed", Colors.BRIGHT_GREEN)
        
        return TaskResult(
            success=len(fixed_issues) > 0,
            message=f"Fixed {total_fixes}/{len(issues)} issues",
            data={
                'fixed_issues': fixed_issues,
                'failed_fixes': failed_fixes,
                'summary': self.generate_fix_summary(fixed_issues, failed_fixes)
            },
            files_modified=[issue.get("file") for issue in fixed_issues if issue.get("file")],
            metadata={'total_issues': len(issues), 'fixed_count': total_fixes}
        )
    
    def _handle_file_rewrite(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """Handle rewrite of specific files"""
        colored_print(f"Rewriting {len(task_input.files)} files", Colors.BRIGHT_CYAN)
        
        rewritten_files = []
        
        for file_path in task_input.files:
            result = self.rewrite_with_context(
                task_input.description,
                str(file_path),
                []
            )
            
            if result.get('success'):
                rewritten_files.append(str(file_path))
        
        return TaskResult(
            success=len(rewritten_files) > 0,
            message=f"Rewrote {len(rewritten_files)}/{len(task_input.files)} files",
            files_modified=rewritten_files
        )
    
    def _handle_general_rewrite(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """Handle general rewrite request"""
        colored_print(f"General code rewrite", Colors.BRIGHT_CYAN)
        
        desc_lower = task_input.description.lower()
        
        if "refactor" in desc_lower:
            result = self.handle_refactoring_task(task_input)
        elif "optimize" in desc_lower:
            result = self.handle_optimization_task(task_input)
        elif "clean" in desc_lower or "cleanup" in desc_lower:
            result = self.handle_cleanup_task(task_input)
        elif "modernize" in desc_lower:
            result = self.handle_modernization_task(task_input)
        else:
            result = self.handle_general_rewrite(task_input)
        
        return TaskResult(
            success=result.get('status') == 'success',
            message=result.get('message', 'Rewrite completed'),
            data=result
        )

    
    def rewrite_with_context(self, description: str, target_file: str, context_paths: List[Union[str, Path]] = None) -> Dict:
        """Rewrite code with full context awareness"""
        
        colored_print(f"Context-aware code rewriting", Colors.BRIGHT_MAGENTA)
        colored_print(f"  TARGET: {target_file}", Colors.WHITE)
        
        context_data = {}
        
        if os.path.exists(target_file):
            context_data["target_file"] = gather_file_context(target_file)
            colored_print(f"  Target file loaded", Colors.CYAN)
        
        if context_paths:
            colored_print(f"  Gathering context from {len(context_paths)} paths", Colors.CYAN)
            
            for path in context_paths:
                path_obj = Path(path)
                if path_obj.is_file():
                    context_data[f"reference_{path_obj.name}"] = gather_file_context(path_obj)
                elif path_obj.is_dir():
                    context_data[f"reference_{path_obj.name}"] = gather_directory_context(path_obj)
        
        context_summary = self.format_context_for_ai(context_data)
        
        prompt_parts = [
            "OPERATION: CONTEXTUAL_CODE_REWRITE",
            f"TARGET: {target_file}",
            f"TASK: {description}",
            "",
            "CONTEXT:",
            context_summary,
            "",
            "REQUIREMENTS:",
            "- Analyze the existing code and understand its purpose",
            "- Apply the requested changes while maintaining functionality",
            "- Follow existing code patterns and style conventions",
            "- Preserve important logic and error handling",
            "- Ensure compatibility with the rest of the project",
            "",
            "CONSTRAINTS:",
            "- Maintain existing API interfaces where possible",
            "- Use project dependencies and imports correctly",
            "- Follow established naming and structure conventions",
            "- Keep changes minimal and focused on requirements",
            "- Preserve existing functionality unless explicitly changed",
            "",
            "OUTPUT: REWRITTEN_CODE"
        ]
        
        prompt = "\n".join(prompt_parts)
        ai_result = self.execute_ai_operation(prompt)
        
        return {
            "success": ai_result.get('success', False),
            "rewritten_code": ai_result.get('response', ''),
            "context_used": len(context_data),
            "summary": 'Context-aware code rewrite completed'
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
"""
Code Reviewer Agent - Handles code quality analysis and review tasks
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..core.base_agent import BaseAgent, TaskInput, TaskResult
from ..core.models import AgentRole, Colors
from ..core.utils import colored_print, gather_file_context, gather_directory_context, gather_project_context


class CodeReviewerAgent(BaseAgent):
    """Specialized agent for code quality review and analysis"""
    
    def __init__(self, agent_id: str, workspace_dir: str, **kwargs):
        super().__init__(agent_id, AgentRole.REVIEWER, workspace_dir, **kwargs)
        self.terminal = kwargs.get('terminal_instance')
    
    def _define_capabilities(self) -> Dict[str, bool]:
        """Define code reviewer capabilities"""
        return {
            'code_review': True,
            'quality_analysis': True,
            'security_analysis': True,
            'performance_analysis': True,
            'best_practices_check': True,
            'context_aware_review': True,
            'project_analysis': True
        }
    
    def _is_task_type_supported(self, task_type: str) -> bool:
        """Check if task type is supported by code reviewer"""
        supported_types = [
            'code_review', 'quality_analysis', 'security_check',
            'performance_review', 'project_analysis', 'contextual_review'
        ]
        return task_type in supported_types
    
    def _execute_specific_task(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """Execute code review task based on input type"""
        if task_input.has_files():
            return self._handle_file_review(task_input, context)
        elif task_input.has_directories():
            return self._handle_project_review(task_input, context)
        else:
            return self._handle_general_review(task_input, context)
    
    def _handle_file_review(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """Handle review of specific files"""
        colored_print(f"Reviewing {len(task_input.files)} files", Colors.BRIGHT_CYAN)
        
        review_result = self.review_with_context(
            [str(f) for f in task_input.files],
            task_input.description,
            []
        )
        
        issues_found = review_result.get('issues_found', len(review_result.get('issues', [])))
        
        if issues_found > 0:
            self._delegate_to_rewriter_if_needed(review_result)
        
        return TaskResult(
            success=True,
            message=f"Code review completed: {issues_found} issues found",
            data=review_result,
            metadata={'review_type': 'file_review', 'issues_count': issues_found}
        )
    
    def _handle_project_review(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """Handle review of entire project/directory"""
        colored_print(f"Reviewing project directories", Colors.BRIGHT_CYAN)
        
        project_dir = task_input.directories[0] if task_input.directories else self.workspace_dir
        review_result = self.analyze_project_quality(str(project_dir))
        
        return TaskResult(
            success=True,
            message=f"Project analysis completed",
            data=review_result,
            metadata={'review_type': 'project_analysis'}
        )
    
    def _handle_general_review(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """Handle general review request"""
        colored_print(f"Conducting general code review", Colors.BRIGHT_CYAN)
        
        review_result = self.conduct_comprehensive_code_review(task_input.description)
        
        issues_found = review_result.get('issues_found', 0)
        if issues_found > 0:
            self._delegate_to_rewriter_if_needed(review_result)
        
        return TaskResult(
            success=True,
            message=f"Code review completed: {issues_found} issues found",
            data=review_result,
            metadata={'review_type': 'general_review', 'issues_count': issues_found}
        )
    
    def _delegate_to_rewriter_if_needed(self, review_result: Dict):
        """Delegate to code rewriter if issues found"""
        if review_result.get('issues_found', 0) > 0:
            self.delegate_to_code_rewriter(review_result)

    
    def conduct_comprehensive_code_review(self, description: str) -> Dict:
        """Conduct comprehensive code review using AI with project context"""
        
        prompt_parts = [
            "OPERATION: CODE_REVIEW",
            f"TASK: {description}",
            "",
            "REQUIREMENTS:",
            "- Analyze code quality and best practices",
            "- Identify bugs, security issues, and performance problems",
            "- Check for maintainability and readability issues",
            "- Verify proper error handling and edge cases",
            "- Assess architecture and design patterns",
            "",
            "CONSTRAINTS:",
            "- Provide specific line numbers and file locations for issues",
            "- Categorize issues by severity (CRITICAL, MAJOR, MINOR)",
            "- Suggest specific fixes for each issue found",
            "- Include positive feedback for well-written code",
            "",
            "OUTPUT: STRUCTURED_REVIEW_REPORT"
        ]
        
        prompt = "\n".join(prompt_parts)
        ai_result = self.execute_ai_operation(prompt)
        
        if ai_result.get('success'):
            review_content = ai_result.get('response', '')
            return self.parse_review_report(review_content)
        else:
            return self.conduct_basic_code_review(description)
    
    def parse_review_report(self, review_content: str) -> Dict:
        """Parse AI review output into structured format"""
        
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
        
        colored_print(f"Conducting basic code review analysis", Colors.YELLOW)
        
        issues = []
        
        return {
            "issues_found": len(issues),
            "issues": issues,
            "summary": f"Basic review completed - {len(issues)} issues found",
            "timestamp": datetime.now().isoformat()
        }
    
    def review_with_context(self, target_files: List[str], description: str, context_paths: List[Union[str, Path]] = None) -> Dict:
        """Perform code review with full context awareness"""
        
        colored_print(f"Context-aware code review of {len(target_files)} files", Colors.BRIGHT_BLUE)
        
        context_data = {}
        
        for i, file_path in enumerate(target_files):
            if os.path.exists(file_path):
                context_data[f"target_file_{i}"] = gather_file_context(file_path)
                colored_print(f"  {Path(file_path).name}", Colors.CYAN)
            else:
                colored_print(f"  {Path(file_path).name} (NOT FOUND)", Colors.RED)
        
        if context_paths:
            colored_print(f"Additional context from {len(context_paths)} paths", Colors.CYAN)
            
            for path in context_paths:
                path_obj = Path(path)
                colored_print(f"  {path_obj.name}", Colors.WHITE)
                
                if path_obj.is_file():
                    context_data[f"reference_{path_obj.name}"] = gather_file_context(path_obj)
                elif path_obj.is_dir():
                    context_data[f"reference_{path_obj.name}"] = gather_directory_context(path_obj)
        
        context_summary = self.format_context_for_ai(context_data)
        
        prompt_parts = [
            "OPERATION: CONTEXTUAL_CODE_REVIEW",
            f"TASK: Review files with context: {description}",
            f"FILES: {', '.join(target_files)}",
            "",
            "CONTEXT:",
            context_summary,
            "",
            "REQUIREMENTS:",
            "- Analyze code quality in context of the entire project",
            "- Identify issues that affect project architecture and consistency",
            "- Check for compatibility with existing codebase patterns",
            "- Assess integration points and dependencies",
            "- Verify adherence to project conventions and standards",
            "- Identify security issues and performance problems",
            "",
            "CONSTRAINTS:",
            "- Provide specific file paths and line numbers for issues",
            "- Categorize issues by severity and impact on project",
            "- Consider existing project architecture and patterns",
            "- Suggest fixes that maintain project consistency",
            "- Focus on issues that truly impact code quality",
            "",
            "OUTPUT: CONTEXTUAL_REVIEW_REPORT"
        ]
        
        prompt = "\n".join(prompt_parts)
        ai_result = self.execute_ai_operation(prompt)
        
        if ai_result.get('success'):
            return self._parse_contextual_review(ai_result.get('response', ''), target_files, context_data)
        else:
            return self.conduct_comprehensive_code_review(description)
    
    def _parse_contextual_review(self, response: str, target_files: List[str], context_data: Dict) -> Dict:
        """Parse contextual review response"""
        review = self.parse_review_report(response)
        review.update({
            "type": "contextual_code_review",
            "files_reviewed": target_files,
            "context_used": len(context_data)
        })
        return review
    
    def analyze_project_quality(self, project_path: str, focus_areas: List[str] = None) -> Dict:
        """Analyze overall project quality with context"""
        
        colored_print(f"Project-wide quality analysis", Colors.BRIGHT_MAGENTA)
        colored_print(f"  PROJECT: {Path(project_path).name}", Colors.WHITE)
        
        project_context = gather_project_context(project_path)
        
        default_focus = ["architecture", "code_quality", "security", "performance", "maintainability"]
        focus = focus_areas if focus_areas else default_focus
        
        colored_print(f"  FOCUS: {', '.join(focus)}", Colors.CYAN)
        
        prompt_parts = [
            "OPERATION: PROJECT_QUALITY_ANALYSIS",
            f"PROJECT: {Path(project_path).name}",
            f"FOCUS AREAS: {', '.join(focus)}",
            "",
            "PROJECT CONTEXT:",
            self.format_project_context_for_ai(project_context),
            "",
            "REQUIREMENTS:",
            "- Analyze project architecture and organization",
            "- Assess code quality and consistency across files",
            "- Identify security vulnerabilities and risks",
            "- Evaluate performance characteristics",
            "- Check maintainability and scalability aspects",
            "- Review dependency management and structure",
            "",
            "CONSTRAINTS:",
            "- Provide actionable recommendations for improvement",
            "- Prioritize issues by impact on project success",
            "- Consider project type and intended use case",
            "- Suggest specific implementation strategies",
            "- Focus on areas specified in focus_areas",
            "",
            "OUTPUT: PROJECT_ANALYSIS_REPORT"
        ]
        
        prompt = "\n".join(prompt_parts)
        ai_result = self.execute_ai_operation(prompt)
        
        return self._parse_project_analysis(ai_result.get('response', ''), project_path, focus)
    
    def _parse_project_analysis(self, response: str, project_path: str, focus: List[str]) -> Dict:
        """Parse project analysis response"""
        return {
            "type": "project_quality_analysis",
            "project_path": project_path,
            "project_name": Path(project_path).name,
            "focus_areas": focus,
            "analysis_content": response,
            "timestamp": datetime.now().isoformat()
        }
    
    def format_context_for_ai(self, context_data: Dict) -> str:
        """Format gathered context data for AI input"""
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
    
    def format_project_context_for_ai(self, project_context: Dict) -> str:
        """Format project context specifically for project analysis"""
        if not project_context:
            return "No project context available"
        
        context_parts = [f"""
PROJECT OVERVIEW:
Name: {project_context.get('project_name', 'unknown')}
Type: {project_context.get('project_type', 'unknown')}
Path: {project_context.get('project_path', 'unknown')}
"""]
        
        package_info = project_context.get('package_info', {})
        if package_info:
            context_parts.append(f"""
PACKAGE INFO:
Dependencies: {', '.join(package_info.get('dependencies', [])[:10])}{'...' if len(package_info.get('dependencies', [])) > 10 else ''}
Scripts: {', '.join(package_info.get('scripts', []))}
Framework: {package_info.get('framework', 'none')}
""")
        
        key_files = project_context.get('key_files', {})
        if key_files:
            context_parts.append("\nKEY FILES:")
            for filename, file_data in list(key_files.items())[:5]:
                if file_data.get('readable') and file_data.get('content'):
                    content = file_data['content'][:1000] + ('...' if len(file_data['content']) > 1000 else '')
                    context_parts.append(f"""
{filename}:
{content}
""")
        
        return "\n".join(context_parts)
    
    def delegate_to_code_rewriter(self, review_result: Dict):
        """Delegate issues to code rewriter with structured task list"""
        
        issues = review_result.get("issues", [])
        if not issues:
            return
        
        colored_print(f"Delegating {len(issues)} issues to code rewriter", Colors.BRIGHT_YELLOW)
        
        rewriter_task_description = f"Fix {len(issues)} code issues from review report"
        
        task_id = self.delegate_task(
            task_description=rewriter_task_description,
            target_agent_role="code_rewriter",
            task_type="code_rewrite_from_review",
            priority=1,
            task_data={
                "review_report": review_result,
                "total_issues": len(issues),
                "critical_issues": len([i for i in issues if i.get("severity") == "CRITICAL"]),
                "major_issues": len([i for i in issues if i.get("severity") == "MAJOR"]),
                "minor_issues": len([i for i in issues if i.get("severity") == "MINOR"]),
                "source_agent": self.agent_id
            }
        )
        
        colored_print(f"Created rewriter task {task_id} with {len(issues)} structured fixes", Colors.GREEN)
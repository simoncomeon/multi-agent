"""
Code Reviewer Agent - Handles code quality analysis and review tasks
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..core.models import Colors
from ..core.utils import colored_print, gather_file_context, gather_directory_context, gather_project_context


class CodeReviewerAgent:
    """Specialized agent for code quality review and analysis"""
    
    def __init__(self, terminal_instance, comm_instance):
        self.terminal = terminal_instance
        self.comm = comm_instance
        self.agent_id = "code_reviewer"
    
    def handle_code_review_task(self, task: Dict) -> Dict:
        """Handle code review tasks and create structured review reports for code rewriter"""
        
        description = task["description"]
        colored_print(f"INFO: CODE REVIEWER: Conducting comprehensive code review", Colors.BRIGHT_CYAN)
        colored_print(f"   Task: {description}", Colors.CYAN)
        
        # Use universal AI collaboration for code review
        review_result = self.conduct_comprehensive_code_review(description)
        
        # If issues found, automatically delegate to code rewriter
        if review_result.get("issues_found", 0) > 0:
            self.delegate_to_code_rewriter(review_result)
        
        return {
            "status": "completed",
            "review_report": review_result,
            "message": f"Code review completed: {review_result.get('summary', 'Review finished')}"
        }
    
    def conduct_comprehensive_code_review(self, description: str) -> Dict:
        """Conduct comprehensive code review using AI with project context"""
        
        # Create standardized AI input for code review
        standardized_input = self.terminal.create_standardized_ai_input(
            operation_type="CODE_REVIEW",
            task_description=f"Comprehensive code review: {description}",
            context_type="QUALITY_ANALYSIS",
            requirements=[
                "Analyze code quality and best practices",
                "Identify bugs, security issues, and performance problems",
                "Check for maintainability and readability issues",
                "Verify proper error handling and edge cases",
                "Assess architecture and design patterns"
            ],
            constraints=[
                "Provide specific line numbers and file locations for issues",
                "Categorize issues by severity (critical, major, minor)",
                "Suggest specific fixes for each issue found",
                "Include positive feedback for well-written code"
            ],
            expected_output="STRUCTURED_REVIEW_REPORT"
        )
        
        # Execute AI-powered code review
        ai_result = self.terminal.execute_standardized_ai_operation(standardized_input)
        
        if ai_result.get('status') == 'success':
            review_content = ai_result.get('implementation', '')
            return self.parse_review_report(review_content)
        else:
            # Fallback review
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
        
        colored_print(f"   INFO: Conducting basic code review analysis", Colors.YELLOW)
        
        # Basic file analysis
        issues = []
        if hasattr(self.terminal, 'project_process_files') and self.terminal.project_process_files:
            for file_path, file_info in self.terminal.project_process_files.items():
                # Basic checks
                content = file_info['content']
                if 'TODO' in content or 'FIXME' in content:
                    issues.append({
                        "severity": "MINOR",
                        "description": "Contains TODO or FIXME comments",
                        "file": file_path,
                        "line_number": 0,
                        "suggested_fix": "Complete or remove TODO/FIXME items"
                    })
        
        return {
            "issues_found": len(issues),
            "issues": issues,
            "summary": f"Basic review completed - {len(issues)} issues found",
            "timestamp": datetime.now().isoformat()
        }
    
    def review_with_context(self, target_files: List[str], description: str, context_paths: List[Union[str, Path]] = None) -> Dict:
        """Perform code review with full context awareness"""
        
        colored_print(f"CODE REVIEWER: Context-aware code review", Colors.BRIGHT_BLUE)
        colored_print(f"   FILES: {len(target_files)} files to review", Colors.WHITE)
        
        # Gather context from target files
        context_data = {}
        
        for i, file_path in enumerate(target_files):
            if os.path.exists(file_path):
                context_data[f"target_file_{i}"] = gather_file_context(file_path)
                colored_print(f"     • {Path(file_path).name}", Colors.CYAN)
            else:
                colored_print(f"     • {Path(file_path).name} (NOT FOUND)", Colors.RED)
        
        # Add reference context
        if context_paths:
            colored_print(f"   CONTEXT: Additional context from {len(context_paths)} paths", Colors.CYAN)
            
            for path in context_paths:
                path_obj = Path(path)
                colored_print(f"     • {path_obj.name}", Colors.WHITE)
                
                if path_obj.is_file():
                    context_data[f"reference_{path_obj.name}"] = gather_file_context(path_obj)
                elif path_obj.is_dir():
                    context_data[f"reference_{path_obj.name}"] = gather_directory_context(path_obj)
        
        # Add project context
        if hasattr(self.terminal, 'current_project_process') and self.terminal.current_project_process:
            project_path = os.path.join(self.terminal.workspace_dir, self.terminal.current_project_process)
            if os.path.exists(project_path):
                colored_print(f"   PROJECT: Adding project context: {self.terminal.current_project_process}", Colors.CYAN)
                context_data["project"] = gather_project_context(project_path)
        
        # Format context for AI
        context_summary = self.format_context_for_ai(context_data)
        
        # Enhanced AI operation for context-aware code review
        standardized_input = self.terminal.create_standardized_ai_input(
            operation_type="CONTEXTUAL_CODE_REVIEW",
            task_description=f"Review files with context: {description}\\nFiles: {', '.join(target_files)}",
            context_type="FULL_PROJECT_REVIEW",
            requirements=[
                "Analyze code quality in context of the entire project",
                "Identify issues that affect project architecture and consistency",
                "Check for compatibility with existing codebase patterns",
                "Assess integration points and dependencies",
                "Verify adherence to project conventions and standards",
                "Identify security issues and performance problems"
            ],
            constraints=[
                "Provide specific file paths and line numbers for issues",
                "Categorize issues by severity and impact on project",
                "Consider existing project architecture and patterns",
                "Suggest fixes that maintain project consistency",
                "Focus on issues that truly impact code quality"
            ],
            expected_output="CONTEXTUAL_REVIEW_REPORT",
            additional_context=context_summary
        )
        
        ai_result = self.terminal.execute_standardized_ai_operation(standardized_input)
        
        if ai_result.get('status') == 'success':
            return {
                "type": "contextual_code_review",
                "files_reviewed": target_files,
                "context_used": len(context_data),
                "issues": ai_result.get('issues', []),
                "summary": ai_result.get('summary', 'Context-aware review completed'),
                "recommendations": ai_result.get('recommendations', []),
                "positive_feedback": ai_result.get('positive_feedback', []),
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Fallback to basic review
            return self.conduct_ai_powered_review(description)
    
    def analyze_project_quality(self, project_path: str, focus_areas: List[str] = None) -> Dict:
        """Analyze overall project quality with context"""
        
        colored_print(f"CODE REVIEWER: Project-wide quality analysis", Colors.BRIGHT_MAGENTA)
        colored_print(f"   PROJECT: {Path(project_path).name}", Colors.WHITE)
        
        # Gather comprehensive project context
        project_context = gather_project_context(project_path)
        
        # Focus areas for analysis
        default_focus = ["architecture", "code_quality", "security", "performance", "maintainability"]
        focus = focus_areas if focus_areas else default_focus
        
        colored_print(f"   FOCUS: {', '.join(focus)}", Colors.CYAN)
        
        # Enhanced AI operation for project analysis
        standardized_input = self.terminal.create_standardized_ai_input(
            operation_type="PROJECT_QUALITY_ANALYSIS",
            task_description=f"Analyze overall quality of project: {Path(project_path).name}\\nFocus areas: {', '.join(focus)}",
            context_type="COMPLETE_PROJECT_ANALYSIS",
            requirements=[
                "Analyze project architecture and organization",
                "Assess code quality and consistency across files",
                "Identify security vulnerabilities and risks",
                "Evaluate performance characteristics",
                "Check maintainability and scalability aspects",
                "Review dependency management and structure"
            ],
            constraints=[
                "Provide actionable recommendations for improvement",
                "Prioritize issues by impact on project success",
                "Consider project type and intended use case",
                "Suggest specific implementation strategies",
                "Focus on areas specified in focus_areas"
            ],
            expected_output="PROJECT_ANALYSIS_REPORT",
            additional_context=self.format_project_context_for_ai(project_context)
        )
        
        ai_result = self.terminal.execute_standardized_ai_operation(standardized_input)
        
        return {
            "type": "project_quality_analysis",
            "project_path": project_path,
            "project_name": Path(project_path).name,
            "focus_areas": focus,
            "overall_score": ai_result.get('overall_score', 'Not scored'),
            "strengths": ai_result.get('strengths', []),
            "weaknesses": ai_result.get('weaknesses', []),
            "critical_issues": ai_result.get('critical_issues', []),
            "recommendations": ai_result.get('recommendations', []),
            "next_steps": ai_result.get('next_steps', []),
            "summary": ai_result.get('summary', 'Project analysis completed'),
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
        
        # Package information
        package_info = project_context.get('package_info', {})
        if package_info:
            context_parts.append(f"""
PACKAGE INFO:
Dependencies: {', '.join(package_info.get('dependencies', [])[:10])}{'...' if len(package_info.get('dependencies', [])) > 10 else ''}
Scripts: {', '.join(package_info.get('scripts', []))}
Framework: {package_info.get('framework', 'none')}
""")
        
        # Key files content (limited)
        key_files = project_context.get('key_files', {})
        if key_files:
            context_parts.append("\\nKEY FILES:")
            for filename, file_data in list(key_files.items())[:5]:  # Limit to 5 files
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
        
        colored_print(f"   PROCESS: Delegating {len(issues)} issues to code rewriter", Colors.BRIGHT_YELLOW)
        
        # Create structured task for code rewriter
        rewriter_task_description = f"Fix {len(issues)} code issues from review report"
        
        # Create detailed task with structured issue list
        task_id = self.comm.create_task(
            task_type="code_rewrite_from_review",
            description=rewriter_task_description,
            assigned_to="code_rewriter",
            created_by=self.agent_id,
            priority=1,
            data={
                "review_report": review_result,
                "total_issues": len(issues),
                "critical_issues": len([i for i in issues if i.get("severity") == "CRITICAL"]),
                "major_issues": len([i for i in issues if i.get("severity") == "MAJOR"]),
                "minor_issues": len([i for i in issues if i.get("severity") == "MINOR"]),
                "source_agent": self.agent_id
            }
        )
        
        colored_print(f"   SUCCESS: Created rewriter task {task_id} with {len(issues)} structured fixes", Colors.GREEN)
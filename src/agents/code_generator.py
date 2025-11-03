"""
Code Generator Agent - Handles code generation and implementation tasks
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..core.models import Colors
from ..core.utils import colored_print, gather_file_context, gather_directory_context, gather_project_context


class CodeGeneratorAgent:
    """Specialized agent for code generation and implementation"""
    
    def __init__(self, terminal_instance, comm_instance):
        self.terminal = terminal_instance
        self.comm = comm_instance
        self.agent_id = "code_generator"
    
    def handle_code_generation_task(self, task: Dict) -> Dict:
        """Handle code generation and file creation/editing"""
        description = task["description"]
        
        colored_print(f"CODE GENERATOR: Processing code generation task", Colors.BRIGHT_CYAN)
        colored_print(f"   Task: {description}", Colors.CYAN)
        
        # Check if this involves file creation or editing
        if self.requires_file_operations(description):
            return self.handle_file_based_code_generation(task)
        else:
            return self.handle_analysis_and_guidance(task)
    
    def requires_file_operations(self, description: str) -> bool:
        """Check if task requires actual file creation or editing"""
        file_keywords = [
            "create file", "write file", "generate file", "implement in",
            "add to file", "modify file", "edit file", "create component",
            "implement function", "add class", "write code for", "build", 
            "develop", "make", "generate", "create", "code"
        ]
        desc_lower = description.lower()
        
        # Also check for component/app creation patterns
        creation_patterns = [
            "create a", "build a", "make a", "develop a", "generate a",
            "todo", "component", "app", "application", "widget", "module"
        ]
        
        has_file_keywords = any(keyword in desc_lower for keyword in file_keywords)
        has_creation_patterns = any(pattern in desc_lower for pattern in creation_patterns)
        
        return has_file_keywords or has_creation_patterns
    
    def handle_file_based_code_generation(self, task: Dict) -> Dict:
        """Handle code generation that involves creating or editing files"""
        description = task["description"]
        
        # Delegate to file manager for actual file operations
        file_task_id = self.comm.create_task(
            task_type="file_management",
            description=f"File operations for code generation: {description}",
            assigned_to="file_manager",
            created_by=self.agent_id,
            priority=task.get("priority", 1),
            data={
                "generation_task": True,
                "original_description": description,
                "code_requirements": self.extract_code_requirements(description)
            }
        )
        
        colored_print(f"   DELEGATED: File operations task {file_task_id} -> file_manager", Colors.GREEN)
        
        # Also provide guidance for the implementation
        guidance = self.analyze_task_and_provide_guidance(description)
        
        colored_print(f"\\n=== CODE GENERATION GUIDANCE ===", Colors.BRIGHT_YELLOW)
        colored_print(guidance, Colors.WHITE)
        colored_print(f"================================\\n", Colors.BRIGHT_YELLOW)
        
        return {
            "type": "code_generation_with_files",
            "delegated_task_id": file_task_id,
            "guidance": guidance,
            "file_operations": "delegated_to_file_manager",
            "message": f"Code generation task delegated to file manager. Task ID: {file_task_id}"
        }
    
    def handle_analysis_and_guidance(self, task: Dict) -> Dict:
        """Handle code generation analysis without file operations"""
        description = task["description"]
        
        # Provide intelligent guidance
        guidance = self.analyze_task_and_provide_guidance(description)
        
        colored_print(f"\\n=== COLLABORATIVE ANALYSIS ===", Colors.BRIGHT_CYAN)
        colored_print(guidance, Colors.CYAN)
        colored_print(f"================================\\n", Colors.BRIGHT_CYAN)
        
        # Try AI model if available for actual implementation
        ai_result = self.try_ai_implementation(description)
        
        return {
            "type": "collaborative_guidance",
            "guidance": guidance,
            "ai_implementation": ai_result,
            "approach": "collaborative",
            "message": "This task requires AI model collaboration for implementation. The guidance above provides architectural direction."
        }
    
    def extract_code_requirements(self, description: str) -> Dict:
        """Extract code requirements for file manager"""
        desc_lower = description.lower()
        
        requirements = {
            "language": "javascript",  # default
            "file_type": "component",
            "framework": None,
            "features": [],
            "structure": "single_file"
        }
        
        # Language detection
        if "python" in desc_lower:
            requirements["language"] = "python"
        elif "typescript" in desc_lower:
            requirements["language"] = "typescript"
        elif "react" in desc_lower:
            requirements["language"] = "javascript"
            requirements["framework"] = "react"
        elif "vue" in desc_lower:
            requirements["language"] = "javascript"
            requirements["framework"] = "vue"
        
        # Feature extraction
        if "todo" in desc_lower or "task" in desc_lower:
            requirements["features"] = ["add_item", "remove_item", "toggle_complete", "persistence"]
        elif "time" in desc_lower or "clock" in desc_lower:
            requirements["features"] = ["real_time_display", "formatting", "timezone_support"]
        elif "counter" in desc_lower:
            requirements["features"] = ["increment", "decrement", "reset", "state_management"]
        
        return requirements
    
    def analyze_task_with_context(self, description: str, context_paths: List[Union[str, Path]] = None) -> str:
        """Analyze task with file/directory context for better AI responses"""
        
        # Gather context from specified paths
        context_data = {}
        if context_paths:
            colored_print(f"   CONTEXT: Gathering context from {len(context_paths)} paths", Colors.CYAN)
            
            for path in context_paths:
                path_obj = Path(path)
                colored_print(f"     • {path_obj.name}", Colors.WHITE)
                
                if path_obj.is_file():
                    context_data[f"file_{path_obj.name}"] = gather_file_context(path_obj)
                elif path_obj.is_dir():
                    context_data[f"dir_{path_obj.name}"] = gather_directory_context(path_obj)
        
        # Also gather current project context if available
        if hasattr(self.terminal, 'current_project_process') and self.terminal.current_project_process:
            project_path = os.path.join(self.terminal.workspace_dir, self.terminal.current_project_process)
            if os.path.exists(project_path):
                colored_print(f"   PROJECT: Adding current project context: {self.terminal.current_project_process}", Colors.CYAN)
                context_data["current_project"] = gather_project_context(project_path)
        
        # Create enhanced AI input with context
        context_summary = self.format_context_for_ai(context_data)
        
        standardized_input = self.terminal.create_standardized_ai_input(
            operation_type="CODE_GENERATION_ANALYSIS",
            task_description=description,
            context_type="PROJECT_AWARE_GENERATION",
            requirements=[
                "Analyze the task in context of the existing codebase",
                "Provide specific, actionable recommendations",
                "Consider existing patterns and architecture", 
                "Suggest file locations and naming conventions",
                "Identify dependencies and imports needed"
            ],
            constraints=[
                "Match existing code style and patterns",
                "Follow project conventions and structure",
                "Consider existing dependencies and tools",
                "Maintain consistency with current architecture"
            ],
            expected_output="CONTEXTUAL_ANALYSIS",
            additional_context=context_summary
        )
        
        ai_result = self.terminal.execute_standardized_ai_operation(standardized_input)
        
        if ai_result.get('status') == 'success':
            return ai_result.get('analysis', 'Context-aware analysis completed')
        else:
            # Fallback to basic analysis
            return self.analyze_task_and_provide_guidance(description)
    
    def format_context_for_ai(self, context_data: Dict) -> str:
        """Format gathered context data for AI input"""
        if not context_data:
            return "No additional context provided"
        
        context_parts = []
        
        for key, data in context_data.items():
            if "error" in data:
                context_parts.append(f"{key}: {data['error']}")
                continue
            
            if key.startswith("file_"):
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
            
            elif key == "current_project":
                context_parts.append(f"""
PROJECT: {data['project_name']} ({data.get('project_type', 'unknown')})
Location: {data['project_path']}
Key files: {', '.join(data.get('key_files', {}).keys())}
Package info: {data.get('package_info', {})}
""")
        
        return "\n".join(context_parts)
    
    def generate_code_with_context(self, description: str, context_paths: List[Union[str, Path]] = None, target_file: str = None) -> Dict:
        """Generate code with full context awareness"""
        
        colored_print(f"   GENERATING: Context-aware code generation", Colors.BRIGHT_GREEN)
        
        # Gather context
        context_data = {}
        if context_paths:
            for path in context_paths:
                path_obj = Path(path)
                if path_obj.is_file():
                    context_data[f"reference_{path_obj.name}"] = gather_file_context(path_obj)
                elif path_obj.is_dir():
                    context_data[f"reference_{path_obj.name}"] = gather_directory_context(path_obj)
        
        # Add target file context if it exists
        if target_file and os.path.exists(target_file):
            context_data["target_file"] = gather_file_context(target_file)
        
        # Add current project context
        if hasattr(self.terminal, 'current_project_process') and self.terminal.current_project_process:
            project_path = os.path.join(self.terminal.workspace_dir, self.terminal.current_project_process)
            if os.path.exists(project_path):
                context_data["project"] = gather_project_context(project_path)
        
        context_summary = self.format_context_for_ai(context_data)
        
        # Enhanced AI operation for code generation
        standardized_input = self.terminal.create_standardized_ai_input(
            operation_type="CONTEXTUAL_CODE_GENERATION",
            task_description=f"Generate code for: {description}" + (f" in file: {target_file}" if target_file else ""),
            context_type="FULL_PROJECT_CONTEXT",
            requirements=[
                "Generate functional, ready-to-use code",
                "Match existing code patterns and style",
                "Include proper imports and dependencies",
                "Follow project conventions and structure",
                "Add appropriate error handling and validation"
            ],
            constraints=[
                "Use existing project dependencies where possible",
                "Follow established naming conventions",
                "Maintain consistency with existing architecture",
                "Generate complete, working implementations"
            ],
            expected_output="GENERATED_CODE",
            additional_context=context_summary
        )
        
        ai_result = self.terminal.execute_standardized_ai_operation(standardized_input)
        
        return {
            "success": ai_result.get('status') == 'success',
            "generated_code": ai_result.get('generated_code', ''),
            "file_suggestions": ai_result.get('file_suggestions', []),
            "dependencies": ai_result.get('dependencies', []),
            "next_steps": ai_result.get('next_steps', []),
            "context_used": len(context_data),
            "summary": ai_result.get('summary', 'Context-aware code generation completed')
        }
    
    def analyze_task_and_provide_guidance(self, description: str) -> str:
        """Universal task analysis using AI collaboration with standardized input/output"""
        
        # Standardized AI Input
        standardized_input = self.terminal.create_standardized_ai_input(
            operation_type="TASK_ANALYSIS",
            task_description=description,
            context_type="PROJECT_ANALYSIS"
        )
        
        colored_print(f"   AGENT: Universal AI task analysis with standardized input", Colors.BRIGHT_CYAN)
        
        # Try AI analysis with standardized input
        ai_result = self.terminal.execute_standardized_ai_operation(standardized_input)
        
        if ai_result.get('status') == 'success':
            return self.process_standardized_ai_output(ai_result, "TASK_ANALYSIS")
        
        # Fallback to basic analysis if AI unavailable
        return self.provide_fallback_guidance(description)
    
    def provide_fallback_guidance(self, description: str) -> str:
        """Provide fallback guidance when AI is unavailable"""
        
        desc_lower = description.lower()
        analysis = {
            "framework": None,
            "component_type": None,
            "features": [],
            "suggested_approach": []
        }
        
        # Framework detection
        if "react" in desc_lower:
            analysis["framework"] = "React"
            analysis["suggested_approach"].append("Use functional components with hooks")
            analysis["suggested_approach"].append("Consider state management needs")
        elif "vue" in desc_lower:
            analysis["framework"] = "Vue"
            analysis["suggested_approach"].append("Use composition API for modern Vue development")
        elif "python" in desc_lower:
            analysis["framework"] = "Python"
            analysis["suggested_approach"].append("Follow PEP 8 style guidelines")
            analysis["suggested_approach"].append("Consider using type hints")
        elif "node" in desc_lower or "javascript" in desc_lower:
            analysis["framework"] = "Node.js/JavaScript"
            analysis["suggested_approach"].append("Use modern ES6+ features")
        
        # Component type detection
        if "time" in desc_lower or "clock" in desc_lower:
            analysis["component_type"] = "Time/Clock Display"
            analysis["features"] = ["real-time updates", "date formatting", "time formatting"]
            analysis["suggested_approach"].append("Implement timer with setInterval")
            analysis["suggested_approach"].append("Consider timezone handling")
        elif "todo" in desc_lower or "task" in desc_lower:
            analysis["component_type"] = "Task Management"
            analysis["features"] = ["add/remove items", "mark complete", "persistence"]
            analysis["suggested_approach"].append("Use local state or localStorage")
            analysis["suggested_approach"].append("Consider CRUD operations")
        elif "app" in desc_lower:
            analysis["component_type"] = "Application"
            analysis["features"] = ["user interface", "routing", "state management"]
            analysis["suggested_approach"].append("Plan component hierarchy")
            analysis["suggested_approach"].append("Consider data flow patterns")
        
        # Generate intelligent guidance
        guidance = f'''TASK ANALYSIS: {description}
{'=' * 60}

FRAMEWORK DETECTED: {analysis["framework"] or "Not specified - recommend clarifying"}
COMPONENT TYPE: {analysis["component_type"] or "Generic component"}
SUGGESTED FEATURES: {", ".join(analysis["features"]) if analysis["features"] else "Basic functionality"}

ARCHITECTURAL GUIDANCE:
{chr(10).join(f"• {approach}" for approach in analysis["suggested_approach"])}

IMPLEMENTATION STRATEGY:
This task requires collaborative development between AI model and human developer.

RECOMMENDED WORKFLOW:
1. AI Model: Generate initial implementation based on requirements
2. Human Developer: Review and customize for specific needs  
3. Collaborative Refinement: Iterate based on testing and feedback

TECHNICAL CONSIDERATIONS:
• Follow framework best practices and conventions
• Implement proper error handling and edge cases
• Consider accessibility and user experience
• Plan for testing and maintainability

NEXT STEPS:
• Activate AI model for implementation generation
• Review generated code for project-specific requirements
• Test implementation and iterate as needed'''
        
        return guidance
    
    def try_ai_implementation(self, description: str) -> Dict:
        """Try to generate actual implementation using AI model"""
        
        # Create standardized AI input for implementation
        standardized_input = self.terminal.create_standardized_ai_input(
            operation_type="CODE_GENERATION",
            task_description=description,
            context_type="IMPLEMENTATION",
            requirements=[
                "Generate complete, working code",
                "Follow best practices and conventions",
                "Include proper error handling",
                "Add comprehensive comments"
            ],
            constraints=[
                "Use modern language features",
                "Ensure code is maintainable",
                "Include proper imports/dependencies",
                "Follow project structure"
            ],
            expected_output="COMPLETE_IMPLEMENTATION"
        )
        
        # Execute AI operation
        ai_result = self.terminal.execute_standardized_ai_operation(standardized_input)
        
        if ai_result.get('status') == 'success':
            return {
                "status": "success",
                "implementation": ai_result.get('implementation', ''),
                "files_created": ai_result.get('files_created', []),
                "dependencies": ai_result.get('dependencies', []),
                "notes": ai_result.get('notes', '')
            }
        else:
            return {
                "status": "failed",
                "message": "AI model not available or implementation failed",
                "fallback": "Use the guidance above for manual implementation"
            }
    
    def process_standardized_ai_output(self, ai_result: Dict, operation_type: str) -> str:
        """Process standardized AI output into readable format"""
        
        if operation_type == "TASK_ANALYSIS":
            analysis_content = ai_result.get('analysis', ai_result.get('content', ''))
            return f'''AI-POWERED TASK ANALYSIS:
{'=' * 50}

{analysis_content}

CONFIDENCE: {ai_result.get('confidence', 'N/A')}
COMPLEXITY: {ai_result.get('complexity', 'N/A')}
ESTIMATED_TIME: {ai_result.get('estimated_time', 'N/A')}

TECHNICAL RECOMMENDATIONS:
{ai_result.get('recommendations', 'See analysis above')}'''
        
        return ai_result.get('content', 'AI analysis completed')
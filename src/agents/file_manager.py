"""
File Manager Agent - Handles file operations, project structure management
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..core.models import Colors
from ..core.utils import colored_print, gather_file_context, gather_directory_context, gather_project_context


class FileManagerAgent:
    """Specialized agent for file and project management operations"""
    
    def __init__(self, terminal_instance, comm_instance):
        self.terminal = terminal_instance
        self.comm = comm_instance
        self.agent_id = "file_manager"
        self.workspace_dir = terminal_instance.workspace_dir
    
    def handle_file_management_task(self, task: Dict) -> Dict:
        """Handle file management tasks - create directories, organize project structure, edit files"""
        description = task["description"]
        task_data = task.get("data", {})
        
        colored_print(f"FILE MANAGER: Processing file management task", Colors.BRIGHT_CYAN)
        colored_print(f"   Task: {description}", Colors.CYAN)
        
        # Check for specific delegated task types
        if task_data.get("generation_task"):
            return self.handle_code_generation_file_task(task)
        elif task_data.get("rewrite_task") or task_data.get("review_fix_task"):
            return self.handle_code_editing_task(task)
        
        # Check if this is an edit task or create task
        elif self.is_edit_task(description):
            return self.handle_file_edit_task(description, task_data)
        else:
            return self.handle_file_create_task(task)
    
    def is_edit_task(self, description: str) -> bool:
        """Determine if this is an edit task or create task"""
        edit_keywords = ["edit", "modify", "update", "change", "add to", "enhance", "improve"]
        desc_lower = description.lower()
        return any(keyword in desc_lower for keyword in edit_keywords)
    
    def handle_file_create_task(self, task: Dict) -> Dict:
        """Handle file creation tasks - Enhanced with auto project location"""
        description = task["description"]
        task_data = task.get("data", {})
        
        colored_print(f"FILE MANAGER: Processing creation task", Colors.BRIGHT_YELLOW)
        colored_print(f"   Task: {description}", Colors.WHITE)
        
        # STEP 1: Auto-locate existing project directory FIRST
        existing_project = self.auto_locate_project_directory(description, task_data)
        
        if existing_project:
            # Use existing project - create files within it
            project_path = existing_project["path"]
            project_name = existing_project["name"]
            
            colored_print(f"   FOUND: Located existing project '{project_name}'", Colors.BRIGHT_GREEN)
            colored_print(f"   PATH: {project_path}", Colors.GREEN)
            
            # Auto-set project focus for all file operations
            self.terminal.set_project_process(project_name)
            
            # Create the requested component/file within existing project
            result = self.create_component_in_existing_project(project_path, description, task_data)
            
            return {
                "type": "file_management_completed",
                "project_path": project_path,
                "project_name": project_name,
                "component_created": result.get("component_name"),
                "files_created": result.get("files_created", []),
                "message": f"Successfully created component in existing project '{project_name}'"
            }
        
        else:
            # No existing project - create new project structure
            colored_print(f"   INFO: No existing project found, creating new project", Colors.CYAN)
            
            # Extract project information from task data and description
            project_info = self.analyze_project_requirements(description, task_data)
            
            # Create project structure
            project_path = self.create_project_structure(project_info)
            
            return {
                "type": "file_management_completed",
                "project_path": project_path,
                "project_info": project_info,
                "message": f"Successfully created project structure at {project_path}",
                "files_created": self.list_created_files(project_path)
            }
    
    def analyze_project_requirements(self, description: str, task_data: Dict = None) -> Dict:
        """Extract project requirements from task description and data"""
        desc_lower = description.lower()
        
        # Determine project type and framework
        project_info = {
            "name": None,
            "type": "generic",
            "framework": "unknown"
        }
        
        # Extract project name from task data or description
        if task_data and task_data.get('project_name'):
            project_info["name"] = task_data['project_name']
        else:
            project_info["name"] = self.extract_project_name_from_description(description, "new-project")
        
        # Detect project type and framework
        if any(framework in desc_lower for framework in ['react', 'vue', 'angular']):
            project_info["type"] = "web_frontend"
            if 'react' in desc_lower:
                project_info["framework"] = "react"
            elif 'vue' in desc_lower:
                project_info["framework"] = "vue"
            elif 'angular' in desc_lower:
                project_info["framework"] = "angular"
        elif any(keyword in desc_lower for keyword in ['python', 'flask', 'django', 'fastapi']):
            project_info["type"] = "python"
            if 'flask' in desc_lower:
                project_info["framework"] = "flask"
            elif 'django' in desc_lower:
                project_info["framework"] = "django"
            elif 'fastapi' in desc_lower:
                project_info["framework"] = "fastapi"
            else:
                project_info["framework"] = "python"
        elif any(keyword in desc_lower for keyword in ['node', 'express', 'nodejs']):
            project_info["type"] = "nodejs"
            project_info["framework"] = "express"
        else:
            # Generic project - determine based on context
            project_info["type"] = "web_frontend"
            project_info["framework"] = "react"  # Default to React
        
        return project_info
    
    def create_project_structure(self, project_info: Dict) -> str:
        """Create actual project structure based on project info"""
        project_name = project_info["name"]
        project_type = project_info["type"]
        framework = project_info["framework"]
        
        project_path = os.path.join(self.workspace_dir, project_name)
        
        colored_print(f"   CREATING: {project_type} project with {framework}", Colors.BRIGHT_GREEN)
        colored_print(f"   PATH: {project_path}", Colors.GREEN)
        
        # Create base project directory
        os.makedirs(project_path, exist_ok=True)
        
        # Create project structure based on type and framework
        if project_type == "web_frontend":
            if framework == "react":
                self._create_react_project_files(project_path, project_name)
            elif framework == "vue":
                self._create_vue_project_files(project_path, project_name)
            else:
                self._create_generic_web_project_files(project_path, project_name)
        elif project_type == "python":
            if framework == "flask":
                self._create_flask_project_files(project_path, project_name)
            else:
                self._create_python_project_files(project_path, project_name)
        elif project_type == "nodejs":
            self._create_nodejs_project_files(project_path, project_name)
        else:
            self._create_generic_project_files(project_path, project_name)
        
        # Set this as the current project
        self.terminal.set_project_process(project_name)
        
        return project_path
    
    def list_created_files(self, project_path: str) -> List[str]:
        """List all files created in the project"""
        files = []
        if os.path.exists(project_path):
            for root, dirs, filenames in os.walk(project_path):
                for filename in filenames:
                    rel_path = os.path.relpath(os.path.join(root, filename), project_path)
                    files.append(rel_path)
        return files
    
    def auto_locate_project_directory(self, description: str, task_data: Dict = None) -> Dict:
        """Automatically locate existing project directory without creating UnknownProject"""
        
        colored_print(f"   AUTO: Scanning workspace for existing projects...", Colors.CYAN)
        
        # Check if we want to force a new project
        force_new = (
            "new" in description.lower() or 
            "create" in description.lower() and "project" in description.lower() or
            (task_data and task_data.get('project_name') and not os.path.exists(os.path.join(self.workspace_dir, task_data['project_name'])))
        )
        
        if force_new:
            colored_print(f"   FORCE_NEW: Creating new project as requested", Colors.BRIGHT_YELLOW)
            return None
        
        # PRIORITY 1: Use current project if already set (only if not forcing new)
        if hasattr(self.terminal, 'current_project_process') and self.terminal.current_project_process:
            current_path = os.path.join(self.workspace_dir, self.terminal.current_project_process)
            if os.path.exists(current_path):
                colored_print(f"   CURRENT: Using active project '{self.terminal.current_project_process}'", Colors.BRIGHT_GREEN)
                return {
                    "name": self.terminal.current_project_process,
                    "path": current_path,
                    "source": "current_project"
                }
        
        # PRIORITY 2: Look for project name in task data
        if task_data and 'project_name' in task_data:
            project_name = task_data['project_name']
            project_path = os.path.join(self.workspace_dir, project_name)
            if os.path.exists(project_path):
                colored_print(f"   TASK_DATA: Found project '{project_name}' from task data", Colors.BRIGHT_GREEN)
                return {
                    "name": project_name,
                    "path": project_path,
                    "source": "task_data"
                }
        
        # PRIORITY 3: Scan all existing projects in workspace
        existing_projects = []
        if os.path.exists(self.workspace_dir):
            for item in os.listdir(self.workspace_dir):
                item_path = os.path.join(self.workspace_dir, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    # Analyze if this is a valid project directory
                    project_info = self.analyze_existing_project_structure(item_path)
                    if project_info:
                        existing_projects.append({
                            "name": item,
                            "path": item_path,
                            "framework": project_info.get("framework"),
                            "suitability": self.calculate_project_suitability(item_path, description)
                        })
        
        if existing_projects:
            colored_print(f"   SCAN: Found {len(existing_projects)} existing projects", Colors.CYAN)
            for proj in existing_projects:
                colored_print(f"      • {proj['name']} ({proj['framework']}) - Suitability: {proj['suitability']}", Colors.CYAN)
            
            # PRIORITY 4: Use most suitable existing project
            best_project = max(existing_projects, key=lambda x: x['suitability'])
            if best_project['suitability'] > 0.3:  # Minimum suitability threshold
                colored_print(f"   BEST_MATCH: Selected '{best_project['name']}' (suitability: {best_project['suitability']:.2f})", Colors.BRIGHT_GREEN)
                return {
                    "name": best_project['name'],
                    "path": best_project['path'],
                    "source": "auto_selected",
                    "suitability": best_project['suitability']
                }
        
        colored_print(f"   RESULT: No suitable existing project found", Colors.YELLOW)
        return None
    
    def analyze_existing_project_structure(self, project_path: str) -> Dict:
        """Analyze an existing directory to determine if it's a valid project"""
        
        project_info = {"framework": "unknown", "is_valid_project": False}
        
        try:
            files = os.listdir(project_path)
            
            # Check for common project indicators
            if "package.json" in files:
                project_info["framework"] = "javascript/node"
                project_info["is_valid_project"] = True
            elif "requirements.txt" in files or "setup.py" in files:
                project_info["framework"] = "python"
                project_info["is_valid_project"] = True
            elif "pom.xml" in files:
                project_info["framework"] = "java"
                project_info["is_valid_project"] = True
            elif "Cargo.toml" in files:
                project_info["framework"] = "rust"
                project_info["is_valid_project"] = True
            elif "src" in files or "components" in files:
                project_info["is_valid_project"] = True
                
                # Check deeper for React/Vue indicators
                src_path = os.path.join(project_path, "src")
                if os.path.exists(src_path):
                    src_files = os.listdir(src_path)
                    if any(".jsx" in f for f in src_files):
                        project_info["framework"] = "react"
                    elif any(".vue" in f for f in src_files):
                        project_info["framework"] = "vue"
                    elif "App.js" in src_files:
                        project_info["framework"] = "react"
        except:
            pass
        
        return project_info if project_info["is_valid_project"] else None
    
    def calculate_project_suitability(self, project_path: str, task_description: str) -> float:
        """Calculate how suitable an existing project is for the given task"""
        
        suitability = 0.0
        desc_lower = task_description.lower()
        project_name = os.path.basename(project_path).lower()
        
        # Name matching
        if "time" in desc_lower and "time" in project_name:
            suitability += 0.8
        elif "todo" in desc_lower and "todo" in project_name:
            suitability += 0.8
        elif "app" in desc_lower and "app" in project_name:
            suitability += 0.4
        
        # Component matching
        try:
            # Check if project has similar components already
            if os.path.exists(os.path.join(project_path, "src", "components")):
                components_dir = os.path.join(project_path, "src", "components")
                component_files = os.listdir(components_dir)
                
                if "time" in desc_lower:
                    if any("time" in f.lower() for f in component_files):
                        suitability += 0.5
                if "date" in desc_lower:
                    if any("date" in f.lower() for f in component_files):
                        suitability += 0.5
                        
                # Base suitability for having components directory
                suitability += 0.2
        except:
            pass
        
        # Framework compatibility
        project_info = self.analyze_existing_project_structure(project_path)
        if project_info:
            if ("react" in desc_lower and project_info.get("framework") == "react") or \
               ("vue" in desc_lower and project_info.get("framework") == "vue") or \
               ("javascript" in desc_lower and "javascript" in project_info.get("framework", "")):
                suitability += 0.3
        
        return min(suitability, 1.0)  # Cap at 1.0
    
    def create_component_in_existing_project(self, project_path: str, description: str, task_data: Dict) -> Dict:
        """Create component in existing project structure"""
        
        # Analyze what component to create
        component_info = self.analyze_component_requirements(description, project_path)
        
        # Get project structure context for AI
        project_context = self.get_project_structure_context(project_path)
        
        # Use AI to generate component code
        result = self.generate_component_with_ai(project_path, component_info, project_context, description)
        
        return result
    
    def analyze_component_requirements(self, description: str, project_path: str) -> Dict:
        """Analyze what component needs to be created"""
        
        desc_lower = description.lower()
        component_info = {
            "name": "UnknownComponent",
            "type": "generic",
            "features": [],
            "target_dir": "src/components"
        }
        
        # Detect component name and type
        if "time" in desc_lower:
            component_info["name"] = "TimeComponent"
            component_info["type"] = "display"
            component_info["features"] = ["time_display", "real_time_updates", "formatting"]
        elif "date" in desc_lower:
            component_info["name"] = "DateComponent"  
            component_info["type"] = "display"
            component_info["features"] = ["date_display", "formatting"]
        elif "week" in desc_lower:
            component_info["name"] = "WeekComponent"
            component_info["type"] = "display"
            component_info["features"] = ["week_number", "week_display"]
        elif "todo" in desc_lower or "task" in desc_lower:
            component_info["name"] = "TodoComponent"
            component_info["type"] = "interactive"
            component_info["features"] = ["add_task", "remove_task", "mark_complete"]
        elif "button" in desc_lower:
            component_info["name"] = "Button"
            component_info["type"] = "ui"
            component_info["features"] = ["clickable", "customizable"]
        
        # Determine target directory based on project structure
        if os.path.exists(os.path.join(project_path, "src", "components")):
            component_info["target_dir"] = "src/components"
        elif os.path.exists(os.path.join(project_path, "components")):
            component_info["target_dir"] = "components"
        elif os.path.exists(os.path.join(project_path, "src")):
            component_info["target_dir"] = "src"
        else:
            component_info["target_dir"] = "."
        
        colored_print(f"      Component: {component_info['name']} ({component_info['type']})", Colors.YELLOW)
        colored_print(f"      Target: {component_info['target_dir']}", Colors.YELLOW)
        colored_print(f"      Features: {', '.join(component_info['features'])}", Colors.YELLOW)
        
        return component_info
    
    def get_project_structure_context(self, project_path: str) -> str:
        """Get project structure context for AI model"""
        
        context = f"PROJECT STRUCTURE ANALYSIS:\\n"
        context += f"Project Path: {project_path}\\n\\n"
        
        try:
            # Get directory structure
            context += "DIRECTORY STRUCTURE:\\n"
            for root, dirs, files in os.walk(project_path):
                level = root.replace(project_path, '').count(os.sep)
                indent = '  ' * level
                context += f"{indent}{os.path.basename(root)}/\\n"
                
                sub_indent = '  ' * (level + 1)
                for file in files[:10]:  # Limit to first 10 files per directory
                    context += f"{sub_indent}{file}\\n"
                    
                if len(files) > 10:
                    context += f"{sub_indent}... ({len(files) - 10} more files)\\n"
                
                # Don't go too deep
                if level > 3:
                    dirs[:] = []
        except:
            pass
        
        return context
    
    def generate_component_with_ai(self, project_path: str, component_info: Dict, project_context: str, description: str) -> Dict:
        """Generate component using AI with project context"""
        
        # Create standardized AI input for component generation
        standardized_input = self.terminal.create_standardized_ai_input(
            operation_type="COMPONENT_CREATION",
            task_description=f"Create {component_info['name']} component: {description}",
            context_type="PROJECT_COMPONENT",
            requirements=[
                f"Create a {component_info['type']} component named {component_info['name']}",
                f"Include features: {', '.join(component_info['features'])}",
                f"Place in directory: {component_info['target_dir']}",
                "Follow project conventions and patterns",
                "Include proper imports and exports"
            ],
            constraints=[
                f"Use existing project structure at {project_path}",
                "Maintain consistency with existing code style",
                "Include proper error handling",
                "Add appropriate comments and documentation"
            ],
            expected_output="COMPONENT_FILES",
            additional_context=project_context
        )
        
        # Execute AI operation
        ai_result = self.terminal.execute_standardized_ai_operation(standardized_input)
        
        if ai_result.get('status') == 'success':
            return {
                "component_name": component_info['name'],
                "files_created": ai_result.get('files_created', []),
                "implementation": ai_result.get('implementation', ''),
                "status": "success"
            }
        else:
            return {
                "component_name": component_info['name'],
                "files_created": [],
                "status": "failed",
                "error": ai_result.get('error', 'Component generation failed')
            }
    
    def handle_code_generation_file_task(self, task: Dict) -> Dict:
        """Handle file operations for code generation tasks"""
        description = task["description"]
        task_data = task.get("data", {})
        code_requirements = task_data.get("code_requirements", {})
        
        colored_print(f"FILE MANAGER: Processing code generation file task", Colors.BRIGHT_GREEN)
        colored_print(f"   Requirements: {code_requirements.get('language', 'unknown')} {code_requirements.get('file_type', 'file')}", Colors.GREEN)
        
        # Auto-locate existing project or create appropriate structure
        project_info = self.find_or_create_project_for_generation(task_data, description)
        
        if project_info:
            # Generate and create the actual files
            result = self.create_code_files(project_info, code_requirements, description)
            
            return {
                "type": "code_generation_file_completed",
                "project_path": project_info["path"],
                "files_created": result.get("files_created", []),
                "code_generated": True,
                "message": f"Code generation completed in project: {project_info['name']}"
            }
        else:
            return {
                "type": "code_generation_file_failed",
                "error": "Could not determine appropriate project location",
                "message": "Failed to locate or create project for code generation"
            }
    
    def handle_code_editing_task(self, task: Dict) -> Dict:
        """Handle file editing for code rewriter tasks"""
        description = task["description"]
        task_data = task.get("data", {})
        
        colored_print(f"FILE MANAGER: Processing code editing task", Colors.BRIGHT_MAGENTA)
        
        if task_data.get("review_fix_task"):
            return self.handle_review_fix_file_task(task)
        elif task_data.get("rewrite_task"):
            return self.handle_rewrite_file_task(task)
        else:
            # Fallback to general file editing
            return self.handle_file_edit_task(description, task_data)
    
    def handle_review_fix_file_task(self, task: Dict) -> Dict:
        """Handle file editing for review fixes"""
        task_data = task.get("data", {})
        file_path = task_data.get("file_path")
        issues_to_fix = task_data.get("issues_to_fix", [])
        
        colored_print(f"FILE MANAGER: Applying review fixes to {file_path}", Colors.YELLOW)
        colored_print(f"   Issues to fix: {len(issues_to_fix)}", Colors.WHITE)
        
        # Apply each fix systematically
        fixes_applied = []
        fixes_failed = []
        
        for issue in issues_to_fix:
            fix_result = self.apply_single_file_fix(file_path, issue)
            
            if fix_result.get("success"):
                fixes_applied.append(fix_result)
                colored_print(f"   FIXED: {issue.get('description', 'Unknown issue')}", Colors.GREEN)
            else:
                fixes_failed.append(fix_result)
                colored_print(f"   FAILED: {issue.get('description', 'Unknown issue')}", Colors.RED)
        
        return {
            "type": "review_fixes_applied",
            "file_path": file_path,
            "fixes_applied": len(fixes_applied),
            "fixes_failed": len(fixes_failed),
            "details": {
                "successful_fixes": fixes_applied,
                "failed_fixes": fixes_failed
            },
            "message": f"Applied {len(fixes_applied)}/{len(issues_to_fix)} fixes to {file_path}"
        }
    
    def handle_rewrite_file_task(self, task: Dict) -> Dict:
        """Handle general file rewriting tasks"""
        task_data = task.get("data", {})
        file_path = task_data.get("file_path")
        changes_required = task_data.get("changes_required", {})
        
        colored_print(f"FILE MANAGER: Rewriting file {file_path}", Colors.MAGENTA)
        colored_print(f"   Change type: {changes_required.get('type', 'general')}", Colors.WHITE)
        
        # Execute the rewrite operation
        rewrite_result = self.execute_file_rewrite(file_path, changes_required, task_data.get("original_description", ""))
        
        return {
            "type": "file_rewrite_completed",
            "file_path": file_path,
            "changes_applied": rewrite_result.get("changes_applied", []),
            "rewrite_successful": rewrite_result.get("success", False),
            "message": f"File rewrite completed: {rewrite_result.get('summary', 'Rewrite finished')}"
        }
    
    def handle_file_edit_task(self, description: str, task_data: Dict = None) -> Dict:
        """Handle file editing tasks"""
        
        colored_print(f"FILE MANAGER: Processing edit task", Colors.BRIGHT_YELLOW)
        colored_print(f"   Task: {description}", Colors.WHITE)
        
        # Use AI to analyze edit requirements and execute
        edit_result = self.execute_file_edit_with_ai(description, task_data)
        
        return {
            "type": "file_edit_completed",
            "files_modified": edit_result.get("files_modified", []),
            "changes_made": edit_result.get("changes_made", []),
            "message": f"File edit task completed: {edit_result.get('summary', 'Edit finished')}"
        }
    
    def execute_file_edit_with_ai(self, description: str, task_data: Dict = None) -> Dict:
        """Execute file edits using AI assistance"""
        
        # Get current project context
        project_context = ""
        if hasattr(self.terminal, 'current_project_process') and self.terminal.current_project_process:
            project_path = os.path.join(self.workspace_dir, self.terminal.current_project_process)
            project_context = self.get_project_structure_context(project_path)
        
        # Create standardized AI input for file editing
        standardized_input = self.terminal.create_standardized_ai_input(
            operation_type="FILE_EDIT",
            task_description=f"File editing task: {description}",
            context_type="PROJECT_MODIFICATION",
            requirements=[
                "Analyze which files need to be modified",
                "Make precise and targeted changes",
                "Preserve existing functionality",
                "Follow project conventions"
            ],
            constraints=[
                "Only modify necessary files",
                "Maintain code quality and style",
                "Include proper validation",
                "Document changes clearly"
            ],
            expected_output="FILE_MODIFICATIONS",
            additional_context=project_context
        )
        
        # Execute AI operation
        ai_result = self.terminal.execute_standardized_ai_operation(standardized_input)
        
        if ai_result.get('status') == 'success':
            return {
                "files_modified": ai_result.get('files_modified', []),
                "changes_made": ai_result.get('changes_made', []),
                "summary": ai_result.get('summary', 'Files edited successfully'),
                "status": "success"
            }
        else:
            return {
                "files_modified": [],
                "changes_made": [],
                "summary": "File editing failed",
                "status": "failed",
                "error": ai_result.get('error', 'Edit operation failed')
            }
    
    def find_or_create_project_for_generation(self, task_data: Dict, description: str) -> Dict:
        """Find existing project or determine where to create code files"""
        
        # Try to auto-locate existing project first
        existing_project = self.auto_locate_project_directory(description, task_data)
        
        if existing_project:
            return existing_project
        
        # If no existing project, analyze requirements to determine project structure
        code_requirements = task_data.get("code_requirements", {})
        language = code_requirements.get("language", "javascript")
        framework = code_requirements.get("framework")
        
        # Create appropriate project structure based on requirements
        if framework == "react":
            return self.create_react_project_structure(description)
        elif language == "python":
            return self.create_python_project_structure(description)
        else:
            return self.create_generic_project_structure(description, language)
    
    def edit_file_with_context(self, target_file: str, description: str, context_paths: List[Union[str, Path]] = None) -> Dict:
        """Edit a file with full context awareness"""
        
        colored_print(f"FILE MANAGER: Context-aware file editing", Colors.BRIGHT_BLUE)
        colored_print(f"   TARGET: {target_file}", Colors.WHITE)
        
        # Gather context
        context_data = {}
        
        # Add target file context if it exists
        if os.path.exists(target_file):
            context_data["target_file"] = gather_file_context(target_file)
            colored_print(f"   CONTEXT: Target file loaded ({context_data['target_file'].get('size_formatted', 'unknown')})", Colors.CYAN)
        else:
            colored_print(f"   INFO: Target file will be created: {target_file}", Colors.YELLOW)
        
        # Add reference files/directories
        if context_paths:
            colored_print(f"   CONTEXT: Gathering context from {len(context_paths)} paths", Colors.CYAN)
            
            for path in context_paths:
                path_obj = Path(path)
                colored_print(f"     • {path_obj.name}", Colors.WHITE)
                
                if path_obj.is_file():
                    context_data[f"reference_{path_obj.name}"] = gather_file_context(path_obj)
                elif path_obj.is_dir():
                    context_data[f"reference_{path_obj.name}"] = gather_directory_context(path_obj)
        
        # Add project context
        if hasattr(self.terminal, 'current_project_process') and self.terminal.current_project_process:
            project_path = os.path.join(self.workspace_dir, self.terminal.current_project_process)
            if os.path.exists(project_path):
                colored_print(f"   PROJECT: Adding project context: {self.terminal.current_project_process}", Colors.CYAN)
                context_data["project"] = gather_project_context(project_path)
        
        # Format context for AI
        context_summary = self.format_context_for_ai(context_data)
        
        # Enhanced AI operation for file editing
        standardized_input = self.terminal.create_standardized_ai_input(
            operation_type="CONTEXTUAL_FILE_EDITING",
            task_description=f"Edit file {target_file}: {description}",
            context_type="FULL_PROJECT_CONTEXT",
            requirements=[
                "Analyze existing file content and project structure",
                "Make precise changes based on the description",
                "Follow existing code patterns and conventions",
                "Maintain compatibility with project architecture",
                "Include proper imports and dependencies"
            ],
            constraints=[
                "Preserve existing functionality unless explicitly changed",
                "Use consistent coding style with the project",
                "Maintain proper file structure and organization",
                "Ensure changes work with existing project setup",
                "Add appropriate error handling and validation"
            ],
            expected_output="FILE_EDIT_RESULT",
            additional_context=context_summary
        )
        
        ai_result = self.terminal.execute_standardized_ai_operation(standardized_input)
        
        success = ai_result.get('status') == 'success'
        
        if success:
            colored_print(f"   SUCCESS: File editing completed with context", Colors.BRIGHT_GREEN)
        else:
            colored_print(f"   ERROR: Context-aware file editing failed", Colors.RED)
        
        return {
            "success": success,
            "file_path": target_file,
            "content_updated": ai_result.get('content_updated', ''),
            "changes_made": ai_result.get('changes_made', []),
            "context_used": len(context_data),
            "summary": ai_result.get('summary', 'Context-aware file edit completed')
        }
    
    def create_file_with_context(self, file_path: str, description: str, context_paths: List[Union[str, Path]] = None) -> Dict:
        """Create a new file with context awareness"""
        
        colored_print(f"FILE MANAGER: Context-aware file creation", Colors.BRIGHT_GREEN)
        colored_print(f"   TARGET: {file_path}", Colors.WHITE)
        
        # Gather context
        context_data = {}
        
        # Add reference files/directories
        if context_paths:
            colored_print(f"   CONTEXT: Gathering context from {len(context_paths)} paths", Colors.CYAN)
            
            for path in context_paths:
                path_obj = Path(path)
                colored_print(f"     • {path_obj.name}", Colors.WHITE)
                
                if path_obj.is_file():
                    context_data[f"reference_{path_obj.name}"] = gather_file_context(path_obj)
                elif path_obj.is_dir():
                    context_data[f"reference_{path_obj.name}"] = gather_directory_context(path_obj)
        
        # Add project context
        if hasattr(self.terminal, 'current_project_process') and self.terminal.current_project_process:
            project_path = os.path.join(self.workspace_dir, self.terminal.current_project_process)
            if os.path.exists(project_path):
                colored_print(f"   PROJECT: Adding project context: {self.terminal.current_project_process}", Colors.CYAN)
                context_data["project"] = gather_project_context(project_path)
        
        # Format context for AI
        context_summary = self.format_context_for_ai(context_data)
        
        # Enhanced AI operation for file creation
        standardized_input = self.terminal.create_standardized_ai_input(
            operation_type="CONTEXTUAL_FILE_CREATION",
            task_description=f"Create file {file_path}: {description}",
            context_type="FULL_PROJECT_CONTEXT",
            requirements=[
                "Create functional, complete file content",
                "Follow existing project patterns and conventions",
                "Include proper imports and dependencies",
                "Add appropriate documentation and comments",
                "Ensure compatibility with project structure"
            ],
            constraints=[
                "Use consistent coding style with the project",
                "Follow established naming conventions",
                "Include proper error handling where appropriate",
                "Make the file integrate seamlessly with existing code",
                "Follow language and framework best practices"
            ],
            expected_output="FILE_CREATION_RESULT",
            additional_context=context_summary
        )
        
        ai_result = self.terminal.execute_standardized_ai_operation(standardized_input)
        
        success = ai_result.get('status') == 'success'
        
        if success:
            colored_print(f"   SUCCESS: File creation completed with context", Colors.BRIGHT_GREEN)
        else:
            colored_print(f"   ERROR: Context-aware file creation failed", Colors.RED)
        
        return {
            "success": success,
            "file_path": file_path,
            "content_created": ai_result.get('content_created', ''),
            "features_included": ai_result.get('features_included', []),
            "context_used": len(context_data),
            "summary": ai_result.get('summary', 'Context-aware file creation completed')
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
{data['content'][:2500]}{'...[truncated]' if len(data['content']) > 2500 else ''}
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
    
    def create_code_files(self, project_info: Dict, code_requirements: Dict, description: str) -> Dict:
        """Create actual code files based on requirements"""
        
        project_path = project_info["path"]
        language = code_requirements.get("language", "javascript")
        features = code_requirements.get("features", [])
        
        colored_print(f"   CREATING: Code files in {project_path}", Colors.GREEN)
        
        # Use AI to generate appropriate code based on requirements
        code_generation_input = self.terminal.create_standardized_ai_input(
            operation_type="CODE_GENERATION",
            task_description=f"Generate {language} code: {description}",
            context_type="FILE_CREATION",
            requirements=[
                f"Create {language} files for: {', '.join(features) if features else 'basic functionality'}",
                "Follow best practices and conventions",
                "Include proper structure and organization",
                "Add necessary imports and dependencies"
            ],
            constraints=[
                f"Target directory: {project_path}",
                f"Language: {language}",
                "Create functional, ready-to-use code",
                "Include proper error handling"
            ],
            expected_output="CODE_FILES",
            additional_context=f"Project structure: {self.get_project_structure_context(project_path)}"
        )
        
        ai_result = self.terminal.execute_standardized_ai_operation(code_generation_input)
        
        files_created = []
        if ai_result.get('status') == 'success':
            files_created = ai_result.get('files_created', [])
            colored_print(f"   SUCCESS: Created {len(files_created)} files", Colors.BRIGHT_GREEN)
        
        return {
            "files_created": files_created,
            "generation_successful": ai_result.get('status') == 'success',
            "summary": ai_result.get('summary', 'Code generation completed')
        }
    
    def apply_single_file_fix(self, file_path: str, issue: Dict) -> Dict:
        """Apply a single fix to a file based on review issue"""
        
        colored_print(f"     Applying fix for: {issue.get('description', 'Unknown issue')}", Colors.CYAN)
        
        # Use AI to generate and apply the specific fix
        fix_input = self.terminal.create_standardized_ai_input(
            operation_type="FILE_FIX",
            task_description=f"Fix issue in {file_path}: {issue.get('description', '')}",
            context_type="CODE_REVIEW_FIX",
            requirements=[
                "Apply specific fix for the identified issue",
                "Maintain existing functionality",
                "Follow coding best practices",
                "Ensure fix is targeted and minimal"
            ],
            constraints=[
                f"Target file: {file_path}",
                f"Issue severity: {issue.get('severity', 'MEDIUM')}",
                f"Issue type: {issue.get('type', 'general')}",
                "Only modify necessary code sections"
            ],
            expected_output="FILE_MODIFICATION",
            additional_context=f"Issue details: {issue}"
        )
        
        ai_result = self.terminal.execute_standardized_ai_operation(fix_input)
        
        return {
            "success": ai_result.get('status') == 'success',
            "issue_description": issue.get('description', ''),
            "fix_applied": ai_result.get('fix_applied', ''),
            "changes_made": ai_result.get('changes_made', []),
            "summary": ai_result.get('summary', 'Fix attempt completed')
        }
    
    def execute_file_rewrite(self, file_path: str, changes_required: Dict, original_description: str) -> Dict:
        """Execute file rewrite based on change requirements"""
        
        change_type = changes_required.get("type", "general_rewrite")
        focus_areas = changes_required.get("focus_areas", [])
        
        colored_print(f"     Rewriting with focus on: {', '.join(focus_areas) if focus_areas else 'general improvement'}", Colors.CYAN)
        
        # Use AI to perform the rewrite
        rewrite_input = self.terminal.create_standardized_ai_input(
            operation_type="FILE_REWRITE",
            task_description=f"Rewrite {file_path}: {original_description}",
            context_type="CODE_REFACTORING",
            requirements=[
                f"Perform {change_type} on the file",
                f"Focus on: {', '.join(focus_areas) if focus_areas else 'general improvements'}",
                "Maintain functionality while improving code quality",
                "Apply modern best practices"
            ],
            constraints=[
                f"Target file: {file_path}",
                f"Rewrite type: {change_type}",
                "Preserve existing API and interfaces",
                "Maintain backward compatibility where possible"
            ],
            expected_output="FILE_REWRITE",
            additional_context=f"Change requirements: {changes_required}"
        )
        
        ai_result = self.terminal.execute_standardized_ai_operation(rewrite_input)
        
        return {
            "success": ai_result.get('status') == 'success',
            "changes_applied": ai_result.get('changes_applied', []),
            "rewrite_type": change_type,
            "summary": ai_result.get('summary', 'File rewrite completed')
        }
    
    def create_react_project_structure(self, description: str) -> Dict:
        """Create React project structure for code generation"""
        # Implementation would create React-specific directory structure
        project_name = self.extract_project_name_from_description(description, "react-app")
        project_path = os.path.join(self.workspace_dir, project_name)
        
        return {
            "name": project_name,
            "path": project_path,
            "type": "react",
            "structure_created": True
        }
    
    def create_python_project_structure(self, description: str) -> Dict:
        """Create Python project structure for code generation"""
        # Implementation would create Python-specific directory structure
        project_name = self.extract_project_name_from_description(description, "python-project")
        project_path = os.path.join(self.workspace_dir, project_name)
        
        return {
            "name": project_name,
            "path": project_path,
            "type": "python",
            "structure_created": True
        }
    
    def create_generic_project_structure(self, description: str, language: str) -> Dict:
        """Create generic project structure for code generation"""
        project_name = self.extract_project_name_from_description(description, f"{language}-project")
        project_path = os.path.join(self.workspace_dir, project_name)
        
        return {
            "name": project_name,
            "path": project_path,
            "type": language,
            "structure_created": True
        }
    
    def extract_project_name_from_description(self, description: str, default_prefix: str) -> str:
        """Extract or generate project name from task description"""
        desc_lower = description.lower()
        
        # Look for common project indicators
        if "todo" in desc_lower:
            return "todo-app"
        elif "timer" in desc_lower or "clock" in desc_lower:
            return "timer-app"
        elif "counter" in desc_lower:
            return "counter-app"
        elif "calculator" in desc_lower:
            return "calculator-app"
        else:
            # Generate based on timestamp
            timestamp = datetime.now().strftime("%H%M%S")
            return f"{default_prefix}-{timestamp}"
    
    def _create_react_project_files(self, project_path: str, project_name: str):
        """Create React project structure and files"""
        # Create directories
        os.makedirs(os.path.join(project_path, "src"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "src", "components"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "public"), exist_ok=True)
        
        # Create package.json
        package_json = {
            "name": project_name,
            "version": "1.0.0",
            "dependencies": {
                "react": "^18.0.0",
                "react-dom": "^18.0.0"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test"
            }
        }
        
        with open(os.path.join(project_path, "package.json"), "w") as f:
            import json
            json.dump(package_json, f, indent=2)
        
        # Create basic React app files
        app_js = f"""import React from 'react';
import './App.css';

function App() {{
  return (
    <div className="App">
      <h1>Welcome to {project_name}</h1>
    </div>
  );
}}

export default App;"""
        
        with open(os.path.join(project_path, "src", "App.js"), "w") as f:
            f.write(app_js)
        
        # Create index.js
        index_js = """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);"""
        
        with open(os.path.join(project_path, "src", "index.js"), "w") as f:
            f.write(index_js)
        
        # Create public/index.html
        index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
</head>
<body>
    <div id="root"></div>
</body>
</html>"""
        
        with open(os.path.join(project_path, "public", "index.html"), "w") as f:
            f.write(index_html)
        
        colored_print(f"   ✅ Created React project structure", Colors.GREEN)
    
    def _create_vue_project_files(self, project_path: str, project_name: str):
        """Create Vue.js project structure and files"""
        # Create directories
        os.makedirs(os.path.join(project_path, "src"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "src", "components"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "public"), exist_ok=True)
        
        # Create package.json
        package_json = {
            "name": project_name,
            "version": "1.0.0",
            "dependencies": {
                "vue": "^3.0.0"
            },
            "scripts": {
                "dev": "vite",
                "build": "vite build"
            }
        }
        
        with open(os.path.join(project_path, "package.json"), "w") as f:
            import json
            json.dump(package_json, f, indent=2)
        
        # Create Vue app file
        app_vue = f"""<template>
  <div id="app">
    <h1>Welcome to {project_name}</h1>
  </div>
</template>

<script>
export default {{
  name: 'App'
}}
</script>"""
        
        with open(os.path.join(project_path, "src", "App.vue"), "w") as f:
            f.write(app_vue)
        
        colored_print(f"   ✅ Created Vue.js project structure", Colors.GREEN)
    
    def _create_python_project_files(self, project_path: str, project_name: str):
        """Create Python project structure and files"""
        # Create directories
        os.makedirs(os.path.join(project_path, "src"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "tests"), exist_ok=True)
        
        # Create requirements.txt
        with open(os.path.join(project_path, "requirements.txt"), "w") as f:
            f.write("# Python dependencies\n")
        
        # Create main.py
        main_py = f"""#!/usr/bin/env python3
\"\"\"
{project_name} - Main application
\"\"\"

def main():
    print("Welcome to {project_name}")

if __name__ == "__main__":
    main()
"""
        
        with open(os.path.join(project_path, "main.py"), "w") as f:
            f.write(main_py)
        
        # Create README.md
        readme = f"""# {project_name}

A Python project.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```
"""
        
        with open(os.path.join(project_path, "README.md"), "w") as f:
            f.write(readme)
        
        colored_print(f"   ✅ Created Python project structure", Colors.GREEN)
    
    def _create_flask_project_files(self, project_path: str, project_name: str):
        """Create Flask project structure and files"""
        # Create directories
        os.makedirs(os.path.join(project_path, "templates"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "static"), exist_ok=True)
        
        # Create requirements.txt
        with open(os.path.join(project_path, "requirements.txt"), "w") as f:
            f.write("Flask==2.3.0\n")
        
        # Create app.py
        app_py = f"""from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', title='{project_name}')

if __name__ == '__main__':
    app.run(debug=True)
"""
        
        with open(os.path.join(project_path, "app.py"), "w") as f:
            f.write(app_py)
        
        # Create templates/index.html
        index_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{{{{ title }}}}</title>
</head>
<body>
    <h1>Welcome to {project_name}</h1>
</body>
</html>"""
        
        with open(os.path.join(project_path, "templates", "index.html"), "w") as f:
            f.write(index_html)
        
        colored_print(f"   ✅ Created Flask project structure", Colors.GREEN)
    
    def _create_nodejs_project_files(self, project_path: str, project_name: str):
        """Create Node.js/Express project structure and files"""
        # Create package.json
        package_json = {
            "name": project_name,
            "version": "1.0.0",
            "main": "server.js",
            "dependencies": {
                "express": "^4.18.0"
            },
            "scripts": {
                "start": "node server.js",
                "dev": "nodemon server.js"
            }
        }
        
        with open(os.path.join(project_path, "package.json"), "w") as f:
            import json
            json.dump(package_json, f, indent=2)
        
        # Create server.js
        server_js = f"""const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {{
    res.send('<h1>Welcome to {project_name}</h1>');
}});

app.listen(PORT, () => {{
    console.log(`Server running on port ${{PORT}}`);
}});
"""
        
        with open(os.path.join(project_path, "server.js"), "w") as f:
            f.write(server_js)
        
        colored_print(f"   ✅ Created Node.js project structure", Colors.GREEN)
    
    def _create_generic_web_project_files(self, project_path: str, project_name: str):
        """Create generic web project structure"""
        # Create basic HTML structure
        os.makedirs(os.path.join(project_path, "css"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "js"), exist_ok=True)
        
        # Create index.html
        index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <h1>Welcome to {project_name}</h1>
    <script src="js/main.js"></script>
</body>
</html>"""
        
        with open(os.path.join(project_path, "index.html"), "w") as f:
            f.write(index_html)
        
        # Create basic CSS
        style_css = """body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
}

h1 {
    color: #333;
}"""
        
        with open(os.path.join(project_path, "css", "style.css"), "w") as f:
            f.write(style_css)
        
        # Create basic JS
        main_js = """console.log('Project initialized');"""
        
        with open(os.path.join(project_path, "js", "main.js"), "w") as f:
            f.write(main_js)
        
        colored_print(f"   ✅ Created generic web project structure", Colors.GREEN)
    
    def _create_generic_project_files(self, project_path: str, project_name: str):
        """Create basic project structure"""
        # Create README.md
        readme = f"""# {project_name}

A new project.

## Getting Started

This is a basic project structure.
"""
        
        with open(os.path.join(project_path, "README.md"), "w") as f:
            f.write(readme)
        
        colored_print(f"   ✅ Created generic project structure", Colors.GREEN)
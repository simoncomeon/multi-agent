"""
Enhanced File Manager Agent - Framework-agnostic file and project management
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from ..core.base_agent import BaseAgent, TaskInput, TaskResult, FrameworkDetector
from ..core.models import AgentRole, Colors
from ..core.utils import colored_print, format_file_size


class EnhancedFileManagerAgent(BaseAgent):
    """
    Enhanced file manager agent with intelligent project management,
    file operations, and framework-aware directory structures.
    """

    def __init__(self, agent_id: str, workspace_dir: str, **kwargs):
        super().__init__(agent_id, AgentRole.FILE_MANAGER, workspace_dir, **kwargs)

        # File management specific settings
        self.backup_enabled = kwargs.get('backup_enabled', True)
        self.max_file_size = kwargs.get('max_file_size', 10 * 1024 * 1024)  # 10MB
        self.excluded_patterns = kwargs.get('excluded_patterns', [
            '.git', '__pycache__', 'node_modules', '.DS_Store', '*.pyc'
        ])

    def _define_capabilities(self) -> Dict[str, bool]:
        """Define file manager capabilities"""
        return {
            'file_creation': True,
            'file_modification': True,
            'file_deletion': True,
            'directory_management': True,
            'project_scaffolding': True,
            'file_backup': True,
            'batch_operations': True,
            'template_processing': True,
            'project_analysis': True,
            'structure_optimization': True
        }

    def _define_supported_file_types(self) -> List[str]:
        """Support all file types for file management"""
        return ['*']  # File manager can handle any file type

    def _is_task_type_supported(self, task_type: str) -> bool:
        """Check if task type is supported by file manager"""
        supported_types = [
            'file_management', 'file_creation', 'file_modification', 
            'directory_management', 'project_scaffolding', 'file_organization'
        ]
        return task_type in supported_types or task_type == 'general'

    def _execute_specific_task(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """Execute file management task based on input type"""

        # STEP 0a: If coordinator passed a structured dict, handle it first
        if isinstance(task_input.description, dict):
            return self._handle_structured_enrichment_dict(task_input, context)

        # STEP 0b: If description is a JSON-formatted enrichment blob, extract the actual description
        cleaned_input = self._extract_enhanced_description_from_json(task_input)
        if cleaned_input:
            task_input = cleaned_input

        # STEP 1: Check if this task needs AI enrichment first (for project creation)
        needs_enrichment = self._should_enrich_task(task_input.description)

        if needs_enrichment:
            colored_print(f"FILE MANAGER AI: Analyzing task requirements...", Colors.BRIGHT_CYAN)
            # Let file manager enrich the task itself
            enriched_result = self._enrich_and_execute_task(task_input, context)
            if enriched_result:
                return enriched_result
            # If enrichment fails, continue with normal processing

        # STEP 2: Check if this is already an AI-enhanced description that needs parsing
        if self._is_enhanced_ai_description(task_input.description):
            colored_print(f"SMART MODE: Parsing AI-enhanced instructions", Colors.BRIGHT_CYAN)
            return self._handle_enhanced_ai_instructions(task_input, context)

        # STEP 3: Normal task routing
        if task_input.has_directories():
            return self._handle_directory_operations(task_input, context)
        elif task_input.has_files() and not task_input.target_file:
            return self._handle_batch_file_operations(task_input, context)
        elif task_input.target_file:
            return self._handle_single_file_operations(task_input, context)
        else:
            desc_lower = task_input.description.lower() if isinstance(task_input.description, str) else ""
            if ('project' in desc_lower) or ('scaffold' in desc_lower):
                return self._handle_project_scaffolding(task_input, context)
            return self._handle_general_file_operations(task_input, context)

    def _handle_directory_operations(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """Handle directory-level file operations"""
        target_dir = task_input.target_directory or self.workspace_dir
        target_dir = Path(target_dir)

        operations_performed = []

        # Create directory if it doesn't exist
        desc_lower = task_input.description.lower() if isinstance(task_input.description, str) else ""
        if 'create' in desc_lower:
            target_dir.mkdir(parents=True, exist_ok=True)
            operations_performed.append(f"Created directory: {target_dir}")

        # Organize existing files
        if 'organize' in desc_lower:
            result = self._organize_directory_structure(target_dir, task_input)
            operations_performed.extend(result.get('operations', []))

        if any(keyword in desc_lower for keyword in ['scaffold', 'template', 'init']):
            result = self._scaffold_directory_structure(target_dir, task_input, context)
            operations_performed.extend(result.get('operations', []))

        return TaskResult(
            success=True,
            message=f"Directory operations completed on {target_dir}",
            data={'operations': operations_performed},
            files_modified=[str(target_dir)]
        )

    def _handle_batch_file_operations(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """Handle operations on multiple files"""
        colored_print(f" Batch file operations: {len(task_input.files)} files", Colors.BRIGHT_CYAN)

        successful_operations = []
        failed_operations = []

        for file_path in task_input.files:
            try:
                result = self._process_single_file(file_path, task_input, context)
                if result.get('success'):
                    successful_operations.append(str(file_path))
                else:
                    failed_operations.append(f"{file_path}: {result.get('error', 'Unknown error')}")
            except Exception as e:
                failed_operations.append(f"{file_path}: {str(e)}")

        return TaskResult(
            success=len(failed_operations) == 0,
            message=f"Processed {len(successful_operations)} files successfully, {len(failed_operations)} failed",
            data={
                'successful_operations': successful_operations,
                'failed_operations': failed_operations
            },
            files_modified=successful_operations
        )

    def _handle_single_file_operations(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """Handle operations on a single target file"""
        target_file = Path(task_input.target_file)

        # Determine operation type from description
        operation_type = self._detect_operation_type(task_input.description)

        if operation_type == 'create':
            return self._create_file_with_content(target_file, task_input, context)
        elif operation_type == 'modify':
            return self._modify_file_content(target_file, task_input, context)
        elif operation_type == 'delete':
            return self._delete_file(target_file)
        elif operation_type == 'copy':
            return self._copy_file(target_file, task_input)
        elif operation_type == 'move':
            return self._move_file(target_file, task_input)
        else:
            return self._analyze_file(target_file, task_input, context)

    def _handle_project_scaffolding(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """
        ENHANCED: Handle project scaffolding with AI-powered analysis and full project generation
        """
        colored_print(f"AI-POWERED PROJECT SCAFFOLDING", Colors.BRIGHT_CYAN)
        colored_print(f"   Analyzing: {task_input.description}", Colors.CYAN)

        # Check if using project workspace from coordinator context
        if 'project_workspace' in task_input.data:
            project_dir = Path(task_input.data['project_workspace'])
            colored_print(f"   INFO: Using project context from coordinator - {task_input.data.get('project_name')} at {project_dir}", Colors.CYAN)
        else:
            # Determine project directory
            if task_input.target_directory:
                project_dir = Path(task_input.target_directory)
            else:
                # Extract project name from description or data
                project_name = task_input.data.get('project_name') or self._extract_project_name(task_input.description)
                project_dir = self.workspace_dir / project_name

        colored_print(f"   Target Directory: {project_dir}", Colors.GREEN)

        # STEP 1: Use AI to analyze the task and determine optimal project structure
        ai_analysis = self._ai_analyze_project_requirements(task_input.description, context)
        
        if not ai_analysis.get('success'):
            colored_print(f"   WARNING: AI analysis unavailable, using heuristic approach", Colors.YELLOW)
            return self._fallback_project_creation(project_dir, task_input, context)
        
        colored_print(f"   COMPLETE: AI Analysis Complete", Colors.GREEN)
        project_plan = ai_analysis.get('project_plan', {})
        
        # Display what AI determined
        framework = project_plan.get('framework', 'unknown')
        components = project_plan.get('components', [])
        colored_print(f"   Framework: {framework}", Colors.CYAN)
        colored_print(f"   Components: {len(components)} identified", Colors.CYAN)
        
        # STEP 2: Create project directory
        project_dir.mkdir(parents=True, exist_ok=True)
        
        created_files = []
        created_directories = []
        
        # STEP 3: Create directory structure
        directories = project_plan.get('directory_structure', [])
        colored_print(f"\n   DIRECTORIES: Creating {len(directories)} directories...", Colors.CYAN)
        for dir_name in directories:
            dir_path = project_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            created_directories.append(str(dir_path))
            colored_print(f"      CREATED: {dir_name}/", Colors.GREEN)
        
        # STEP 4: Generate all project files using AI
        files_to_create = project_plan.get('files', [])
        colored_print(f"\n   FILES: Generating {len(files_to_create)} files...", Colors.CYAN)
        
        for file_info in files_to_create:
            file_path = project_dir / file_info['path']
            file_type = file_info.get('type', 'unknown')
            
            colored_print(f"      Creating: {file_info['path']}", Colors.YELLOW)
            
            # Generate content using AI for each file
            if file_info.get('needs_ai_generation', True):
                content_result = self._ai_generate_file_content(
                    file_path=file_path,
                    file_description=file_info.get('description', ''),
                    project_context={
                        'framework': framework,
                        'project_description': task_input.description,
                        'all_files': [f['path'] for f in files_to_create]
                    },
                    context=context
                )
                
                if content_result.get('success'):
                    content = content_result.get('content', '')
                else:
                    # Use template content if AI generation fails
                    content = file_info.get('template_content', f"// {file_info['path']}\n// TODO: Implement\n")
                    colored_print(f"         WARNING: Using template (AI unavailable)", Colors.YELLOW)
            else:
                content = file_info.get('content', '')
            
            # Write the file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            self.write_file(file_path, content)
            created_files.append(str(file_path))
            colored_print(f"         CREATED: {file_info['path']} ({len(content)} chars)", Colors.GREEN)
        
        # STEP 5: Generate README with project overview
        readme_path = project_dir / "README.md"
        if not readme_path.exists():
            readme_content = self._ai_generate_readme(project_plan, task_input.description)
            self.write_file(readme_path, readme_content)
            created_files.append(str(readme_path))
            colored_print(f"      CREATED: README.md", Colors.GREEN)
        
        colored_print(f"\n   SUCCESS: PROJECT COMPLETE!", Colors.BRIGHT_GREEN)
        colored_print(f"      {len(created_files)} files created", Colors.GREEN)
        colored_print(f"      {len(created_directories)} directories created", Colors.GREEN)

        return TaskResult(
            success=True,
            message=f"SUCCESS: Complete {framework} project created in {project_dir.name}",
            data={
                'framework': framework,
                'project_directory': str(project_dir),
                'components': components,
                'ai_powered': True,
                'project_plan': project_plan
            },
            files_created=created_files,
            files_modified=created_directories
        )

    def _handle_general_file_operations(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """Handle general file management tasks"""
        # Parse task description for file operations
        operations = self._parse_file_operations(task_input.description)

        if not operations:
            return TaskResult(
                success=False,
                message="Could not determine file operations from task description",
                data={'parsed_description': task_input.description}
            )

        executed_operations = []
        failed_operations = []

        for operation in operations:
            try:
                result = self._execute_file_operation(operation)
                if result.get('success'):
                    executed_operations.append(operation)
                else:
                    failed_operations.append(f"{operation}: {result.get('error')}")
            except Exception as e:
                failed_operations.append(f"{operation}: {str(e)}")

        return TaskResult(
            success=len(failed_operations) == 0,
            message=f"Executed {len(executed_operations)} operations, {len(failed_operations)} failed",
            data={'executed_operations': executed_operations, 'failed_operations': failed_operations}
        )

    def _organize_directory_structure(self, directory: Path, task_input: TaskInput) -> Dict:
        """Organize directory structure according to best practices"""
        # Simple file type organization
        if not directory.exists():
            return {'operations': []}

        operations = []

        # Group files by type
        file_types = {}
        for file_path in directory.iterdir():
            if file_path.is_file():
                file_type = file_path.suffix.lower() or 'no_extension'
                if file_type not in file_types:
                    file_types[file_type] = []
                file_types[file_type].append(file_path)

        # Create directories for each file type (if multiple files of same type)
        for file_type, files in file_types.items():
            if len(files) > 1:  # Only create directories for multiple files
                type_dir = directory / file_type
                if not type_dir.exists():
                    type_dir.mkdir(parents=True, exist_ok=True)
                    operations.append(f"Created directory: {type_dir}")

                # Move files to type directory
                for file_path in files:
                    if file_path.parent != type_dir:
                        new_path = type_dir / file_path.name
                        try:
                            shutil.move(str(file_path), str(new_path))
                            operations.append(f"Moved {file_path.name} to {type_dir}")
                        except Exception as e:
                            operations.append(f"Failed to move {file_path.name}: {e}")

        return {'operations': operations}

    def _scaffold_directory_structure(self, directory: Path, task_input: TaskInput, context: Dict) -> Dict:
        """Scaffold directory structure based on framework or template"""
        operations = []

        # Detect framework from context or task description
        framework = self._detect_project_framework(task_input, context)

        # Get framework-specific structure
        structure = self._get_project_structure(framework)

        # Create directories
        for dir_name in structure.get('directories', []):
            dir_path = directory / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                operations.append(f"Created directory: {dir_path}")

        return {'operations': operations}

    def _process_single_file(self, file_path: Path, task_input: TaskInput, context: Dict) -> Dict:
        """Process a single file based on task description"""
        # Determine what to do with the file
        desc_lower = task_input.description.lower() if isinstance(task_input.description, str) else ""
        if 'backup' in desc_lower:
            return self._backup_file(file_path)
        elif 'analyze' in desc_lower:
            return self._analyze_file_content(file_path)
        elif 'format' in desc_lower:
            return self._format_file(file_path)
        else:
            return {'success': True, 'message': f'Processed {file_path}'}

    # Utility methods
    def _detect_operation_type(self, description: str) -> str:
        """Detect the type of file operation from description"""
        description_lower = description.lower() if isinstance(description, str) else ""

        if any(keyword in description_lower for keyword in ['create', 'new', 'generate']):
            return 'create'
        elif any(keyword in description_lower for keyword in ['modify', 'edit', 'update', 'change']):
            return 'modify'
        elif any(keyword in description_lower for keyword in ['delete', 'remove']):
            return 'delete'
        elif any(keyword in description_lower for keyword in ['copy', 'duplicate']):
            return 'copy'
        elif any(keyword in description_lower for keyword in ['move', 'relocate']):
            return 'move'
        else:
            return 'analyze'

    def _extract_project_name(self, description: str) -> str:
        """Extract project name from task description"""
        # Simple extraction - look for common patterns
        words = description.split() if isinstance(description, str) else []

        # Look for patterns like "create project X" or "new X project"
        for i, word in enumerate(words):
            if word.lower() in ['project', 'app', 'application'] and i > 0:
                return words[i-1]
            elif word.lower() in ['create', 'new'] and i < len(words) - 1:
                next_word = words[i+1]
                if next_word.lower() not in ['project', 'app', 'application']:
                    return next_word

        return 'new_project'

    def _detect_project_framework(self, task_input: TaskInput, context: Dict) -> str:
        """Detect project framework from task and context"""
        # Prefer explicit framework in data
        if isinstance(task_input.data, dict):
            fw = task_input.data.get('framework')
            if isinstance(fw, str) and fw:
                return fw.lower()

        # If description is a dict with tools/steps, infer from that
        if isinstance(task_input.description, dict):
            desc_dict = task_input.description
            tools = desc_dict.get('tools', []) if isinstance(desc_dict.get('tools', []), list) else []
            joined = " ".join(tools).lower()
            if 'create-react-app' in joined or 'react' in joined:
                return 'react'
            if 'vue' in joined:
                return 'vue'
            if 'angular' in joined:
                return 'angular'
            if 'flask' in joined or 'python' in joined:
                return 'flask'
            if 'django' in joined:
                return 'django'
            if 'express' in joined or 'node' in joined:
                return 'express'

        description = task_input.description.lower() if isinstance(task_input.description, str) else ""

        # Check for explicit framework mentions
        if 'react' in description:
            return 'react'
        elif 'vue' in description:
            return 'vue'
        elif 'angular' in description:
            return 'angular'
        elif 'flask' in description or 'python' in description:
            return 'flask'
        elif 'django' in description:
            return 'django'
        elif 'express' in description or 'node' in description:
            return 'express'

        # Use framework detector if available
        if context:
            return FrameworkDetector.detect_framework(context)

        return 'generic'

    def _get_project_structure(self, framework: str) -> Dict:
        """Get project structure for given framework"""
        structures = {
            'react': {
                'directories': ['src', 'src/components', 'src/hooks', 'src/utils', 'public', 'tests'],
                'files': [
                    {'name': 'package.json', 'content': '{\n  "name": "react-app",\n  "version": "1.0.0"\n}'},
                    {'name': 'README.md', 'content': '# React Application\n\nA new React project.'},
                    {'name': 'src/App.js', 'generate_content': True}
                ]
            },
            'flask': {
                'directories': ['app', 'tests', 'app/templates', 'app/static'],
                'files': [
        {'name': 'requirements.txt', 'content': 'Flask==2.3.2\n'},
                    {'name': 'README.md', 'content': '# Flask Application\n\nA new Flask project.'},
                    {'name': 'app/__init__.py', 'generate_content': True},
                    {'name': 'app/routes.py', 'generate_content': True}
                ]
            },
            'generic': {
                'directories': ['src', 'tests', 'docs'],
                'files': [
                    {'name': 'README.md', 'content': '# New Project\n\nProject description here.'}
                ]
            }
        }

        return structures.get(framework, structures['generic'])

    def _parse_file_operations(self, description: str) -> List[str]:
        """Parse file operations from task description"""
        # Simple parsing - could be enhanced with NLP
        operations = []

        desc_lower = description.lower() if isinstance(description, str) else ""
        if 'organize' in desc_lower:
            operations.append('organize_files')
        if 'backup' in desc_lower:
            operations.append('backup_files')
        if 'cleanup' in desc_lower:
            operations.append('cleanup_files')

        return operations

    def _execute_file_operation(self, operation: str) -> Dict:
        """Execute a specific file operation"""
        # Placeholder implementation
        return {'success': True, 'message': f'Executed operation: {operation}'}

    def _create_file_with_content(self, file_path: Path, task_input: TaskInput, context: Dict) -> TaskResult:
        """Create a new file with content"""
        # Generate content using AI if no content provided
        content = ""
        if task_input.text_inputs:
            content = "\n".join(task_input.text_inputs)
        else:
            # Use AI to generate content
            ai_result = self._generate_file_content(file_path, task_input, context)
            if ai_result.get('success'):
                content = ai_result.get('response', '')

        success = self.write_file(file_path, content)

        return TaskResult(
            success=success,
            message=f"Created file: {file_path}" if success else f"Failed to create file: {file_path}",
            files_created=[str(file_path)] if success else []
        )

    def _generate_file_content(self, file_path: Path, task_input: TaskInput, context: Dict) -> Dict[str, Any]:
        """Generate file content using AI"""
        prompt = self.create_ai_prompt(task_input, context, f"GENERATE_FILE_CONTENT:{file_path.suffix}")
        return self.execute_ai_operation(prompt)

    def _modify_file_content(self, file_path: Path, task_input: TaskInput, context: Dict) -> TaskResult:
        """Modify existing file content"""
        if not file_path.exists():
            return TaskResult(success=False, message=f"File does not exist: {file_path}")

        # Read current content
        current_content = self.read_file(file_path)
        if current_content is None:
            return TaskResult(success=False, message=f"Could not read file: {file_path}")

        # Use AI to modify content
        prompt = f"""
        MODIFY FILE CONTENT

        Current file: {file_path}
        Current content:
        {current_content}

        Modification request:
        {task_input.description}

        Provide the complete modified file content.
        """

        ai_result = self.execute_ai_operation(prompt)
        if ai_result.get('success'):
            new_content = ai_result.get('response', '')
            success = self.write_file(file_path, new_content)

            return TaskResult(
                success=success,
                message=f"Modified file: {file_path}" if success else f"Failed to modify file: {file_path}",
                files_modified=[str(file_path)] if success else []
            )
        else:
            return TaskResult(success=False, message=f"AI failed to generate modifications: {ai_result.get('error')}")

    def _delete_file(self, file_path: Path) -> TaskResult:
        """Delete a file"""
        try:
            if file_path.exists():
                file_path.unlink()
                return TaskResult(success=True, message=f"Deleted file: {file_path}")
            else:
                return TaskResult(success=False, message=f"File does not exist: {file_path}")
        except Exception as e:
            return TaskResult(success=False, message=f"Failed to delete file {file_path}: {e}")

    def _copy_file(self, file_path: Path, task_input: TaskInput) -> TaskResult:
        """Copy a file"""
        if not file_path.exists():
            return TaskResult(success=False, message=f"Source file does not exist: {file_path}")

        # Determine destination from task input or generate default
        if task_input.target_directory:
            dest_path = Path(task_input.target_directory) / file_path.name
        else:
            dest_path = file_path.parent / f"{file_path.stem}_copy{file_path.suffix}"

        try:
            shutil.copy2(str(file_path), str(dest_path))
            return TaskResult(
                success=True,
                message=f"Copied {file_path} to {dest_path}",
                files_created=[str(dest_path)]
            )
        except Exception as e:
            return TaskResult(success=False, message=f"Failed to copy file: {e}")

    def _move_file(self, file_path: Path, task_input: TaskInput) -> TaskResult:
        """Move a file"""
        if not file_path.exists():
            return TaskResult(success=False, message=f"Source file does not exist: {file_path}")

        # Determine destination
        if task_input.target_directory:
            dest_path = Path(task_input.target_directory) / file_path.name
        else:
            return TaskResult(success=False, message="No target directory specified for move operation")

        try:
            shutil.move(str(file_path), str(dest_path))
            return TaskResult(
                success=True,
                message=f"Moved {file_path} to {dest_path}",
                files_modified=[str(dest_path)]
            )
        except Exception as e:
            return TaskResult(success=False, message=f"Failed to move file: {e}")

    def _analyze_file(self, file_path: Path, task_input: TaskInput, context: Dict) -> TaskResult:
        """Analyze a file and provide information"""
        if not file_path.exists():
            return TaskResult(success=False, message=f"File does not exist: {file_path}")

        file_info = {
            'path': str(file_path),
            'size': file_path.stat().st_size,
            'extension': file_path.suffix,
            'exists': True
        }

        # Try to read content if it's a text file
        content = self.read_file(file_path)
        if content is not None:
            file_info['lines'] = len(content.split('\n'))
            file_info['characters'] = len(content)
            file_info['is_text'] = True
        else:
            file_info['is_text'] = False

        return TaskResult(
            success=True,
            message=f"File analysis completed for {file_path}",
            data=file_info
        )

    # Helper methods for file operations
    def _backup_file(self, file_path: Path) -> Dict:
        """Create backup of a file"""
        if not file_path.exists():
            return {'success': False, 'error': 'File does not exist'}

        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
        try:
            shutil.copy2(str(file_path), str(backup_path))
            return {'success': True, 'backup_path': str(backup_path)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _analyze_file_content(self, file_path: Path) -> Dict:
        """Analyze file content"""
        content = self.read_file(file_path)
        if content is None:
            return {'success': False, 'error': 'Could not read file'}

        return {
            'success': True,
            'lines': len(content.split('\n')),
            'characters': len(content),
            'size_bytes': len(content.encode('utf-8'))
        }

    def _format_file(self, file_path: Path) -> Dict:
        """Format a file (placeholder)"""
        return {'success': True, 'message': f'Formatted {file_path}'}

    # ========== NEW: AI-POWERED PROJECT CREATION METHODS ==========
    
    def _ai_analyze_project_requirements(self, description: str, context: Dict) -> Dict:
        """
        Use AI to analyze project requirements and generate a complete project plan
        """
        colored_print(f"   AI: Asking AI to analyze project requirements...", Colors.CYAN)
        
        prompt = f"""Analyze this project request and create a COMPLETE project plan:

PROJECT REQUEST: {description}

You must provide a JSON response with the following structure:
{{
    "framework": "react|vue|angular|flask|django|express|nextjs|etc",
    "project_type": "web|mobile|api|desktop|cli|library",
    "components": [
        {{"name": "ComponentName", "type": "component|page|service|util", "description": "what it does"}}
    ],
    "directory_structure": [
        "src/",
        "src/components/",
        "src/pages/",
        "src/utils/",
        "src/hooks/",
        "src/services/",
        "public/",
        "tests/",
        "config/"
    ],
    "files": [
        {{
            "path": "package.json",
            "type": "config",
            "description": "Project dependencies and scripts",
            "needs_ai_generation": true,
            "template_content": "{{}}"
        }},
        {{
            "path": "src/App.js",
            "type": "component",
            "description": "Main application component",
            "needs_ai_generation": true
        }}
    ],
    "dependencies": ["react", "react-dom", "etc"],
    "best_practices": ["use hooks", "typescript recommended", "etc"]
}}

IMPORTANT:
- Include ALL files needed for a complete, working project
- Include package.json/requirements.txt with ALL dependencies
- Include configuration files (.gitignore, .env.example, tsconfig.json if TypeScript)
- Include src/index.js or equivalent entry point
- Include at least 3-5 components based on the description
- Include test files
- Include README template structure
- Be comprehensive - this should be a production-ready structure

Return ONLY valid JSON, no markdown or explanations."""

        ai_result = self.execute_ai_operation(prompt)
        
        if not ai_result.get('success'):
            return {'success': False, 'error': 'AI unavailable'}
        
        # Parse AI response
        try:
            import re
            response = ai_result.get('response', '')
            
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            else:
                # Try to find JSON object
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    response = json_match.group(0)
            
            project_plan = json.loads(response)
            colored_print(f"   PARSED: Parsed project plan successfully", Colors.GREEN)
            
            return {
                'success': True,
                'project_plan': project_plan
            }
        except json.JSONDecodeError as e:
            colored_print(f"   WARNING: Failed to parse AI response as JSON: {e}", Colors.YELLOW)
            return {'success': False, 'error': f'JSON parse error: {e}'}
    
    def _ai_generate_file_content(self, file_path: Path, file_description: str, 
                                   project_context: Dict, context: Dict) -> Dict:
        """
        Use AI to generate complete, working content for a specific file
        """
        framework = project_context.get('framework', 'unknown')
        project_desc = project_context.get('project_description', '')
        all_files = project_context.get('all_files', [])
        
        # Determine file type and language
        extension = file_path.suffix
        language_map = {
            '.js': 'JavaScript',
            '.jsx': 'JavaScript React JSX',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript React TSX',
            '.py': 'Python',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.html': 'HTML',
            '.json': 'JSON',
            '.md': 'Markdown',
            '.yaml': 'YAML',
            '.yml': 'YAML'
        }
        language = language_map.get(extension, 'text')
        
        prompt = f"""Generate COMPLETE, WORKING code for this file in a {framework} project:

FILE: {file_path.name}
LANGUAGE: {language}
PURPOSE: {file_description}

PROJECT CONTEXT:
- Framework: {framework}
- Project: {project_desc}
- Related files: {', '.join(all_files[:10])}

REQUIREMENTS:
1. Generate COMPLETE, PRODUCTION-READY code (no placeholders or TODOs)
2. Include ALL necessary imports
3. Follow {framework} best practices
4. Include proper error handling
5. Add helpful comments
6. Make it fully functional
7. For config files (package.json, etc), include ALL necessary dependencies

For React components: Include state, hooks, props, styling
For package.json: Include ALL dependencies, scripts (dev, build, test, start)
For Python files: Include docstrings, type hints
For configuration: Include all common settings

Return ONLY the file content, no explanations or markdown blocks."""

        ai_result = self.execute_ai_operation(prompt)
        
        if not ai_result.get('success'):
            return {'success': False, 'error': 'AI unavailable'}
        
        content = ai_result.get('response', '')
        
        # Clean up markdown code blocks if present
        import re
        code_block_match = re.search(r'```(?:\w+)?\s*(.*?)\s*```', content, re.DOTALL)
        if code_block_match:
            content = code_block_match.group(1)
        
        return {
            'success': True,
            'content': content
        }
    
    def _ai_generate_readme(self, project_plan: Dict, description: str) -> str:
        """Generate a comprehensive README using AI"""
        framework = project_plan.get('framework', 'unknown')
        components = project_plan.get('components', [])
        dependencies = project_plan.get('dependencies', [])
        
        prompt = f"""Generate a comprehensive README.md for this project:

PROJECT: {description}
FRAMEWORK: {framework}
COMPONENTS: {len(components)} components
DEPENDENCIES: {', '.join(dependencies[:10])}

Include:
1. Project title and description
2. Features list
3. Installation instructions
4. Usage examples
5. Project structure
6. Available scripts
7. Technologies used
8. Contributing guidelines

Make it professional and comprehensive. Return ONLY the markdown content."""

        ai_result = self.execute_ai_operation(prompt)
        
        if ai_result.get('success'):
            content = ai_result.get('response', '')
            import re
            code_block_match = re.search(r'```(?:markdown|md)?\s*(.*?)\s*```', content, re.DOTALL)
            if code_block_match:
                content = code_block_match.group(1)
            return content
        
        # Fallback template
        return f"""# {project_plan.get('framework', 'Project').title()} Project

{description}

## Features

- Built with {framework}
- {len(components)} components
- Modern best practices

## Installation

```bash
npm install  # or pip install -r requirements.txt
```

## Usage

```bash
npm start  # or python app.py
```

## Project Structure

See the project files for the complete structure.

## Technologies

- {framework}
- {', '.join(dependencies[:5])}

## License

MIT
"""
    
    def _fallback_project_creation(self, project_dir: Path, task_input: TaskInput, context: Dict) -> TaskResult:
        """
        Fallback project creation when AI is unavailable - uses heuristic approach
        """
        colored_print(f"   FALLBACK: Using heuristic project creation", Colors.YELLOW)
        
        # Detect framework from description
        framework = self._detect_project_framework(task_input, context)
        
        created_files = []
        created_directories = []
        
        # Create basic project structure based on framework
        structure = self._get_project_structure(framework)
        
        for dir_name in structure.get('directories', []):
            dir_path = project_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            created_directories.append(str(dir_path))
        
        # Create basic files
        for file_info in structure.get('files', []):
            file_path = project_dir / file_info['name']
            content = file_info.get('content', '')
            
            # Generate content using AI if needed
            if file_info.get('generate_content'):
                ai_result = self._generate_file_content(file_path, task_input, context)
                if ai_result.get('success'):
                    content = ai_result.get('response', content)
            
            self.write_file(file_path, content)
            created_files.append(str(file_path))
        
        return TaskResult(
            success=True,
            message=f"Project scaffolding completed for {framework} project (heuristic mode)",
            data={
                'framework': framework,
                'project_directory': str(project_dir),
                'structure': structure,
                'ai_powered': False
            },
            files_created=created_files,
            files_modified=created_directories
        )
    
    # ========== NEW: SMART AI INSTRUCTION PARSING ==========
    
    def _is_enhanced_ai_description(self, description: Union[str, Dict]) -> bool:
        """Check if description contains AI-enhanced structured instructions"""
        if not isinstance(description, str):
            return False
        # Look for patterns that indicate AI-enhanced instructions
        indicators = [
            'Step 1:', 'Step 2:', '$ mkdir', '$ npx', '$ npm',
            'Create a new file', 'add the following code:',
            'Update package.json', 'Open package.json'
        ]
        return any(indicator in description for indicator in indicators)
    
    def _handle_enhanced_ai_instructions(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """
        Parse and execute AI-enhanced instructions intelligently
        
        This method:
        1. Extracts file creation instructions
        2. Extracts code blocks
        3. Executes commands if safe
        4. Creates all necessary files
        """
        colored_print(f"   Parsing enhanced instructions...", Colors.CYAN)
        
        # Get project directory
        if 'project_workspace' in task_input.data:
            project_dir = Path(task_input.data['project_workspace'])
        elif task_input.target_directory:
            project_dir = Path(task_input.target_directory)
        else:
            project_name = task_input.data.get('project_name') or self._extract_project_name(task_input.description)
            project_dir = self.workspace_dir / project_name
        
        colored_print(f"   Target: {project_dir}", Colors.CYAN)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Parse the instructions
        parsed_data = self._parse_ai_instructions(task_input.description)
        
        colored_print(f"   Found: {len(parsed_data['files'])} files to create", Colors.GREEN)
        colored_print(f"   Found: {len(parsed_data['commands'])} commands (review only)", Colors.YELLOW)
        
        created_files = []
        
        # Create all files
        for file_info in parsed_data['files']:
            file_path = project_dir / file_info['path']
            colored_print(f"      Creating: {file_info['path']}", Colors.CYAN)
            
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            self.write_file(file_path, file_info['content'])
            created_files.append(str(file_path))
            colored_print(f"         DONE: {file_info['path']}", Colors.GREEN)
        
        # Show commands for user to run manually
        if parsed_data['commands']:
            colored_print(f"\n   COMMANDS TO RUN:", Colors.BRIGHT_YELLOW)
            for cmd in parsed_data['commands']:
                colored_print(f"      $ {cmd}", Colors.YELLOW)
            colored_print(f"   Note: Run these commands manually in the project directory", Colors.CYAN)
        
        return TaskResult(
            success=True,
            message=f"Created {len(created_files)} files from AI instructions",
            data={
                'files_created': created_files,
                'commands_suggested': parsed_data['commands'],
                'project_directory': str(project_dir)
            },
            files_created=created_files
        )
    
    def _parse_ai_instructions(self, description: str) -> Dict:
        """
        Parse AI-enhanced instructions to extract files and commands
        
        Returns:
            {
                'files': [{'path': 'src/App.js', 'content': '...'}],
                'commands': ['npm install', 'npm start']
            }
        """
        import re
        
        files = []
        commands = []
        
        lines = description.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Detect file creation patterns
            # Pattern: "Create a new file PATH and add the following code:"
            file_match = re.match(r'Create a new file\s+([^\s]+)\s+and add the following code:', line)
            if file_match:
                file_path = file_match.group(1)
                i += 1
                
                # Extract code block
                code_lines = []
                in_code_block = False
                
                while i < len(lines):
                    current_line = lines[i]
                    
                    # Start of code block (might have language marker)
                    if current_line.strip().startswith('```') and not in_code_block:
                        in_code_block = True
                        i += 1
                        continue
                    
                    # End of code block
                    if current_line.strip() == '```' and in_code_block:
                        break
                    
                    # Check if we hit next step or instruction
                    if re.match(r'(Step \d+:|Create a new file|Update |Open )', current_line.strip()) and not in_code_block:
                        i -= 1  # Go back one line
                        break
                    
                    if in_code_block or (not in_code_block and current_line.strip() and not current_line.strip().startswith('$')):
                        code_lines.append(current_line.rstrip())
                    
                    i += 1
                
                if code_lines:
                    files.append({
                        'path': file_path,
                        'content': '\n'.join(code_lines)
                    })
            
            # Pattern: "Open/Update package.json and update/add..."
            update_match = re.match(r'(Open|Update)\s+([^\s]+)\s+and (update|add)', line)
            if update_match:
                file_path = update_match.group(2)
                i += 1
                
                # Extract JSON or code block
                code_lines = []
                in_code_block = False
                
                while i < len(lines):
                    current_line = lines[i]
                    
                    if current_line.strip().startswith('{') and not in_code_block:
                        in_code_block = True
                    
                    if in_code_block:
                        code_lines.append(current_line.rstrip())
                        if current_line.strip().startswith('}') and current_line.strip().endswith('}'):
                            break
                    
                    if re.match(r'(Step \d+:|Create |Update |Open )', current_line.strip()) and not in_code_block:
                        i -= 1
                        break
                    
                    i += 1
                
                if code_lines:
                    files.append({
                        'path': file_path,
                        'content': '\n'.join(code_lines)
                    })
            
            # Extract commands ($ prefix)
            if line.startswith('$'):
                cmd = line[1:].strip()
                # Filter out dangerous commands
                if not any(dangerous in cmd for dangerous in ['rm -rf', 'sudo', 'chmod 777']):
                    commands.append(cmd)
            
            i += 1
        
        return {
            'files': files,
            'commands': commands
        }
    
    # ========== FILE MANAGER's OWN AI ENRICHMENT ==========
    
    def _extract_enhanced_description_from_json(self, task_input: TaskInput) -> Optional[TaskInput]:
        """
        Check if description is a JSON-formatted enrichment and extract the actual description
        """
        if not isinstance(task_input.description, str):
            return None
        description = task_input.description.strip()
        
        # Check if it starts with JSON-like structure
        if not (description.startswith('{') or description.startswith('"enhanced_description"')):
            return None
        
        try:
            import json
            import re
            
            # Try to extract JSON object
            # Clean up backticks and other formatting
            cleaned = description
            if '```' in cleaned:
                cleaned = re.sub(r'```json?\s*', '', cleaned)
                cleaned = re.sub(r'```', '', cleaned)
            
            # Try to find the first complete JSON object
            brace_count = 0
            start = cleaned.find('{')
            if start == -1:
                return None
            
            end = start
            for i in range(start, len(cleaned)):
                if cleaned[i] == '{':
                    brace_count += 1
                elif cleaned[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            
            json_str = cleaned[start:end]
            enrichment_data = json.loads(json_str)
            
            # Extract the enhanced_description
            if 'enhanced_description' in enrichment_data:
                enhanced_desc = enrichment_data['enhanced_description']
                colored_print(f"   EXTRACTED: Found enhanced description from JSON", Colors.GREEN)
                
                # Create new TaskInput with cleaned description
                new_task_input = TaskInput(
                    description=enhanced_desc,
                    files=task_input.files,
                    directories=task_input.directories,
                    target_file=task_input.target_file,
                    target_directory=task_input.target_directory,
                    text_inputs=task_input.text_inputs,
                    metadata=task_input.metadata,
                    data=task_input.data
                )
                
                # Also merge in task_data if present
                if 'task_data' in enrichment_data and isinstance(enrichment_data['task_data'], dict):
                    new_task_input.data.update(enrichment_data['task_data'])
                
                return new_task_input
        
        except (json.JSONDecodeError, Exception) as e:
            colored_print(f"   INFO: Not JSON-formatted enrichment: {str(e)[:50]}", Colors.CYAN)
            return None
        
        return None
    
    def _should_enrich_task(self, description: Union[str, Dict]) -> bool:
        """
        Determine if task should be enriched by file manager's AI before execution
        """
        # Check for project creation indicators
        project_keywords = ['create', 'build', 'setup', 'initialize', 'scaffold']
        framework_keywords = ['react', 'vue', 'angular', 'flask', 'django', 'express', 'next']
        if isinstance(description, dict):
            # If it's already structured, no enrichment needed here
            return False

        desc_lower = description.lower() if isinstance(description, str) else ""
        
        # If it contains project creation keywords AND framework keywords
        has_project = any(keyword in desc_lower for keyword in project_keywords)
        has_framework = any(keyword in desc_lower for keyword in framework_keywords)
        
        # Don't enrich if already enriched (has structured instructions)
        already_enriched = self._is_enhanced_ai_description(description)
        
        return has_project and has_framework and not already_enriched
    
    def _enrich_and_execute_task(self, task_input: TaskInput, context: Dict) -> Optional[TaskResult]:
        """
        File Manager enriches the task using its own AI analysis, then executes
        """
        try:
            # Get project directory
            if 'project_workspace' in task_input.data:
                project_dir = Path(task_input.data['project_workspace'])
            elif task_input.target_directory:
                project_dir = Path(task_input.target_directory)
            else:
                project_name = task_input.data.get('project_name') or self._extract_project_name(task_input.description)
                project_dir = self.workspace_dir / project_name
            
            colored_print(f"   Analyzing project requirements with AI...", Colors.CYAN)
            
            # Use the existing AI-powered project scaffolding
            # This already has the _ai_analyze_project_requirements method
            return self._handle_project_scaffolding(task_input, context)
            
        except Exception as e:
            colored_print(f"   AI enrichment failed: {e}", Colors.YELLOW)
            colored_print(f"   Falling back to standard processing", Colors.YELLOW)
            return None

    # ========== NEW: STRUCTURED JSON HANDLER ==========

    def _handle_structured_enrichment_dict(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """
        Handle a structured dict description from coordinator/AI containing steps/tools/project_structure/files.
        Creates directories and key files (with AI where appropriate) and suggests commands.
        """
        desc_dict = task_input.description if isinstance(task_input.description, dict) else {}

        # Determine project directory
        if 'project_workspace' in task_input.data:
            project_dir = Path(task_input.data['project_workspace'])
        elif task_input.target_directory:
            project_dir = Path(task_input.target_directory)
        else:
            project_name = task_input.data.get('project_name') or 'new_project'
            project_dir = self.workspace_dir / project_name

        project_dir.mkdir(parents=True, exist_ok=True)

        # Infer framework
        framework = (desc_dict.get('framework') or '').lower() if isinstance(desc_dict.get('framework'), str) else None
        if not framework:
            tools = desc_dict.get('tools', []) if isinstance(desc_dict.get('tools', []), list) else []
            joined = " ".join(tools).lower()
            if 'create-react-app' in joined or 'react' in joined:
                framework = 'react'
            elif 'vue' in joined:
                framework = 'vue'
            elif 'angular' in joined:
                framework = 'angular'
            elif 'flask' in joined or 'python' in joined:
                framework = 'flask'
            elif 'django' in joined:
                framework = 'django'
            elif 'express' in joined or 'node' in joined:
                framework = 'express'
            else:
                framework = 'generic'

        created_files: List[str] = []
        created_directories: List[str] = []

        # Create directory structure from project_structure
        structure = desc_dict.get('project_structure')
        if isinstance(structure, dict):
            def create_structure(base: Path, tree: Dict):
                for name, subtree in tree.items():
                    dir_path = base / name
                    dir_path.mkdir(parents=True, exist_ok=True)
                    created_directories.append(str(dir_path))
                    if isinstance(subtree, dict):
                        create_structure(dir_path, subtree)
                    # If subtree is a str (file content placeholder), create file
                    elif isinstance(subtree, str) and subtree != "":
                        file_path = dir_path
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        self.write_file(file_path, subtree)
                        created_files.append(str(file_path))

            create_structure(project_dir, structure)

        # Create listed files (generate content with AI for key files)
        files = desc_dict.get('files', [])
        if isinstance(files, list):
            key_files = {"package.json", "src/App.js", "src/index.js", "public/index.html", "README.md"}
            for rel in files:
                if not isinstance(rel, str):
                    continue
                file_path = project_dir / rel
                file_path.parent.mkdir(parents=True, exist_ok=True)
                content = ""
                try:
                    if rel in key_files:
                        gen = self._ai_generate_file_content(
                            file_path=file_path,
                            file_description=f"Generate a complete {rel} for a {framework} project.",
                            project_context={
                                'framework': framework,
                                'project_description': str(task_input.description),
                                'all_files': files
                            },
                            context=context
                        )
                        if gen.get('success'):
                            content = gen.get('content', '')
                    # Fallback placeholder
                    if not content:
                        if rel.endswith('.json'):
                            content = "{}\n"
                        elif rel.endswith('.js'):
                            content = "// TODO: implement\n"
                        elif rel.endswith('.html'):
                            content = "<!doctype html>\n<html><head><meta charset=\"utf-8\"></head><body><div id=\"root\"></div></body></html>\n"
                        elif rel.endswith('.css'):
                            content = "/* styles */\n"
                        else:
                            content = ""
                except Exception:
                    content = content or ""

                self.write_file(file_path, content)
                created_files.append(str(file_path))

        # Collect commands from steps/tools
        commands: List[str] = []
        steps = desc_dict.get('steps', []) if isinstance(desc_dict.get('steps', []), list) else []
        for step in steps:
            if not isinstance(step, str):
                continue
            s = step.strip()
            if s.startswith('$'):
                s = s[1:].strip()
            if s.lower().startswith('run '):
                s = s[4:].strip()
            # Heuristic: include NPX/NPM/PIP commands
            if any(s.lower().startswith(prefix) for prefix in ['npx ', 'npm ', 'yarn ', 'pnpm ', 'pip ', 'pip3 '] ):
                commands.append(s)

        return TaskResult(
            success=True,
            message=f"Structured plan applied for {framework} project",
            data={
                'framework': framework,
                'project_directory': str(project_dir),
                'commands_suggested': commands
            },
            files_created=created_files,
            files_modified=created_directories
        )
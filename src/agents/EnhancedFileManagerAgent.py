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
        if task_input.has_directories():
            return self._handle_directory_operations(task_input, context)
        elif task_input.has_files() and not task_input.target_file:
            return self._handle_batch_file_operations(task_input, context)
        elif task_input.target_file:
            return self._handle_single_file_operations(task_input, context)
        elif 'project' in task_input.description.lower() or 'scaffold' in task_input.description.lower():
            return self._handle_project_scaffolding(task_input, context)
        else:
            return self._handle_general_file_operations(task_input, context)

    def _handle_directory_operations(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """Handle directory-level file operations"""
        target_dir = task_input.target_directory or self.workspace_dir
        target_dir = Path(target_dir)

        operations_performed = []

        # Create directory if it doesn't exist
        if 'create' in task_input.description.lower():
            target_dir.mkdir(parents=True, exist_ok=True)
            operations_performed.append(f"Created directory: {target_dir}")

        # Organize existing files
        if 'organize' in task_input.description.lower():
            result = self._organize_directory_structure(target_dir, task_input)
            operations_performed.extend(result.get('operations', []))

        if any(keyword in task_input.description.lower() for keyword in ['scaffold', 'template', 'init']):
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
        """Handle project scaffolding and template application"""
        colored_print(f"Project scaffolding", Colors.BRIGHT_CYAN)

        # Determine project directory
        if task_input.target_directory:
            project_dir = Path(task_input.target_directory)
        else:
            # Extract project name from description
            project_name = self._extract_project_name(task_input.description)
            project_dir = self.workspace_dir / project_name

        colored_print(f"Project directory: {project_dir}", Colors.CYAN)

        # Create project directory
        project_dir.mkdir(parents=True, exist_ok=True)

        # Detect framework and create structure
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
            message=f"Project scaffolding completed for {framework} project in {project_dir}",
            data={
                'framework': framework,
                'project_directory': str(project_dir),
                'structure': structure
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
        if 'backup' in task_input.description.lower():
            return self._backup_file(file_path)
        elif 'analyze' in task_input.description.lower():
            return self._analyze_file_content(file_path)
        elif 'format' in task_input.description.lower():
            return self._format_file(file_path)
        else:
            return {'success': True, 'message': f'Processed {file_path}'}

    # Utility methods
    def _detect_operation_type(self, description: str) -> str:
        """Detect the type of file operation from description"""
        description_lower = description.lower()

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
        words = description.split()

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
        description = task_input.description.lower()

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

        if 'organize' in description.lower():
            operations.append('organize_files')
        if 'backup' in description.lower():
            operations.append('backup_files')
        if 'cleanup' in description.lower():
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
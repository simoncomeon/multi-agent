"""
Base Agent Class - Framework-agnostic agent foundation with standardized interface
"""

import os
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from .models import AgentRole, TaskStatus, Colors
from .utils import colored_print, gather_file_context, gather_directory_context, gather_project_context
from .communication import AgentCommunication
from .ollama_client import ollama_client


class TaskInput:
    """Standardized task input container for flexible parameter handling"""

    def __init__(self, task_description: str, **kwargs):
        self.description = task_description
        self.task_type = kwargs.get('task_type', 'general')
        self.priority = kwargs.get('priority', 1)
        self.metadata = kwargs.get('metadata', {})

        # Input parameters (files, directories, text)
        self.files = self._normalize_paths(kwargs.get('files', []))
        self.directories = self._normalize_paths(kwargs.get('directories', []))
        self.text_inputs = kwargs.get('text_inputs', [])
        self.target_file = kwargs.get('target_file')
        self.target_directory = kwargs.get('target_directory')

        # Context and constraints
        self.context = kwargs.get('context', {})
        self.constraints = kwargs.get('constraints', [])
        self.requirements = kwargs.get('requirements', [])

        # AI-specific parameters
        self.ai_prompt_template = kwargs.get('ai_prompt_template')
        self.ai_model_preferences = kwargs.get('ai_model_preferences', {})

    def _normalize_paths(self, paths: List[Union[str, Path]]) -> List[Path]:
        """Normalize path inputs to Path objects"""
        return [Path(p) for p in paths]

    def has_files(self) -> bool:
        """Check if task has file inputs"""
        return len(self.files) > 0

    def has_directories(self) -> bool:
        """Check if task has directory inputs"""
        return len(self.directories) > 0

    def has_text_inputs(self) -> bool:
        """Check if task has text inputs"""
        return len(self.text_inputs) > 0

    def get_all_inputs(self) -> Dict[str, Any]:
        """Get all inputs as dictionary"""
        return {
            'files': [
                str(f) for f in self.files],
            'directories': [
                str(d) for d in self.directories],
            'text_inputs': self.text_inputs,
            'target_file': str(
                self.target_file) if self.target_file else None,
            'target_directory': str(
                self.target_directory) if self.target_directory else None}


class TaskResult:
    """Standardized task result container"""

    def __init__(self, success: bool, **kwargs):
        self.success = success
        self.message = kwargs.get('message', '')
        self.data = kwargs.get('data', {})
        self.files_created = kwargs.get('files_created', [])
        self.files_modified = kwargs.get('files_modified', [])
        self.output_content = kwargs.get('output_content', '')
        self.delegated_tasks = kwargs.get('delegated_tasks', [])
        self.metadata = kwargs.get('metadata', {})
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'files_created': self.files_created,
            'files_modified': self.files_modified,
            'output_content': self.output_content,
            'delegated_tasks': self.delegated_tasks,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }


class BaseAgent(ABC):
    """
    Framework-agnostic base agent class providing standardized interface,
    communication capabilities, and AI integration.
    """

    def __init__(
            self,
            agent_id: str,
            role: AgentRole,
            workspace_dir: str,
            **kwargs):
        self.agent_id = agent_id
        self.role = role
        self.workspace_dir = Path(workspace_dir)

        # Communication system
        self.comm = AgentCommunication(workspace_dir)

        # AI client integration
        self.ai_client = ollama_client
        self.default_model = kwargs.get('default_model', 'llama3.2')

        # Agent configuration
        self.capabilities = self._define_capabilities()
        self.supported_file_types = self._define_supported_file_types()
        self.framework_adapters = {}

        # Task execution settings
        self.max_context_size = kwargs.get('max_context_size', 50000)
        self.enable_ai_fallback = kwargs.get('enable_ai_fallback', True)

        # Register agent
        self.comm.register_agent(agent_id, role)

        colored_print(
            f"{self.__class__.__name__} '{agent_id}' initialized",
            Colors.BRIGHT_GREEN)

    @abstractmethod
    def _define_capabilities(self) -> Dict[str, bool]:
        """Define agent capabilities - must be implemented by subclasses"""
        pass

    def _define_supported_file_types(self) -> List[str]:
        """Define supported file types - can be overridden by subclasses"""
        return [
            '.py',
            '.js',
            '.ts',
            '.jsx',
            '.tsx',
            '.json',
            '.md',
            '.txt',
            '.yml',
            '.yaml']

    def can_handle_task(self, task_input: TaskInput) -> bool:
        """Check if agent can handle the given task"""
        # Check if any input files are supported
        if task_input.has_files():
            for file_path in task_input.files:
                if file_path.suffix not in self.supported_file_types:
                    return False

        # Check task type compatibility (can be overridden)
        return self._is_task_type_supported(task_input.task_type)

    def _is_task_type_supported(self, task_type: str) -> bool:
        """Check if task type is supported - can be overridden"""
        return True  # Base implementation accepts all task types

    def execute_task(self, task_input: TaskInput) -> TaskResult:
        """
        Main task execution entry point - standardized across all agents
        """
        # Log task execution
        colored_print(f"{self.agent_id}: Executing task", Colors.CYAN)
        colored_print(f" {task_input.description}", Colors.WHITE)

        try:
            # Pre-execution validation
            if not self.can_handle_task(task_input):
                return TaskResult(
                    success=False,
                    message=f"Agent {self.agent_id} cannot handle this task type or file types",
                    metadata={
                        'validation_failed': True})

            # Gather context from inputs
            context = self._gather_input_context(task_input)

            # Execute the specific task (implemented by subclasses)
            result = self._execute_specific_task(task_input, context)

            # Post-execution processing
            self._post_process_result(task_input, result)

            return result

        except Exception as e:
            colored_print(
                f" {self.agent_id}: Task execution failed: {e}",
                Colors.RED)
            return TaskResult(
                success=False,
                message=f"Task execution failed: {str(e)}",
                metadata={'exception': str(e)}
            )

    @abstractmethod
    def _execute_specific_task(
            self,
            task_input: TaskInput,
            context: Dict) -> TaskResult:
        """Execute the agent-specific task logic - must be implemented by subclasses"""
        pass

    def _gather_input_context(self, task_input: TaskInput) -> Dict[str, Any]:
        """Gather context from all input sources"""
        context = {
            'files': {},
            'directories': {},
            'text_inputs': task_input.text_inputs,
            'project_context': None,
            'total_size': 0
        }

        # Gather file contexts
        for file_path in task_input.files:
            file_context = gather_file_context(
                file_path, self.max_context_size)
            context['files'][str(file_path)] = file_context
            context['total_size'] += file_context.get('size', 0)

        # Gather directory contexts
        for dir_path in task_input.directories:
            dir_context = gather_directory_context(dir_path)
            context['directories'][str(dir_path)] = dir_context

        # Gather project context if in a project
        if hasattr(self, 'current_project') and self.current_project:
            context['project_context'] = gather_project_context(
                self.current_project)

        return context

    def _post_process_result(
            self,
            task_input: TaskInput,
            result: TaskResult) -> None:
        """Post-process task result - can be overridden"""
        if result.success:
            colored_print(
                f" {self.agent_id}: Task completed successfully",
                Colors.GREEN)
        else:
            colored_print(
                f" {self.agent_id}: Task completed with issues",
                Colors.YELLOW)

    def create_ai_prompt(
            self,
            task_input: TaskInput,
            context: Dict,
            operation_type: str = None) -> str:
        """
        Create AI prompt from task input and context - framework agnostic
        """
        # Use custom template if provided
        if task_input.ai_prompt_template:
            return self._apply_prompt_template(
                task_input.ai_prompt_template, task_input, context)

        # Build standardized prompt
        prompt_parts = [
            f"AGENT ROLE: {self.role.value.upper()}",
            f"OPERATION: {operation_type or 'GENERAL_TASK'}",
            "",
            f"TASK DESCRIPTION:",
            task_input.description,
            ""
        ]

        # Add context sections
        if context.get('project_context'):
            prompt_parts.extend([
                "PROJECT CONTEXT:",
                self._format_project_context(context['project_context']),
                ""
            ])

        if context.get('files'):
            prompt_parts.extend([
                "INPUT FILES:",
                self._format_files_context(context['files']),
                ""
            ])

        if context.get('directories'):
            prompt_parts.extend([
                "INPUT DIRECTORIES:",
                self._format_directories_context(context['directories']),
                ""
            ])

        if task_input.text_inputs:
            prompt_parts.extend([
                "TEXT INPUTS:",
                "\n".join(f"- {text}" for text in task_input.text_inputs),
                ""
            ])

        # Add requirements and constraints
        if task_input.requirements:
            prompt_parts.extend([
                "REQUIREMENTS:",
                "\n".join(f"- {req}" for req in task_input.requirements),
                ""
            ])

        if task_input.constraints:
            prompt_parts.extend(["CONSTRAINTS:", "\n".join(
                f"- {constraint}" for constraint in task_input.constraints), ""])

        # Add target information
        if task_input.target_file:
            prompt_parts.extend([
                f"TARGET FILE: {task_input.target_file}",
                ""
            ])

        if task_input.target_directory:
            prompt_parts.extend([
                f"TARGET DIRECTORY: {task_input.target_directory}",
                ""
            ])

        prompt_parts.extend([
            "INSTRUCTIONS:",
            "- Provide practical, executable solutions",
            "- Be framework-agnostic unless context indicates specific framework",
            "- Include proper error handling and validation",
            "- Follow best practices for the detected technology stack",
            "- Generate complete, working implementations",
            ""
        ])

        return "\n".join(prompt_parts)

    def _apply_prompt_template(
            self,
            template: str,
            task_input: TaskInput,
            context: Dict) -> str:
        """Apply custom prompt template with variable substitution"""
        variables = {
            'description': task_input.description,
            'files': list(context.get('files', {}).keys()),
            'directories': list(context.get('directories', {}).keys()),
            'target_file': task_input.target_file or '',
            'target_directory': task_input.target_directory or '',
            'agent_role': self.role.value
        }

        try:
            return template.format(**variables)
        except KeyError as e:
            colored_print(f" Template variable missing: {e}", Colors.YELLOW)
            return template

    def _format_project_context(self, project_context: Dict) -> str:
        """Format project context for AI prompt"""
        lines = [
            f"Project: {project_context.get('project_name', 'Unknown')}",
            f"Type: {project_context.get('project_type', 'unknown')}",
            f"Path: {project_context.get('project_path', '')}"
        ]

        if project_context.get('package_info'):
            pkg_info = project_context['package_info']
            if pkg_info.get('dependencies'):
                lines.append(
                    f"Dependencies: {', '.join(pkg_info['dependencies'][:5])}")

        return "\n".join(lines)

    def _format_files_context(self, files_context: Dict) -> str:
        """Format files context for AI prompt"""
        lines = []
        for file_path, file_data in files_context.items():
            if file_data.get('error'):
                lines.append(f"- {file_path}: {file_data['error']}")
            elif file_data.get('readable'):
                content = file_data.get('content', '')
                size_info = file_data.get('size_formatted', 'unknown size')
                lines.append(f"- {file_path} ({size_info})")
                if len(content) > 1000:
                    lines.append(
                        f" Content preview: {content[:1000]}...[truncated]")
                else:
                    lines.append(f" Content: {content}")
            else:
                lines.append(f"- {file_path}: Binary or unreadable file")
        return "\n".join(lines)

    def _format_directories_context(self, dirs_context: Dict) -> str:
        """Format directories context for AI prompt"""
        lines = []
        for dir_path, dir_data in dirs_context.items():
            if dir_data.get('error'):
                lines.append(f"- {dir_path}: {dir_data['error']}")
            else:
                file_count = dir_data.get('file_count', 0)
                lines.append(f"- {dir_path}: {file_count} files")
        return "\n".join(lines)

    def execute_ai_operation(
            self, prompt: str, model: str = None) -> Dict[str, Any]:
        """
        Execute AI operation with error handling and fallback
        """
        model = model or self.default_model

        if not self.ai_client.is_available():
            if self.enable_ai_fallback:
                return self._ai_fallback_response(prompt)
            else:
                return {
                    'success': False,
                    'error': 'AI client not available and fallback disabled',
                    'response': ''
                }

        try:
            colored_print(
                f" {self.agent_id}: Consulting AI model ({model})",
                Colors.MAGENTA)
            result = self.ai_client.generate(prompt, model)

            if result.get('success'):
                colored_print(f" AI operation completed", Colors.GREEN)
                return {
                    'success': True,
                    'response': result.get('response', ''),
                    'model_used': model
                }
            else:
                colored_print(
                    f" AI operation failed: {result.get('error')}",
                    Colors.RED)
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown AI error'),
                    'response': ''
                }

        except Exception as e:
            colored_print(f" AI operation exception: {e}", Colors.RED)
            return {
                'success': False,
                'error': f'AI operation exception: {str(e)}',
                'response': ''
            }

    def _ai_fallback_response(self, prompt: str) -> Dict[str, Any]:
        """Provide fallback response when AI is unavailable - can be overridden"""
        return {
            'success': False,
            'error': 'AI model unavailable - implement fallback logic in subclass',
            'response': 'This agent requires AI model integration for advanced operations.'
        }

    def delegate_task(
            self,
            task_description: str,
            target_agent_role: str,
            **kwargs) -> str:
        """Delegate task to another agent"""
        task_id = self.comm.create_task(
            task_type=kwargs.get('task_type', 'delegated'),
            description=task_description,
            assigned_to=target_agent_role,
            created_by=self.agent_id,
            priority=kwargs.get('priority', 1),
            data=kwargs.get('task_data', {})
        )

        colored_print(
            f" {self.agent_id}: Delegated task {task_id} → {target_agent_role}",
            Colors.YELLOW)
        return task_id

    def send_message(self, target_agent: str, message: str,
                     message_type: str = "info") -> None:
        """Send message to another agent"""
        self.comm.send_message(
            self.agent_id,
            target_agent,
            message,
            message_type)
        colored_print(
            f" {self.agent_id} → {target_agent}: {message}",
            Colors.CYAN)

    def write_file(self,
                   file_path: Union[str,
                                    Path],
                   content: str,
                   backup: bool = True) -> bool:
        """
        Write content to file with backup support
        """
        file_path = Path(file_path)

        try:
            # Create backup if requested and file exists
            if backup and file_path.exists():
                backup_path = file_path.with_suffix(
                    f"{file_path.suffix}.backup")
                file_path.rename(backup_path)
                colored_print(f" Created backup: {backup_path}", Colors.CYAN)

            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            colored_print(
                f" {self.agent_id}: Wrote file {file_path}",
                Colors.GREEN)
            return True

        except Exception as e:
            colored_print(
                f" Failed to write file {file_path}: {e}",
                Colors.RED)
            return False

    def read_file(self, file_path: Union[str, Path]) -> Optional[str]:
        """Read file content with error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            colored_print(f" Failed to read file {file_path}: {e}", Colors.RED)
            return None

    def get_active_agents(self) -> List[Dict]:
        """Get list of active agents in the system"""
        return self.comm.get_active_agents()

    def shutdown(self) -> None:
        """Shutdown agent gracefully"""
        self.comm.unregister_agent(self.agent_id)
        colored_print(f" {self.agent_id}: Agent shutdown complete", Colors.RED)


# Framework detection utilities
class FrameworkDetector:
    """Utility class for detecting project frameworks and adapting accordingly"""

    @staticmethod
    def detect_framework(context: Dict) -> str:
        """Detect framework from project context"""
        project_context = context.get('project_context', {})

        if not project_context:
            return 'unknown'

        project_type = project_context.get('project_type', 'unknown')
        package_info = project_context.get('package_info', {})

        # JavaScript/Node.js framework detection
        if project_type == 'javascript/node':
            deps = package_info.get('dependencies', [])
            if 'react' in deps:
                return 'react'
            elif 'vue' in deps:
                return 'vue'
            elif 'angular' in deps:
                return 'angular'
            elif 'express' in deps:
                return 'express'
            else:
                return 'javascript'

        # Python framework detection
        elif project_type == 'python':
            deps = package_info.get('dependencies', [])
            if any('flask' in dep.lower() for dep in deps):
                return 'flask'
            elif any('django' in dep.lower() for dep in deps):
                return 'django'
            elif any('fastapi' in dep.lower() for dep in deps):
                return 'fastapi'
            else:
                return 'python'

        return project_type

    @staticmethod
    def get_framework_conventions(framework: str) -> Dict[str, Any]:
        """Get framework-specific conventions and patterns"""
        conventions = {
            'react': {
                'file_extensions': ['.jsx', '.tsx', '.js', '.ts'],
                'component_naming': 'PascalCase',
                'directory_structure': ['src', 'components', 'hooks', 'utils'],
                'import_style': 'es6'
            },
            'vue': {
                'file_extensions': ['.vue', '.js', '.ts'],
                'component_naming': 'PascalCase',
                'directory_structure': ['src', 'components', 'views', 'store'],
                'import_style': 'es6'
            },
            'python': {
                'file_extensions': ['.py'],
                'naming_convention': 'snake_case',
                'directory_structure': ['src', 'tests', 'docs'],
                'import_style': 'python'
            },
            'flask': {
                'file_extensions': ['.py'],
                'naming_convention': 'snake_case',
                'directory_structure': ['app', 'templates', 'static', 'tests'],
                'import_style': 'python'
            }
        }

        return conventions.get(framework, {
            'file_extensions': ['.txt'],
            'naming_convention': 'unknown',
            'directory_structure': [],
            'import_style': 'unknown'
        })

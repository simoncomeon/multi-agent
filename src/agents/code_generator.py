"""
Enhanced Code Generator Agent - Framework-agnostic code generation with proper file handling
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from ..core.base_agent import BaseAgent, TaskInput, TaskResult, FrameworkDetector
from ..core.models import AgentRole, Colors
from ..core.utils import colored_print


class EnhancedCodeGeneratorAgent(BaseAgent):
        """
        Enhanced code generator agent with proper file writing capabilities,
        framework detection, and intelligent code generation.
        """

        def __init__(self, agent_id: str, workspace_dir: str, **kwargs):
                super().__init__(agent_id, AgentRole.CODER, workspace_dir, **kwargs)
                # Code generation specific settings
                self.template_cache = {}
                self.language_parsers = self._init_language_parsers()

        def _define_capabilities(self) -> Dict[str, bool]:
                """Define code generator capabilities"""
                return {
                        'code_generation': True,
                        'file_creation': True,
                        'file_modification': True,
                        'framework_adaptation': True,
                        'template_processing': True,
                        'syntax_validation': True,
                        'dependency_resolution': True,
                        'project_scaffolding': True
                }

        def _define_supported_file_types(self) -> List[str]:
                """Support wide range of programming file types"""
                return [
                        # Web technologies
                        '.js', '.jsx', '.ts', '.tsx', '.vue', '.html', '.css', '.scss', '.sass',
                        # Python
                        '.py', '.pyx', '.pyi',
                        # Configuration
                        '.json', '.yaml', '.yml', '.toml', '.ini', '.env',
                        # Documentation
                        '.md', '.rst', '.txt',
                        # Others
                        '.go', '.rs', '.java', '.cpp', '.c', '.h', '.php', '.rb'
                ]

        def _init_language_parsers(self) -> Dict[str, Any]:
                """Initialize language-specific parsers and validators"""
                return {
                        'python': {
                                'keywords': ['def', 'class', 'import', 'from', 'if', 'for', 'while'],
                                'indent_style': 'spaces',
                                'indent_size': 4
                        },
                        'javascript': {
                                'keywords': ['function', 'const', 'let', 'var', 'class', 'import', 'export'],
                                'indent_style': 'spaces',
                                'indent_size': 2
                        },
                        'typescript': {
                                'keywords': ['interface', 'type', 'function', 'const', 'let', 'class'],
                                'indent_style': 'spaces',
                                'indent_size': 2
                        }
                }

        def _is_task_type_supported(self, task_type: str) -> bool:
                """Check if task type is supported by code generator"""
                supported_types = [
                        'code_generation', 'file_creation', 'component_creation',
                        'function_implementation', 'class_creation', 'project_scaffolding',
                        'code_enhancement', 'template_generation'
                ]
                return task_type in supported_types

        def _execute_specific_task(
                self,
                task_input: TaskInput,
                context: Dict
        ) -> TaskResult:
                """Execute code generation task based on input type and context"""
                # Detect framework and adapt approach
                framework = FrameworkDetector.detect_framework(context)
                conventions = FrameworkDetector.get_framework_conventions(framework)
                colored_print(f"Detected framework: {framework}", Colors.CYAN)

                # Determine task approach based on inputs and targets
                if task_input.target_file:
                        return self._handle_targeted_file_generation(
                                task_input, context, framework, conventions)
                elif task_input.target_directory:
                        return self._handle_directory_generation(
                                task_input, context, framework, conventions)
                elif task_input.has_files():
                        return self._handle_file_enhancement(
                                task_input, context, framework, conventions)
                else:
                        return self._handle_general_code_generation(
                                task_input, context, framework, conventions)

        def _handle_targeted_file_generation(
                self,
                task_input: TaskInput,
                context: Dict,
                framework: str,
                conventions: Dict
        ) -> TaskResult:
                """Handle generation of code for a specific target file"""
                target_file = Path(task_input.target_file)
                colored_print(
                        f" Generating code for target file: {target_file}",
                        Colors.BRIGHT_CYAN)

                # Check if file exists for modification vs creation
                file_exists = target_file.exists()
                existing_content = ""
                if file_exists:
                        existing_content = self.read_file(target_file) or ""
                        colored_print(
                                f" Existing file found ({len(existing_content)} chars)",
                                Colors.YELLOW)

                # Create AI prompt for targeted code generation
                prompt = self._create_targeted_generation_prompt(
                        task_input, context, framework, conventions, existing_content, file_exists
                )

                # Execute AI operation
                ai_result = self.execute_ai_operation(prompt)
                if not ai_result['success']:
                        return TaskResult(
                                success=False,
                                message=f"AI code generation failed: {ai_result.get('error', 'Unknown error')}",
                                metadata={'ai_error': ai_result.get('error')}
                        )

                # Extract and process generated code
                generated_code = self._extract_code_from_ai_response(
                        ai_result['response'], target_file.suffix)
                if not generated_code:
                        return TaskResult(
                                success=False,
                                message="No valid code extracted from AI response"
                        )

                # Validate generated code
                validation_result = self._validate_generated_code(
                        generated_code, target_file.suffix)
                if not validation_result['valid']:
                        colored_print(
                                f" Code validation issues: {validation_result['issues']}",
                                Colors.YELLOW)

                # Write code to target file
                success = self.write_file(
                        target_file,
                        generated_code,
                        backup=file_exists)
                if success:
                        files_list = [str(target_file)]
                        return TaskResult(
                                success=True,
                                message=f"Successfully {'updated' if file_exists else 'created'} {target_file}",
                                files_created=[] if file_exists else files_list,
                                files_modified=files_list if file_exists else [],
                                output_content=generated_code,
                                metadata={
                                        'framework': framework,
                                        'file_size': len(generated_code),
                                        'validation': validation_result
                                }
                        )
                else:
                        return TaskResult(
                                success=False,
                                message=f"Failed to write code to {target_file}"
                        )

        def _handle_directory_generation(
                self,
                task_input: TaskInput,
                context: Dict,
                framework: str,
                conventions: Dict
        ) -> TaskResult:
                """Handle generation of multiple files in a target directory"""
                target_dir = Path(task_input.target_directory)
                colored_print(
                        f" Generating project structure in: {target_dir}",
                        Colors.BRIGHT_CYAN)

                # Ensure target directory exists
                target_dir.mkdir(parents=True, exist_ok=True)

                # Create AI prompt for project structure generation
                prompt = self._create_project_structure_prompt(
                        task_input, context, framework, conventions, target_dir
                )

                # Execute AI operation
                ai_result = self.execute_ai_operation(prompt)
                if not ai_result['success']:
                        return TaskResult(
                                success=False,
                                message=f"AI project generation failed: {ai_result.get('error', 'Unknown error')}"
                        )

                # Parse AI response for file structure
                file_structure = self._parse_project_structure_response(
                        ai_result['response'])

                # Generate files based on structure
                created_files = []
                for file_info in file_structure:
                        file_path = target_dir / file_info['path']
                        success = self.write_file(file_path, file_info['content'])
                        if success:
                                created_files.append(str(file_path))
                return TaskResult(
                        success=len(created_files) > 0,
                        message=f"Created {len(created_files)} files in {target_dir}",
                        files_created=created_files,
                        metadata={
                                'framework': framework,
                                'total_files': len(file_structure),
                                'successful_files': len(created_files)
                        }
                )

        def _handle_file_enhancement(
                self,
                task_input: TaskInput,
                context: Dict,
                framework: str,
                conventions: Dict
        ) -> TaskResult:
                """Handle enhancement/modification of existing files"""
                colored_print(f" Enhancing {len(task_input.files)} files", Colors.BRIGHT_CYAN)
                modified_files = []
                results = []
                for file_path in task_input.files:
                        file_context = context['files'].get(str(file_path), {})
                        if not file_context.get('readable'):
                                colored_print(f" Skipping unreadable file: {file_path}", Colors.YELLOW)
                                continue

                        # Create enhancement prompt for this file
                        prompt = self._create_file_enhancement_prompt(
                                task_input, file_path, file_context, framework, conventions
                        )

                        # Execute AI operation for this file
                        ai_result = self.execute_ai_operation(prompt)
                        if ai_result['success']:
                                enhanced_code = self._extract_code_from_ai_response(
                                        ai_result['response'], file_path.suffix
                                )
                                if enhanced_code and self.write_file(file_path, enhanced_code, backup=True):
                                        modified_files.append(str(file_path))
                                        results.append(f"Enhanced {file_path.name}")
                        else:
                                results.append(f"Failed to enhance {file_path.name}: {ai_result.get('error', 'Unknown error')}")

                return TaskResult(
                        success=len(modified_files) > 0,
                        message=f"Enhanced {len(modified_files)}/{len(task_input.files)} files",
                        files_modified=modified_files,
                        metadata={'enhancement_results': results, 'framework': framework}
                )

        def _handle_general_code_generation(
                self,
                task_input: TaskInput,
                context: Dict,
                framework: str,
                conventions: Dict
        ) -> TaskResult:
                """Handle general code generation without specific targets"""
                colored_print(f" General code generation", Colors.BRIGHT_CYAN)

                # Create general generation prompt
                prompt = self._create_general_generation_prompt(
                        task_input, context, framework, conventions
                )

                # Execute AI operation
                ai_result = self.execute_ai_operation(prompt)
                if not ai_result['success']:
                        return TaskResult(
                                success=False,
                                message=f"AI code generation failed: {ai_result.get('error', 'Unknown error')}"
                        )

                # For general generation, provide the code as output content
                # and suggest file locations
                generated_content = ai_result['response']
                file_suggestions = self._analyze_code_for_file_suggestions(generated_content, framework)
                return TaskResult(
                        success=True,
                        message="Code generation completed - review output for implementation",
                        output_content=generated_content,
                        metadata={
                                'framework': framework,
                                'suggested_files': file_suggestions,
                                'requires_manual_implementation': True
                        }
                )

        def _create_targeted_generation_prompt(
                self,
                task_input: TaskInput,
                context: Dict,
                framework: str,
                conventions: Dict,
                existing_content: str,
                file_exists: bool
        ) -> str:
                """Create AI prompt for targeted file generation"""
                base_prompt = self.create_ai_prompt(task_input, context, "TARGETED_CODE_GENERATION")

                # Add specific instructions for targeted generation
                additional_instructions = [
                        "",
                        "TARGETED FILE GENERATION INSTRUCTIONS:",
                        f"- Target file: {task_input.target_file}",
                        f"- Framework: {framework}",
                        f"- File extension: {Path(task_input.target_file).suffix}",
                        f"- Action: {'MODIFY' if file_exists else 'CREATE'}",
                ]
                if file_exists and existing_content:
                        additional_instructions.extend([
                                "",
                                "EXISTING FILE CONTENT:",
                                "```",
                                existing_content[:2000] + ("...[truncated]" if len(existing_content) > 2000 else ""),
                                "```",
                                "",
                                "MODIFICATION INSTRUCTIONS:",
                                "- Preserve existing functionality unless explicitly changing it",
                                "- Add the requested functionality seamlessly",
                                "- Maintain existing code style and patterns",
                                "- Include proper imports and dependencies"
                        ])
                else:
                        additional_instructions.extend([
                                "",
                                "FILE CREATION INSTRUCTIONS:",
                                "- Create a complete, working file",
                                "- Include all necessary imports and dependencies",
                                "- Follow framework conventions and best practices",
                                "- Add appropriate error handling and validation",
                                "- Include helpful comments for complex logic"
                        ])

                # Add framework-specific instructions
                if conventions:
                        additional_instructions.extend([
                                "",
                                "FRAMEWORK CONVENTIONS:",
                                f"- Naming convention: {conventions.get('naming_convention', 'unknown')}",
                                f"- File extensions: {', '.join(conventions.get('file_extensions', []))}",
                                f"- Import style: {conventions.get('import_style', 'unknown')}"
                        ])

                additional_instructions.extend([
                        "",
                        "OUTPUT FORMAT:",
                        "- Provide ONLY the complete file content",
                        "- No explanations, comments, or markdown formatting",
                        "- The output will be written directly to the file",
                        "- Ensure the code is syntactically correct and complete"
                ])
                return base_prompt + "\n" + "\n".join(additional_instructions)

        def _create_project_structure_prompt(
                self,
                task_input: TaskInput,
                context: Dict,
                framework: str,
                conventions: Dict,
                target_dir: Path
        ) -> str:
                """Create AI prompt for project structure generation"""
                base_prompt = self.create_ai_prompt(task_input, context, "PROJECT_STRUCTURE_GENERATION")
                additional_instructions = [
                        "",
                        "PROJECT STRUCTURE GENERATION INSTRUCTIONS:",
                        f"- Target directory: {target_dir}",
                        f"- Framework: {framework}",
                        f"- Generate complete project structure with multiple files",
                ]
                if conventions.get('directory_structure'):
                        additional_instructions.extend([
                                f"- Recommended directories: {', '.join(conventions['directory_structure'])}",
                        ])

                additional_instructions.extend([
                        "",
                        "OUTPUT FORMAT:",
                        "Structure your response as follows for each file:",
                        "FILE: path/to/file.ext",
                        "```",
                        "file content here",
                        "```",
                        "",
                        "Repeat this pattern for all files in the project structure.",
                        "Create a complete, functional project with proper organization."
                ])
                return base_prompt + "\n" + "\n".join(additional_instructions)

        def _create_file_enhancement_prompt(
                self,
                task_input: TaskInput,
                file_path: Path,
                file_context: Dict,
                framework: str,
                conventions: Dict
        ) -> str:
                """Create AI prompt for file enhancement"""
                file_content = file_context.get('content', '')
                prompt_parts = [
                        f"AGENT ROLE: CODE_ENHANCEMENT",
                        f"OPERATION: ENHANCE_EXISTING_FILE",
                        "",
                        f"TASK DESCRIPTION:",
                        task_input.description,
                        "",
                        f"TARGET FILE: {file_path}",
                        f"FRAMEWORK: {framework}",
                        "",
                        "CURRENT FILE CONTENT:",
                        "```",
                        file_content,
                        "```",
                        "",
                        "ENHANCEMENT INSTRUCTIONS:",
                        "- Enhance the existing code based on the task description",
                        "- Preserve all existing functionality",
                        "- Add new features seamlessly",
                        "- Follow existing code style and patterns",
                        "- Improve code quality where appropriate",
                        "",
                        "OUTPUT FORMAT:",
                        "- Provide ONLY the complete enhanced file content",
                        "- No explanations or markdown formatting",
                        "- Ensure all existing functionality is preserved",
                        "- The output will replace the existing file content"
                ]
                if task_input.requirements:
                        prompt_parts.extend([
                                "",
                                "REQUIREMENTS:",
                                "\n".join(f"- {req}" for req in task_input.requirements)
                        ])
                if task_input.constraints:
                        prompt_parts.extend([
                                "",
                                "CONSTRAINTS:",
                                "\n".join(f"- {constraint}" for constraint in task_input.constraints)
                        ])
                return "\n".join(prompt_parts)

        def _create_general_generation_prompt(
                self,
                task_input: TaskInput,
                context: Dict,
                framework: str,
                conventions: Dict
        ) -> str:
                """Create AI prompt for general code generation"""
                base_prompt = self.create_ai_prompt(task_input, context, "GENERAL_CODE_GENERATION")
                additional_instructions = [
                        "",
                        "GENERAL CODE GENERATION INSTRUCTIONS:",
                        f"- Framework: {framework}",
                        "- Generate complete, working code implementation",
                        "- Include multiple files if the solution requires it",
                        "- Provide clear file structure recommendations",
                        "",
                        "OUTPUT FORMAT:",
                        "For each file in your solution, use this format:",
                        "FILE: suggested/path/filename.ext",
                        "```",
                        "file content here",
                        "```",
                        "",
                        "Include all necessary files for a complete implementation.",
                        "Add comments explaining the overall structure and key components."
                ]
                return base_prompt + "\n" + "\n".join(additional_instructions)

        def _extract_code_from_ai_response(self, response: str, file_extension: str) -> str:
                """Extract clean code content from AI response"""
                # Remove common AI response formatting
                cleaned_response = response.strip()

                # Try to extract code from markdown code blocks
                code_block_pattern = r'```(?:\w+\s*)?\n?(.*?)```'
                matches = re.findall(code_block_pattern, cleaned_response, re.DOTALL)
                if matches:
                        # Use the largest code block (likely the main implementation)
                        code_content = max(matches, key=len).strip()
                else:
                        # If no code blocks, use the entire response but clean it up
                        code_content = cleaned_response

                # Remove common AI response prefixes/suffixes
                prefixes_to_remove = [
                        "Here's the implementation:",
                        "Here's the code:",
                        "Here's your solution:",
                        "The implementation is:",
                        "```" + file_extension.lstrip('.'),
                        "```"
                ]
                for prefix in prefixes_to_remove:
                        if code_content.startswith(prefix):
                                code_content = code_content[len(prefix):].strip()

                # Remove trailing explanatory text
                lines = code_content.split('\n')

                # Find the last line that looks like code (has indentation or common code patterns)
                last_code_line = len(lines) - 1
                for i in range(len(lines) - 1, -1, -1):
                        line = lines[i].strip()
                        if (
                                line and (
                                        line.startswith((' ', '\t')) or  # Indented
                                        any(keyword in line for keyword in ['def ', 'class ', 'function ', 'const ', 'let ', 'var ']) or
                                        line.endswith((';', '{', '}', ')', ']')) or
                                        '=' in line
                                )
                        ):
                                last_code_line = i
                                break

                # Keep only up to the last code line
                code_content = '\n'.join(lines[:last_code_line + 1])
                return code_content.strip()

        def _validate_generated_code(self, code: str, file_extension: str) -> Dict[str, Any]:
                """Validate generated code for syntax and structure"""
                validation_result = {
                        'valid': True,
                        'issues': [],
                        'warnings': [],
                        'language': file_extension.lstrip('.')
                }
                try:
                        # Basic syntax validation based on file type
                        if file_extension in ['.py']:
                                self._validate_python_code(code, validation_result)
                        elif file_extension in ['.js', '.jsx', '.ts', '.tsx']:
                                self._validate_javascript_code(code, validation_result)
                        elif file_extension in ['.json']:
                                self._validate_json_code(code, validation_result)

                        # General validations
                        if not code.strip():
                                validation_result['valid'] = False
                                validation_result['issues'].append("Generated code is empty")
                        if len(code.splitlines()) < 2:
                                validation_result['warnings'].append("Generated code is very short")
                except Exception as e:
                        validation_result['issues'].append(f"Validation error: {str(e)}")
                        validation_result['valid'] = len(validation_result['issues']) == 0
                return validation_result

        def _validate_python_code(self, code: str, result: Dict) -> None:
                """Validate Python code syntax"""
                try:
                        compile(code, '<string>', 'exec')
                except SyntaxError as e:
                        result['issues'].append(f"Python syntax error: {e}")
                except Exception as e:
                        result['warnings'].append(f"Python compilation warning: {e}")

        def _validate_javascript_code(self, code: str, result: Dict) -> None:
                """Basic JavaScript code validation"""
                # Check for basic syntax patterns
                if code.count('{') != code.count('}'):
                        result['issues'].append("Mismatched curly braces")
                if code.count('(') != code.count(')'):
                        result['issues'].append("Mismatched parentheses")
                if code.count('[') != code.count(']'):
                        result['issues'].append("Mismatched square brackets")

        def _validate_json_code(self, code: str, result: Dict) -> None:
                """Validate JSON syntax"""
                try:
                        json.loads(code)
                except json.JSONDecodeError as e:
                        result['issues'].append(f"JSON syntax error: {e}")

        def _parse_project_structure_response(self, response: str) -> List[Dict]:
                """Parse AI response for project structure with multiple files"""
                files = []
                current_file = None
                current_content = []
                in_code_block = False
                for line in response.split('\n'):
                        line_stripped = line.strip()
                        # Check for file declaration
                        if line_stripped.startswith('FILE:'):
                                # Save previous file if exists
                                if current_file:
                                        files.append({
                                                'path': current_file,
                                                'content': '\n'.join(current_content).strip()
                                        })
                                # Start new file
                                current_file = line_stripped[5:].strip()
                                current_content = []
                                in_code_block = False
                                continue

                        # Check for code block markers
                        if line_stripped.startswith('```'):
                                in_code_block = not in_code_block
                                continue

                        # Collect content if we're in a file and in a code block
                        if current_file and in_code_block:
                                current_content.append(line)

                # Don't forget the last file
                if current_file:
                        files.append({
                                'path': current_file,
                                'content': '\n'.join(current_content).strip()
                        })
                return files

        def _analyze_code_for_file_suggestions(self, code: str, framework: str) -> List[Dict]:
                """Analyze generated code to suggest file organization"""
                suggestions = []

                # Look for class definitions
                class_matches = re.findall(r'class\s+(\w+)', code)
                for class_name in class_matches:
                        if framework == 'python':
                                filename = f"{class_name.lower()}.py"
                        else:
                                filename = f"{class_name}.js"
                        suggestions.append({
                                'type': 'class',
                                'name': class_name,
                                'suggested_file': filename,
                                'reason': f'Class {class_name} definition found'
                        })

                # Look for function definitions
                if framework == 'python':
                        func_matches = re.findall(r'def\s+(\w+)', code)
                else:
                        func_matches = re.findall(r'function\s+(\w+)|const\s+(\w+)\s*=', code)
                        func_matches = [f[0] or f[1] for f in func_matches if f[0] or f[1]]
                for func_name in func_matches:
                        if len(func_matches) == 1:  # Single function, suggest utils file
                                suggestions.append({
                                        'type': 'function',
                                        'name': func_name,
                                        'suggested_file': f"utils.{framework.split('/')[0] if '/' in framework else framework}",
                                        'reason': f'Single function {func_name} found'
                                })
                return suggestions

        def _ai_fallback_response(self, prompt: str) -> Dict[str, Any]:
                """Provide intelligent fallback when AI is unavailable"""
                return {
                        'success': True,
                        'response': self._generate_fallback_template(prompt),
                        'fallback': True
                }

        def _generate_fallback_template(self, prompt: str) -> str:
                """Generate basic code template when AI is unavailable"""
                # Analyze prompt for language and type
                if 'python' in prompt.lower() or '.py' in prompt:
                        return '''# Generated code template
# TODO: Implement functionality as described

def main():
        """Main function - implement your logic here"""
        pass

if __name__ == "__main__":
        main()
'''
                elif any(lang in prompt.lower() for lang in ['javascript', 'react', '.js', '.jsx']):
                        return '''// Generated code template
// TODO: Implement functionality as described

function main() {
        // Implement your logic here
}

export default main;
'''
                else:
                        return '''// Generated code template
// TODO: Implement functionality as described
// This is a fallback template - customize as needed
'''


# Example usage functions for easy integration
def create_code_generator(workspace_dir: str, agent_id: str = "enhanced_code_generator") -> EnhancedCodeGeneratorAgent:
        """Factory function to create enhanced code generator"""
        return EnhancedCodeGeneratorAgent(agent_id, workspace_dir)


def generate_code_for_file(agent: EnhancedCodeGeneratorAgent, description: str,
                                                   target_file: str, **kwargs) -> TaskResult:
        """Convenience function for targeted file generation"""
        task_input = TaskInput(
                task_description=description,
                target_file=target_file,
                task_type='code_generation',
                requirements=kwargs.get('requirements', []),
                constraints=kwargs.get('constraints', []),
                **kwargs
        )
        return agent.execute_task(task_input)


def generate_project_structure(agent: EnhancedCodeGeneratorAgent, description: str,
                                                           target_directory: str, **kwargs) -> TaskResult:
        """Convenience function for project structure generation"""
        task_input = TaskInput(
                task_description=description,
                target_directory=target_directory,
                task_type='project_scaffolding',
                requirements=kwargs.get('requirements', []),
                constraints=kwargs.get('constraints', []),
                **kwargs
        )
        return agent.execute_task(task_input)


def enhance_existing_files(agent: EnhancedCodeGeneratorAgent, description: str,
                                                   files: List[str], **kwargs) -> TaskResult:
        """Convenience function for file enhancement"""
        task_input = TaskInput(
                task_description=description,
                files=files,
                task_type='file_enhancement',
                requirements=kwargs.get('requirements', []),
                constraints=kwargs.get('constraints', []),
                **kwargs
        )
        return agent.execute_task(task_input)
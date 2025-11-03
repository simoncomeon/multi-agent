"""
Helper Agent - Task Decomposition and Delegation Planning

This agent takes simple task descriptions and creates executable delegate descriptions
for different specialized agents in the multi-agent system. It uses AI best practices
and formats tasks exactly as the CoordinatorAgent expects them.
"""

import re
from typing import List, Dict, Any, Optional
from ..core.models import AgentRole, Task, TaskStatus
from ..core.utils import colored_print, Colors


class HelperAgent:
    """
    Independent agent that decomposes tasks into actionable subtasks
    and assigns them to appropriate specialized agents.
    """
    
    def __init__(self):
        self.role = AgentRole.HELPER
        self.capabilities = {
            'task_analysis': True,
            'task_decomposition': True,
            'agent_assignment': True,
            'dependency_mapping': True,
            'priority_assignment': True,
            'ai_consultation': True,
            'coordinator_formatting': True
        }
        
        # AI Best Practices Knowledge Base
        self.ai_best_practices = {
            'web_development': {
                'structure': ['setup', 'frontend', 'backend', 'database', 'api', 'testing', 'deployment'],
                'technologies': ['react', 'node.js', 'express', 'mongodb', 'postgresql', 'next.js'],
                'patterns': ['mvc', 'component-based', 'restful-api', 'microservices']
            },
            'mobile_development': {
                'structure': ['setup', 'ui_design', 'state_management', 'api_integration', 'testing', 'deployment'],
                'technologies': ['react-native', 'flutter', 'swift', 'kotlin', 'expo'],
                'patterns': ['mvvm', 'bloc', 'redux', 'provider']
            },
            'data_science': {
                'structure': ['data_collection', 'data_cleaning', 'analysis', 'modeling', 'visualization', 'deployment'],
                'technologies': ['python', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch'],
                'patterns': ['etl', 'mlops', 'data-pipeline', 'feature-engineering']
            },
            'api_development': {
                'structure': ['design', 'setup', 'routes', 'middleware', 'validation', 'documentation', 'testing'],
                'technologies': ['express', 'fastapi', 'django', 'flask', 'graphql'],
                'patterns': ['rest', 'graphql', 'microservices', 'authentication']
            }
        }
        
        # Coordinator task format templates
        self.coordinator_task_formats = {
            'file_management': {
                'keywords': ['file', 'directory', 'folder', 'create', 'organize', 'structure'],
                'task_type': 'file_management',
                'agent': 'file_manager'
            },
            'code_generation': {
                'keywords': ['code', 'generate', 'implement', 'write', 'develop'],
                'task_type': 'code_generation',
                'agent': 'coder'
            },
            'code_review': {
                'keywords': ['review', 'check', 'analyze', 'quality'],
                'task_type': 'code_review',
                'agent': 'code_reviewer'
            },
            'git_management': {
                'keywords': ['git', 'commit', 'push', 'pull', 'branch', 'version'],
                'task_type': 'git_management',
                'agent': 'git_manager'
            },
            'testing': {
                'keywords': ['test', 'testing', 'unit', 'integration'],
                'task_type': 'testing',
                'agent': 'tester'
            },
            'research': {
                'keywords': ['research', 'find', 'search', 'investigate'],
                'task_type': 'research',
                'agent': 'researcher'
            },
            'code_rewrite': {
                'keywords': ['fix', 'rewrite', 'refactor', 'improve'],
                'task_type': 'code_rewrite',
                'agent': 'code_rewriter'
            }
        }
        
        # Agent capability mapping
        self.agent_specializations = {
            AgentRole.CODE_REVIEWER: [
                'review code', 'analyze quality', 'check standards', 'find bugs',
                'security analysis', 'performance review', 'code audit'
            ],
            AgentRole.FILE_MANAGER: [
                'create files', 'organize files', 'manage directories', 'file operations',
                'project structure', 'file search', 'backup files', 'file cleanup'
            ],
            AgentRole.CODER: [
                'generate code', 'create functions', 'write classes', 'implement features',
                'code templates', 'boilerplate code', 'api implementation'
            ],
            AgentRole.COORDINATOR: [
                'manage workflow', 'coordinate tasks', 'task scheduling', 'team coordination',
                'progress tracking', 'resource allocation', 'task prioritization'
            ],
            AgentRole.GIT_MANAGER: [
                'git operations', 'version control', 'commit changes', 'branch management',
                'merge conflicts', 'git history', 'repository management'
            ],
            AgentRole.RESEARCHER: [
                'research frameworks', 'find libraries', 'technology analysis', 'documentation',
                'best practices', 'architecture patterns', 'technology comparison'
            ],
            AgentRole.TESTER: [
                'write tests', 'run tests', 'test coverage', 'integration testing',
                'unit testing', 'test automation', 'quality assurance'
            ],
            AgentRole.CODE_REWRITER: [
                'fix code', 'refactor code', 'optimize code', 'update code',
                'code improvement', 'bug fixes', 'performance optimization'
            ]
        }
    
    def consult_ai_best_practices(self, description: str) -> Dict[str, Any]:
        """
        Simulate AI model consultation for best practices and creative task breakdown.
        
        Args:
            description: Task description to analyze
            
        Returns:
            AI consultation results with best practices and structure recommendations
        """
        colored_print(f"[HELPER] Consulting AI best practices for: {description}", Colors.MAGENTA)
        
        description_lower = description.lower()
        consultation = {
            'project_type': None,
            'recommended_structure': [],
            'technologies': [],
            'patterns': [],
            'file_structure': {},
            'creative_breakdown': []
        }
        
        # Identify project type based on AI knowledge
        for project_type, info in self.ai_best_practices.items():
            if any(tech in description_lower for tech in info['technologies']):
                consultation['project_type'] = project_type
                consultation['recommended_structure'] = info['structure']
                consultation['technologies'] = [tech for tech in info['technologies'] if tech in description_lower]
                consultation['patterns'] = info['patterns']
                break
        
        # Generate creative file structure based on AI best practices
        if consultation['project_type']:
            consultation['file_structure'] = self._generate_ai_file_structure(
                consultation['project_type'], description
            )
        
        # Create creative breakdown with AI insights
        consultation['creative_breakdown'] = self._generate_creative_breakdown(
            description, consultation
        )
        
        colored_print(f"[HELPER] AI consultation complete - identified as {consultation['project_type'] or 'generic'} project", Colors.GREEN)
        
        return consultation

    def _generate_ai_file_structure(self, project_type: str, description: str) -> Dict[str, Any]:
        """Generate AI-recommended file structure based on project type."""
        
        structures = {
            'web_development': {
                'frontend/': ['src/', 'components/', 'pages/', 'styles/', 'utils/', 'assets/'],
                'backend/': ['routes/', 'models/', 'controllers/', 'middleware/', 'config/', 'tests/'],
                'root': ['package.json', 'README.md', '.env', '.gitignore']
            },
            'mobile_development': {
                'src/': ['screens/', 'components/', 'navigation/', 'services/', 'utils/', 'assets/'],
                'root': ['App.js', 'package.json', 'README.md', 'app.json']
            },
            'api_development': {
                'src/': ['routes/', 'models/', 'services/', 'middleware/', 'validators/', 'tests/'],
                'root': ['server.js', 'package.json', 'README.md', '.env', 'swagger.json']
            },
            'data_science': {
                'data/': ['raw/', 'processed/', 'external/'],
                'notebooks/': ['exploratory/', 'modeling/', 'validation/'],
                'src/': ['features/', 'models/', 'visualization/', 'utils/'],
                'root': ['requirements.txt', 'README.md', 'main.py']
            }
        }
        
        return structures.get(project_type, {
            'src/': ['components/', 'utils/', 'config/'],
            'root': ['README.md', '.gitignore']
        })

    def _generate_creative_breakdown(self, description: str, consultation: Dict) -> List[str]:
        """Generate creative task breakdown using AI insights."""
        
        breakdown = []
        project_type = consultation.get('project_type', 'generic')
        
        if project_type == 'web_development':
            breakdown = [
                "Research modern web development frameworks and choose optimal stack",
                "Design component architecture and user interface mockups",
                "Set up development environment with build tools and dependencies",
                "Create responsive frontend components with modern CSS frameworks",
                "Implement backend API with proper route handling and validation", 
                "Integrate database with optimized queries and data models",
                "Add comprehensive testing suite with unit and integration tests",
                "Configure deployment pipeline with CI/CD automation"
            ]
        elif project_type == 'mobile_development':
            breakdown = [
                "Research cross-platform development options and performance considerations",
                "Design mobile-first UI/UX with platform-specific guidelines",
                "Set up development environment with emulators and debugging tools",
                "Implement navigation and state management architecture",
                "Create reusable components with responsive design patterns",
                "Integrate with device APIs and third-party services",
                "Add offline functionality and data synchronization",
                "Test on multiple devices and prepare for app store deployment"
            ]
        elif project_type == 'api_development':
            breakdown = [
                "Design RESTful API architecture with proper resource modeling",
                "Set up project structure with industry-standard organization",
                "Implement authentication and authorization middleware",
                "Create data validation and sanitization layers",
                "Add comprehensive error handling and logging",
                "Generate API documentation with interactive examples",
                "Implement rate limiting and security best practices",
                "Add monitoring, testing, and deployment automation"
            ]
        else:
            # Generic creative breakdown
            breakdown = [
                f"Research best practices and architectural patterns for: {description}",
                f"Design system architecture and component structure",
                f"Set up development environment with optimal toolchain",
                f"Implement core functionality with clean, maintainable code",
                f"Add comprehensive testing and quality assurance",
                f"Create documentation and deployment procedures"
            ]
        
        return breakdown

    def analyze_task(self, description: str) -> Dict[str, Any]:
        """
        Analyze a task description using AI best practices and creative insights.
        
        Args:
            description: Simple task description from user
            
        Returns:
            Dictionary with comprehensive task analysis results
        """
        colored_print(f"[HELPER] Analyzing task with AI consultation: {description}", Colors.CYAN)
        
        # Get AI consultation first
        ai_consultation = self.consult_ai_best_practices(description)
        
        analysis = {
            'original_description': description,
            'task_type': self._identify_task_type(description),
            'complexity': self._assess_complexity(description, ai_consultation),
            'required_agents': self._identify_required_agents(description),
            'estimated_subtasks': self._estimate_subtasks(description),
            'dependencies': self._identify_dependencies(description),
            'ai_consultation': ai_consultation,
            'coordinator_compatible': True
        }
        
        return analysis
    
    def format_task_for_coordinator(self, subtask_description: str, task_type: str = None) -> Dict[str, Any]:
        """
        Format a task description with enhanced specificity and precision for the CoordinatorAgent.
        
        Args:
            subtask_description: The task description to format
            task_type: Optional explicit task type
            
        Returns:
            Dictionary formatted for CoordinatorAgent consumption with enhanced precision
        """
        # Make the description more specific and actionable
        enhanced_description = self._enhance_task_description(subtask_description)
        
        # Determine the appropriate coordinator format with better detection
        coordinator_format = self._detect_precise_format(enhanced_description, task_type)
        
        # Create coordinator-compatible task with enhanced specificity
        formatted_task = {
            'description': enhanced_description,
            'task_type': coordinator_format['task_type'],
            'assigned_to': coordinator_format['agent'],
            'priority': self._calculate_precise_priority(enhanced_description),
            'complexity_hints': self._generate_precise_hints(enhanced_description, coordinator_format),
            'execution_context': self._add_execution_context(enhanced_description),
            'success_criteria': self._define_task_success_criteria(enhanced_description),
            'coordinator_ready': True
        }
        
        return formatted_task
    
    def _enhance_task_description(self, description: str) -> str:
        """Make task descriptions more specific and actionable for agents"""
        desc_lower = description.lower()
        
        # File path specificity
        if 'file' in desc_lower and not any(path in description for path in ['/', '\\', '.js', '.py', '.css', '.html']):
            if 'react' in desc_lower or 'component' in desc_lower:
                description = description.replace('file', 'React component file (.jsx/.js)')
            elif 'style' in desc_lower or 'css' in desc_lower:
                description = description.replace('file', 'stylesheet file (.css/.scss)')
            elif 'config' in desc_lower:
                description = description.replace('file', 'configuration file (.json/.yml)')
        
        # Technology specificity
        replacements = {
            'database': 'database (specify: MongoDB/PostgreSQL/MySQL)',
            'api': 'REST API endpoint',
            'frontend': 'frontend React components',
            'backend': 'Node.js/Express backend server',
            'style': 'CSS/SCSS styling',
            'component': 'React functional component',
            'function': 'JavaScript/TypeScript function',
            'test': 'Jest/testing-library unit test',
            'deploy': 'deployment configuration',
            'setup': 'project setup and initialization'
        }
        
        enhanced = description
        for generic, specific in replacements.items():
            if generic in desc_lower and specific.split()[0].lower() not in desc_lower:
                # Only replace if the specific term isn't already there
                enhanced = re.sub(r'\b' + generic + r'\b', specific, enhanced, flags=re.IGNORECASE)
        
        # Add action specificity
        action_enhancements = {
            r'\bcreate\b': 'create and implement',
            r'\bbuild\b': 'build and configure',
            r'\bsetup\b': 'setup and initialize',
            r'\bfix\b': 'debug and fix',
            r'\bupdate\b': 'update and refactor',
            r'\btest\b': 'write and execute tests for'
        }
        
        for pattern, replacement in action_enhancements.items():
            enhanced = re.sub(pattern, replacement, enhanced, flags=re.IGNORECASE)
        
        return enhanced
    
    def _detect_precise_format(self, description: str, task_type: str = None) -> Dict:
        """Detect task format with enhanced precision"""
        desc_lower = description.lower()
        
        # Enhanced keyword matching with specificity scores
        format_scores = {}
        
        for format_name, format_info in self.coordinator_task_formats.items():
            score = 0
            for keyword in format_info['keywords']:
                if keyword in desc_lower:
                    # Weight by keyword importance and specificity
                    if keyword in ['create', 'build', 'implement']:
                        score += 2
                    elif keyword in ['file', 'component', 'function']:
                        score += 3
                    elif keyword in ['react', 'node', 'express', 'database']:
                        score += 4
                    else:
                        score += 1
            format_scores[format_name] = score
        
        # Use explicit task_type if provided
        if task_type and task_type in self.coordinator_task_formats:
            return self.coordinator_task_formats[task_type]
        
        # Select format with highest score
        if format_scores:
            best_format = max(format_scores.items(), key=lambda x: x[1])
            if best_format[1] > 0:
                return self.coordinator_task_formats[best_format[0]]
        
        # Enhanced default selection based on content analysis
        if any(word in desc_lower for word in ['component', 'react', 'frontend', 'ui']):
            return self.coordinator_task_formats['code_generation']
        elif any(word in desc_lower for word in ['review', 'quality', 'check', 'analyze']):
            return self.coordinator_task_formats['code_review']
        elif any(word in desc_lower for word in ['file', 'directory', 'structure', 'organize']):
            return self.coordinator_task_formats['file_management']
        else:
            return self.coordinator_task_formats['code_generation']
    
    def _calculate_precise_priority(self, description: str) -> int:
        """Calculate more precise priority based on task characteristics"""
        desc_lower = description.lower()
        priority = 1
        
        # High priority indicators
        if any(word in desc_lower for word in ['critical', 'urgent', 'fix', 'error', 'bug']):
            priority = 3
        elif any(word in desc_lower for word in ['important', 'required', 'dependency']):
            priority = 2
        elif any(word in desc_lower for word in ['setup', 'initialize', 'configure']):
            priority = 2  # Setup tasks are often dependencies
        elif any(word in desc_lower for word in ['test', 'documentation', 'optional']):
            priority = 1
        
        return priority
    
    def _generate_precise_hints(self, description: str, coordinator_format: Dict) -> Dict:
        """Generate precise complexity hints based on task analysis"""
        desc_lower = description.lower()
        
        # Base estimates by agent type
        base_times = {
            'code_generator': '20-45 minutes',
            'code_rewriter': '15-30 minutes', 
            'file_manager': '10-20 minutes',
            'code_reviewer': '15-25 minutes'
        }
        
        estimated_time = base_times.get(coordinator_format['agent'], '15-30 minutes')
        
        # Adjust based on complexity indicators
        if any(word in desc_lower for word in ['complex', 'advanced', 'multiple', 'integration']):
            estimated_time = '45-90 minutes'
        elif any(word in desc_lower for word in ['simple', 'basic', 'quick', 'small']):
            estimated_time = '10-15 minutes'
        
        # Identify dependencies
        dependencies = []
        if 'setup' in desc_lower or 'initialize' in desc_lower:
            dependencies = ['project_setup']
        elif 'component' in desc_lower and 'style' in desc_lower:
            dependencies = ['component_creation']
        elif 'test' in desc_lower:
            dependencies = ['implementation_complete']
        
        return {
            'estimated_time': estimated_time,
            'dependencies': dependencies,
            'parallel_execution': 'test' in desc_lower or 'review' in desc_lower,
            'complexity_level': self._assess_complexity_level(description)
        }
    
    def _assess_complexity_level(self, description: str) -> str:
        """Assess complexity level for better resource allocation"""
        desc_lower = description.lower()
        
        high_complexity = ['integration', 'system', 'architecture', 'advanced', 'complex', 'multiple']
        medium_complexity = ['component', 'function', 'feature', 'implement', 'configure']
        low_complexity = ['simple', 'basic', 'small', 'quick', 'minor']
        
        if any(word in desc_lower for word in high_complexity):
            return 'high'
        elif any(word in desc_lower for word in low_complexity):
            return 'low'
        else:
            return 'medium'
    
    def _add_execution_context(self, description: str) -> Dict:
        """Add execution context for better agent preparation"""
        desc_lower = description.lower()
        
        context = {
            'requires_ai_context': True,  # All tasks now benefit from context
            'file_operations': False,
            'project_analysis': False,
            'external_dependencies': False
        }
        
        # Detect specific context requirements
        if any(word in desc_lower for word in ['file', 'create', 'edit', 'modify']):
            context['file_operations'] = True
        
        if any(word in desc_lower for word in ['project', 'structure', 'architecture', 'analyze']):
            context['project_analysis'] = True
        
        if any(word in desc_lower for word in ['install', 'dependency', 'package', 'library']):
            context['external_dependencies'] = True
        
        return context
    
    def _define_task_success_criteria(self, description: str) -> List[str]:
        """Define specific success criteria for each task"""
        desc_lower = description.lower()
        criteria = []
        
        if 'create' in desc_lower or 'implement' in desc_lower:
            criteria.extend([
                'Code is functional and error-free',
                'Follows project coding standards',
                'Includes proper error handling'
            ])
        
        if 'component' in desc_lower:
            criteria.extend([
                'Component renders correctly',
                'Props are properly typed',
                'Component integrates with existing code'
            ])
        
        if 'test' in desc_lower:
            criteria.extend([
                'All tests pass',
                'Code coverage meets requirements',
                'Edge cases are covered'
            ])
        
        if 'file' in desc_lower or 'setup' in desc_lower:
            criteria.extend([
                'Files are created in correct locations',
                'Directory structure is organized',
                'Configuration is properly set'
            ])
        
        # Default criteria if none specific found
        if not criteria:
            criteria = [
                'Task completed successfully',
                'Code quality standards met',
                'Integration with existing project verified'
            ]
        
        return criteria

    def decompose_task(self, description: str) -> List[Dict[str, Any]]:
        """
        Decompose a task into precise, coordinator-compatible subtasks with enhanced specificity.
        
        Args:
            description: Simple task description
            
        Returns:
            List of precisely formatted coordinator subtask dictionaries
        """
        colored_print(f"[HELPER] Decomposing task with enhanced precision and AI creativity...", Colors.YELLOW)
        
        # Enhanced analysis with precision focus
        analysis = self.analyze_task(description)
        ai_consultation = analysis['ai_consultation']
        
        # Create more specific subtasks based on enhanced analysis
        if ai_consultation['creative_breakdown']:
            colored_print(f"[HELPER] Using AI-enhanced precise breakdown", Colors.MAGENTA)
            subtasks = self._create_precise_ai_driven_subtasks(description, analysis)
        else:
            # Enhanced traditional breakdown with more specificity
            subtasks = self._create_precise_traditional_subtasks(description, analysis)
        
        # Apply precision enhancements and coordinator formatting
        coordinator_subtasks = []
        for i, subtask in enumerate(subtasks):
            # Enhanced formatting with precision
            formatted_task = self.format_task_for_coordinator(
                subtask['description'], 
                subtask.get('task_type')
            )
            
            # Merge original subtask data with formatted task
            formatted_task.update({
                'id': f"subtask_{i+1:03d}",
                'sequence_order': i + 1,
                'total_subtasks': len(subtasks),
                'estimated_time': subtask.get('estimated_time', '20-30 minutes'),  # Preserve from original subtask
                'priority': subtask.get('priority', formatted_task.get('priority', 1)),  # Use subtask priority if available
                'depends_on': subtask.get('depends_on', []),
                'precision_enhanced': True,
                'context_requirements': self._determine_context_requirements(subtask['description']),
                'validation_steps': self._generate_validation_steps(subtask['description'])
            })
            
            # Ensure complexity_hints includes the estimated_time
            if 'complexity_hints' in formatted_task:
                formatted_task['complexity_hints']['estimated_time'] = subtask.get('estimated_time', '20-30 minutes')
            
            coordinator_subtasks.append(formatted_task)
        
        # Post-process for enhanced coordination
        coordinator_subtasks = self._optimize_task_sequence(coordinator_subtasks)
        
        colored_print(f"[HELPER] Created {len(coordinator_subtasks)} precision-enhanced coordinator subtasks", Colors.GREEN)
        return coordinator_subtasks
    
    def _create_precise_ai_driven_subtasks(self, description: str, analysis: Dict) -> List[Dict]:
        """Create AI-driven subtasks with enhanced precision"""
        ai_breakdown = analysis['ai_consultation']['creative_breakdown']
        
        subtasks = []
        for i, ai_task in enumerate(ai_breakdown):
            # Enhance AI suggestions with more specificity
            enhanced_description = self._make_description_more_specific(ai_task, description, analysis)
            
            subtask = {
                'description': enhanced_description,
                'task_type': self._infer_precise_task_type(enhanced_description),
                'priority': self._calculate_ai_task_priority(ai_task, i, len(ai_breakdown)),
                'estimated_time': self._estimate_precise_time(enhanced_description),
                'depends_on': self._identify_precise_dependencies(enhanced_description, i),
                'ai_enhanced': True
            }
            subtasks.append(subtask)
        
        return subtasks
    
    def _create_precise_traditional_subtasks(self, description: str, analysis: Dict) -> List[Dict]:
        """Create traditional subtasks with enhanced precision"""
        task_type = analysis['task_type']
        complexity = analysis['complexity']
        
        # Get enhanced template based on task analysis
        template = self._get_enhanced_task_template(task_type, description)
        
        subtasks = []
        for i, template_task in enumerate(template):
            # Apply context-specific enhancements
            enhanced_description = self._apply_context_to_template(
                template_task, description, analysis
            )
            
            subtask = {
                'description': enhanced_description,
                'task_type': template_task.get('type', 'code_generation'),
                'priority': template_task.get('priority', 1),
                'estimated_time': self._adjust_time_for_complexity(
                    template_task.get('time', '20 minutes'), complexity
                ),
                'depends_on': template_task.get('depends_on', []),
                'template_enhanced': True
            }
            subtasks.append(subtask)
        
        return subtasks
    
    def _make_description_more_specific(self, ai_task: str, original_description: str, analysis: Dict) -> str:
        """Make AI task descriptions more specific and actionable"""
        # Extract specific technologies/frameworks from original description
        original_lower = original_description.lower()
        
        # Technology-specific enhancements
        tech_context = []
        if 'react' in original_lower:
            tech_context.append('React')
        if 'node' in original_lower:
            tech_context.append('Node.js')
        if 'express' in original_lower:
            tech_context.append('Express')
        if 'database' in original_lower:
            tech_context.append('database')
        
        enhanced = ai_task
        
        # Add technology context if not present
        if tech_context and not any(tech.lower() in ai_task.lower() for tech in tech_context):
            enhanced = f"{ai_task} using {', '.join(tech_context)}"
        
        # Add file path specificity
        if 'file' in enhanced.lower() and not any(ext in enhanced for ext in ['.js', '.jsx', '.py', '.css', '.html']):
            if 'component' in enhanced.lower():
                enhanced = enhanced.replace('file', 'component file (src/components/)')
            elif 'config' in enhanced.lower():
                enhanced = enhanced.replace('file', 'configuration file')
            elif 'style' in enhanced.lower():
                enhanced = enhanced.replace('file', 'stylesheet (src/styles/)')
        
        # Add action specificity
        action_enhancements = {
            'setup': 'setup and configure',
            'create': 'create and implement',
            'build': 'build and test',
            'implement': 'implement and integrate'
        }
        
        for generic, specific in action_enhancements.items():
            if generic in enhanced.lower() and specific not in enhanced.lower():
                enhanced = enhanced.replace(generic, specific)
        
        return enhanced
    
    def _determine_context_requirements(self, description: str) -> Dict:
        """Determine what context each task needs for optimal execution"""
        desc_lower = description.lower()
        
        requirements = {
            'project_files': [],
            'reference_directories': [],
            'configuration_files': [],
            'dependency_analysis': False
        }
        
        # Project files needed
        if 'component' in desc_lower:
            requirements['project_files'].extend(['package.json', 'src/App.js'])
            requirements['reference_directories'].append('src/components')
        
        if 'style' in desc_lower or 'css' in desc_lower:
            requirements['reference_directories'].append('src/styles')
            requirements['project_files'].append('src/index.css')
        
        if 'api' in desc_lower or 'backend' in desc_lower:
            requirements['project_files'].extend(['package.json', 'server.js'])
            requirements['reference_directories'].append('routes')
        
        if 'test' in desc_lower:
            requirements['reference_directories'].extend(['src', 'tests'])
            requirements['project_files'].append('package.json')
        
        # Configuration files
        if 'setup' in desc_lower or 'config' in desc_lower:
            requirements['configuration_files'].extend(['package.json', 'webpack.config.js', 'tsconfig.json'])
        
        # Dependency analysis
        if 'install' in desc_lower or 'dependency' in desc_lower or 'package' in desc_lower:
            requirements['dependency_analysis'] = True
        
        return requirements
    
    def _generate_validation_steps(self, description: str) -> List[str]:
        """Generate specific validation steps for each task"""
        desc_lower = description.lower()
        steps = []
        
        if 'component' in desc_lower:
            steps.extend([
                'Verify component renders without errors',
                'Check prop types and default values',
                'Test component integration with parent components'
            ])
        
        if 'api' in desc_lower:
            steps.extend([
                'Test API endpoints with sample data',
                'Verify error handling for invalid requests',
                'Check response format and status codes'
            ])
        
        if 'style' in desc_lower or 'css' in desc_lower:
            steps.extend([
                'Verify styles apply correctly across browsers',
                'Check responsive design at different screen sizes',
                'Validate accessibility standards'
            ])
        
        if 'setup' in desc_lower or 'config' in desc_lower:
            steps.extend([
                'Verify all dependencies install correctly',
                'Test build and start scripts',
                'Check development server functionality'
            ])
        
        # Default validation steps
        if not steps:
            steps = [
                'Run basic functionality tests',
                'Check integration with existing code',
                'Verify no breaking changes introduced'
            ]
        
        return steps
    
    def _optimize_task_sequence(self, subtasks: List[Dict]) -> List[Dict]:
        """Optimize task sequence for better coordination flow"""
        # Sort by priority and dependencies
        optimized = sorted(subtasks, key=lambda x: (
            -x.get('priority', 1),  # Higher priority first
            x.get('sequence_order', 0)  # Then by original sequence
        ))
        
        # Update sequence numbers after optimization
        for i, task in enumerate(optimized):
            task['sequence_order'] = i + 1
            task['optimized_sequence'] = True
        
        return optimized
    
    def create_execution_plan(self, description: str) -> Dict[str, Any]:
        """
        Create a complete execution plan with AI insights and coordinator compatibility.
        
        Args:
            description: Task description
            
        Returns:
            Complete execution plan dictionary with AI consultation
        """
        colored_print(f"[HELPER] Creating AI-enhanced execution plan...", Colors.MAGENTA)
        
        # Get AI consultation first for inclusion in plan
        ai_consultation = self.consult_ai_best_practices(description)
        
        subtasks = self.decompose_task(description)
        
        execution_plan = {
            'original_task': description,
            'total_subtasks': len(subtasks),
            'estimated_duration': self._estimate_duration(subtasks),
            'execution_phases': self._organize_phases(subtasks),
            'subtasks': subtasks,
            'ai_consultation': ai_consultation,
            'risk_assessment': self._assess_risks(subtasks),
            'success_criteria': self._define_success_criteria(description, ai_consultation),
            'coordinator_compatible': True
        }
        
        return execution_plan
    
    def _identify_task_type(self, description: str) -> str:
        """Identify the primary type of task."""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['create', 'build', 'develop', 'implement', 'generate']):
            return 'development'
        elif any(word in description_lower for word in ['test', 'verify', 'validate', 'check']):
            return 'testing'
        elif any(word in description_lower for word in ['research', 'find', 'analyze', 'investigate']):
            return 'research'
        elif any(word in description_lower for word in ['fix', 'update', 'refactor', 'improve']):
            return 'maintenance'
        else:
            return 'generic'
    
    def _assess_complexity(self, description: str, ai_consultation: Dict = None) -> str:
        """Assess task complexity based on description and AI insights."""
        word_count = len(description.split())
        complexity_indicators = ['complex', 'multiple', 'integrate', 'system', 'advanced', 'enterprise']
        
        base_complexity = 0
        
        # Word count factor
        if word_count > 20:
            base_complexity += 3
        elif word_count > 10:
            base_complexity += 1
        
        # Keyword indicators
        if any(indicator in description.lower() for indicator in complexity_indicators):
            base_complexity += 2
        
        # AI consultation factor
        if ai_consultation:
            project_type = ai_consultation.get('project_type')
            if project_type in ['web_development', 'mobile_development']:
                base_complexity += 2
            elif project_type == 'data_science':
                base_complexity += 3
            
            # Technology stack complexity
            tech_count = len(ai_consultation.get('technologies', []))
            if tech_count > 2:
                base_complexity += 1
        
        # Determine final complexity
        if base_complexity >= 5:
            return 'high'
        elif base_complexity >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _identify_required_agents(self, description: str) -> List[AgentRole]:
        """Identify which agents are likely needed for the task."""
        description_lower = description.lower()
        required_agents = []
        
        for agent_role, keywords in self.agent_specializations.items():
            if any(keyword in description_lower for keyword in keywords):
                required_agents.append(agent_role)
        
        # Always include coordinator for multi-agent tasks
        if len(required_agents) > 1 and AgentRole.COORDINATOR not in required_agents:
            required_agents.insert(0, AgentRole.COORDINATOR)
        
        return required_agents
    
    def _estimate_subtasks(self, description: str) -> int:
        """Estimate number of subtasks needed."""
        complexity = self._assess_complexity(description)
        required_agents = len(self._identify_required_agents(description))
        
        base_subtasks = {
            'low': 2,
            'medium': 4,
            'high': 8
        }
        
        return min(base_subtasks[complexity] + required_agents, 12)
    
    def _identify_dependencies(self, description: str) -> List[str]:
        """Identify potential dependencies in the task."""
        dependencies = []
        description_lower = description.lower()
        
        if 'test' in description_lower and ('create' in description_lower or 'build' in description_lower):
            dependencies.append('code_before_test')
        if 'deploy' in description_lower:
            dependencies.append('test_before_deploy')
        if 'review' in description_lower:
            dependencies.append('code_before_review')
        
        return dependencies
    
    def _create_ai_driven_subtasks(self, description: str, analysis: Dict) -> List[Dict]:
        """Create subtasks using AI creative breakdown and best practices."""
        subtasks = []
        ai_consultation = analysis['ai_consultation']
        creative_breakdown = ai_consultation.get('creative_breakdown', [])
        
        colored_print(f"[HELPER] Using AI creative breakdown with {len(creative_breakdown)} insights", Colors.CYAN)
        
        for i, creative_task in enumerate(creative_breakdown):
            # Determine task type based on creative task content
            task_type = self._determine_task_type_from_content(creative_task)
            
            subtasks.append({
                'id': f'ai_task_{i+1}',
                'description': creative_task,
                'task_type': task_type,
                'priority': i + 1,
                'estimated_time': self._estimate_time_for_creative_task(creative_task),
                'ai_generated': True
            })
        
        # Add file structure setup if AI recommended specific structure
        if ai_consultation.get('file_structure'):
            subtasks.insert(1, {
                'id': 'file_structure_setup',
                'description': f"Set up AI-recommended file structure for {ai_consultation.get('project_type', 'project')}",
                'task_type': 'file_management',
                'priority': 2,
                'estimated_time': '10-15 minutes',
                'ai_generated': True,
                'file_structure': ai_consultation['file_structure']
            })
            # Adjust priorities of subsequent tasks
            for task in subtasks[2:]:
                task['priority'] += 1
        
        return subtasks

    def _create_traditional_subtasks(self, description: str, analysis: Dict) -> List[Dict]:
        """Create subtasks using traditional analysis methods."""
        if analysis['task_type'] == 'development':
            return self._create_development_subtasks(description, analysis)
        elif analysis['task_type'] == 'maintenance':
            return self._create_maintenance_subtasks(description, analysis)
        elif analysis['task_type'] == 'research':
            return self._create_research_subtasks(description, analysis)
        elif analysis['task_type'] == 'testing':
            return self._create_testing_subtasks(description, analysis)
        else:
            return self._create_generic_subtasks(description, analysis)

    def _determine_task_type_from_content(self, task_content: str) -> str:
        """Determine coordinator task type from AI-generated task content."""
        content_lower = task_content.lower()
        
        if any(word in content_lower for word in ['research', 'investigate', 'analyze', 'study']):
            return 'research'
        elif any(word in content_lower for word in ['file', 'structure', 'organize', 'setup', 'create directories']):
            return 'file_management'
        elif any(word in content_lower for word in ['implement', 'code', 'develop', 'build', 'create']):
            return 'code_generation'
        elif any(word in content_lower for word in ['test', 'testing', 'validation', 'verify']):
            return 'testing'
        elif any(word in content_lower for word in ['review', 'check', 'quality', 'audit']):
            return 'code_review'
        elif any(word in content_lower for word in ['git', 'version', 'commit', 'deploy']):
            return 'git_management'
        elif any(word in content_lower for word in ['fix', 'refactor', 'improve', 'optimize']):
            return 'code_rewrite'
        else:
            return 'general'

    def _estimate_time_for_creative_task(self, task_content: str) -> str:
        """Estimate time for AI-generated creative tasks."""
        content_lower = task_content.lower()
        
        # High complexity tasks
        if any(word in content_lower for word in ['architecture', 'deployment', 'integration', 'comprehensive']):
            return '45-90 minutes'
        # Medium complexity tasks  
        elif any(word in content_lower for word in ['implement', 'create', 'develop', 'design']):
            return '30-60 minutes'
        # Research and analysis tasks
        elif any(word in content_lower for word in ['research', 'investigate', 'analyze']):
            return '20-40 minutes'
        # Setup and configuration tasks
        elif any(word in content_lower for word in ['setup', 'configure', 'install']):
            return '10-25 minutes'
        # Default
        else:
            return '15-30 minutes'

    def _create_development_subtasks(self, description: str, analysis: Dict) -> List[Dict]:
        """Create subtasks for development-type tasks."""
        subtasks = []
        
        # Always start with coordination for complex development tasks
        subtasks.append({
            'id': f'coordinate_{len(subtasks)+1}',
            'description': f"Plan and coordinate development approach for: {description}",
            'assigned_agent': AgentRole.COORDINATOR,
            'priority': 1,
            'estimated_time': '10-15 minutes'
        })
        
        # Research phase
        if AgentRole.RESEARCHER in analysis['required_agents'] or 'framework' in description.lower():
            subtasks.append({
                'id': f'research_{len(subtasks)+1}',
                'description': f"Research best practices and frameworks for: {description}",
                'assigned_agent': AgentRole.RESEARCHER,
                'priority': 2,
                'estimated_time': '15-30 minutes'
            })
        
        # File setup
        subtasks.append({
            'id': f'setup_{len(subtasks)+1}',
            'description': f"Set up project structure and files for: {description}",
            'assigned_agent': AgentRole.FILE_MANAGER,
            'priority': 3,
            'estimated_time': '10-20 minutes'
        })
        
        # Code generation - always needed for development
        subtasks.append({
            'id': f'generate_{len(subtasks)+1}',
            'description': f"Generate initial code implementation for: {description}",
            'assigned_agent': AgentRole.CODER,
            'priority': 4,
            'estimated_time': '30-60 minutes'
        })
        
        # Testing if mentioned or implied
        if 'test' in description.lower() or analysis['complexity'] != 'low':
            subtasks.append({
                'id': f'test_{len(subtasks)+1}',
                'description': f"Create and run tests for: {description}",
                'assigned_agent': AgentRole.TESTER,
                'priority': 5,
                'estimated_time': '20-40 minutes'
            })
        
        # Code review for quality assurance
        if analysis['complexity'] != 'low':
            subtasks.append({
                'id': f'review_{len(subtasks)+1}',
                'description': f"Review code quality and standards for: {description}",
                'assigned_agent': AgentRole.CODE_REVIEWER,
                'priority': 6,
                'estimated_time': '15-25 minutes'
            })
        
        return subtasks
    
    def _create_maintenance_subtasks(self, description: str, analysis: Dict) -> List[Dict]:
        """Create subtasks for maintenance-type tasks."""
        subtasks = []
        
        # Analysis phase
        subtasks.append({
            'id': f'analyze_{len(subtasks)+1}',
            'description': f"Analyze current state and identify issues for: {description}",
            'assigned_agent': AgentRole.CODE_REVIEWER,
            'priority': 1,
            'estimated_time': '10-20 minutes'
        })
        
        # Fix implementation
        if AgentRole.CODE_REWRITER in analysis['required_agents']:
            subtasks.append({
                'id': f'fix_{len(subtasks)+1}',
                'description': f"Implement fixes and improvements for: {description}",
                'assigned_agent': AgentRole.CODE_REWRITER,
                'priority': 2,
                'estimated_time': '15-30 minutes'
            })
        
        return subtasks
    
    def _create_research_subtasks(self, description: str, analysis: Dict) -> List[Dict]:
        """Create subtasks for research-type tasks."""
        subtasks = []
        
        subtasks.append({
            'id': f'research_{len(subtasks)+1}',
            'description': f"Conduct comprehensive research on: {description}",
            'assigned_agent': AgentRole.RESEARCHER,
            'priority': 1,
            'estimated_time': '20-40 minutes'
        })
        
        subtasks.append({
            'id': f'document_{len(subtasks)+1}',
            'description': f"Document research findings and recommendations for: {description}",
            'assigned_agent': AgentRole.FILE_MANAGER,
            'priority': 2,
            'estimated_time': '10-15 minutes'
        })
        
        return subtasks
    
    def _create_testing_subtasks(self, description: str, analysis: Dict) -> List[Dict]:
        """Create subtasks for testing-type tasks."""
        subtasks = []
        
        subtasks.append({
            'id': f'test_plan_{len(subtasks)+1}',
            'description': f"Create test strategy and plan for: {description}",
            'assigned_agent': AgentRole.TESTER,
            'priority': 1,
            'estimated_time': '15-25 minutes'
        })
        
        subtasks.append({
            'id': f'test_impl_{len(subtasks)+1}',
            'description': f"Implement and execute tests for: {description}",
            'assigned_agent': AgentRole.TESTER,
            'priority': 2,
            'estimated_time': '25-45 minutes'
        })
        
        return subtasks
    
    def _create_generic_subtasks(self, description: str, analysis: Dict) -> List[Dict]:
        """Create generic subtasks when task type is unclear."""
        subtasks = []
        
        # Always start with coordination
        subtasks.append({
            'id': f'coordinate_{len(subtasks)+1}',
            'description': f"Coordinate and plan approach for: {description}",
            'assigned_agent': AgentRole.COORDINATOR,
            'priority': 1,
            'estimated_time': '10-15 minutes'
        })
        
        # If no specific agents identified, use general approach
        if not analysis['required_agents']:
            subtasks.append({
                'id': f'analyze_{len(subtasks)+1}',
                'description': f"Analyze requirements and approach for: {description}",
                'assigned_agent': AgentRole.RESEARCHER,
                'priority': 2,
                'estimated_time': '15-25 minutes'
            })
            
            subtasks.append({
                'id': f'implement_{len(subtasks)+1}',
                'description': f"Implement solution for: {description}",
                'assigned_agent': AgentRole.CODER,
                'priority': 3,
                'estimated_time': '20-40 minutes'
            })
        else:
            # Add subtasks based on identified agents
            for i, agent in enumerate(analysis['required_agents']):
                if agent != AgentRole.COORDINATOR:
                    subtasks.append({
                        'id': f'execute_{len(subtasks)+1}',
                        'description': f"Execute {agent.value} tasks for: {description}",
                        'assigned_agent': agent,
                        'priority': i + 2,
                        'estimated_time': '15-30 minutes'
                    })
        
        return subtasks
    
    def _assign_priorities_and_dependencies(self, subtasks: List[Dict]):
        """Assign priorities and dependencies to subtasks."""
        for i, subtask in enumerate(subtasks):
            if i > 0:
                subtask['depends_on'] = [subtasks[i-1]['id']]
            else:
                subtask['depends_on'] = []
    
    def _estimate_duration(self, subtasks: List[Dict]) -> str:
        """Estimate total duration for all subtasks."""
        total_min = sum(self._parse_time_estimate(task.get('estimated_time', '15-30 minutes')) 
                       for task in subtasks)
        hours = total_min // 60
        minutes = total_min % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def _parse_time_estimate(self, time_str: str) -> int:
        """Parse time estimate string and return average minutes."""
        if '-' in time_str:
            parts = time_str.split('-')
            min_time = int(re.search(r'\d+', parts[0]).group())
            max_time = int(re.search(r'\d+', parts[1]).group())
            return (min_time + max_time) // 2
        else:
            return int(re.search(r'\d+', time_str).group())
    
    def _organize_phases(self, subtasks: List[Dict]) -> List[Dict]:
        """Organize subtasks into execution phases."""
        phases = []
        current_phase = []
        
        for subtask in subtasks:
            if not subtask.get('depends_on') or not current_phase:
                if current_phase:
                    phases.append({
                        'phase': len(phases) + 1,
                        'tasks': current_phase.copy(),
                        'can_run_parallel': len(current_phase) > 1
                    })
                current_phase = [subtask]
            else:
                current_phase.append(subtask)
        
        if current_phase:
            phases.append({
                'phase': len(phases) + 1,
                'tasks': current_phase,
                'can_run_parallel': len(current_phase) > 1
            })
        
        return phases
    
    def _assess_risks(self, subtasks: List[Dict]) -> List[str]:
        """Assess potential risks in the execution plan."""
        risks = []
        
        if len(subtasks) > 8:
            risks.append("High complexity - many subtasks may lead to coordination challenges")
        
        # Handle both old and new task formats
        agent_types = set()
        for task in subtasks:
            if 'assigned_agent' in task:
                agent_types.add(task['assigned_agent'])
            elif 'assigned_to' in task:
                agent_types.add(task['assigned_to'])
        
        if len(agent_types) > 5:
            risks.append("Multiple agent coordination required - potential for conflicts")
        
        if any(task.get('estimated_time', '').endswith('45 minutes') for task in subtasks):
            risks.append("Some tasks have high time estimates - potential for delays")
        
        return risks
    
    def _define_success_criteria(self, description: str, ai_consultation: Dict = None) -> List[str]:
        """Define success criteria for the task with AI insights."""
        criteria = [
            "All subtasks completed successfully",
            "No critical errors or failures", 
            "Task requirements met as specified",
            "Coordinator agents successfully executed delegated tasks"
        ]
        
        if 'test' in description.lower():
            criteria.append("All tests passing with adequate coverage")
        
        if 'deploy' in description.lower():
            criteria.append("Successful deployment with no rollback needed")
        
        # AI-specific success criteria
        if ai_consultation:
            project_type = ai_consultation.get('project_type')
            
            if project_type == 'web_development':
                criteria.extend([
                    "Frontend components are responsive and accessible",
                    "Backend API follows RESTful best practices",
                    "Application follows modern web development standards"
                ])
            elif project_type == 'mobile_development':
                criteria.extend([
                    "App follows platform-specific design guidelines",
                    "Performance optimized for mobile devices",
                    "Offline functionality works as expected"
                ])
            elif project_type == 'api_development':
                criteria.extend([
                    "API endpoints are properly documented",
                    "Authentication and security measures implemented",
                    "Rate limiting and error handling in place"
                ])
            elif project_type == 'data_science':
                criteria.extend([
                    "Data pipeline is robust and reproducible",
                    "Model performance meets accuracy requirements",
                    "Results are properly validated and documented"
                ])
            
            # Add technology-specific criteria
            technologies = ai_consultation.get('technologies', [])
            if 'react' in technologies:
                criteria.append("React components follow hooks and modern patterns")
            if 'node.js' in technologies:
                criteria.append("Node.js server follows async/await best practices")
            if 'mongodb' in technologies or 'postgresql' in technologies:
                criteria.append("Database operations are optimized and secure")
        
        return criteria

    def print_execution_plan(self, plan: Dict[str, Any]):
        """Print execution plan formatted for easy copy-paste to coordinator."""
        colored_print(f"\n{'='*80}", Colors.CYAN)
        colored_print(f"COORDINATOR-READY EXECUTION PLAN: {plan['original_task']}", Colors.CYAN)
        colored_print(f"{'='*80}", Colors.CYAN)
        
        # Display AI consultation if available
        if 'ai_consultation' in plan and plan['ai_consultation']['project_type']:
            ai_info = plan['ai_consultation']
            colored_print(f"\nAI CONSULTATION RESULTS:", Colors.MAGENTA)
            colored_print(f"  Project Type: {ai_info['project_type']}", Colors.WHITE)
            colored_print(f"  Technologies: {', '.join(ai_info.get('technologies', ['N/A']))}", Colors.WHITE)
            
            # Show AI-recommended file structure in coordinator format
            if ai_info.get('file_structure'):
                colored_print(f"\nAI FILE STRUCTURE (for file_manager):", Colors.BRIGHT_YELLOW)
                file_structure = ai_info['file_structure']
                for directory, contents in file_structure.items():
                    if isinstance(contents, list):
                        colored_print(f"  {directory}", Colors.YELLOW)
                        for item in contents:
                            colored_print(f"    {item}", Colors.WHITE)
        
        colored_print(f"\nCOPY-PASTE READY TASKS FOR COORDINATOR:", Colors.BRIGHT_GREEN)
        colored_print(f"Total: {plan['total_subtasks']} tasks | Duration: {plan['estimated_duration']}", Colors.WHITE)
        
        # Format tasks for easy coordinator copy-paste
        task_counter = 1
        for phase in plan['execution_phases']:
            for task in phase['tasks']:
                agent_name = task.get('assigned_to', task.get('assigned_agent', 'unknown'))
                
                colored_print(f"\n[{task_counter}] <{agent_name}>", Colors.BRIGHT_CYAN)
                colored_print(f"    {task['description']}", Colors.WHITE)
                colored_print(f"    Time: {task['estimated_time']} | Priority: {task['priority']}", Colors.CYAN)
                
                # Add special instructions for coordinator understanding
                task_type = task.get('task_type', 'general')
                if task_type == 'file_management':
                    colored_print(f"    File Operations Task", Colors.YELLOW)
                elif task_type == 'code_generation':
                    colored_print(f"    Code Development Task", Colors.YELLOW)
                elif task_type == 'research':
                    colored_print(f"    Research & Analysis Task", Colors.YELLOW)
                elif task_type == 'testing':
                    colored_print(f"    Testing & Validation Task", Colors.YELLOW)
                elif task_type == 'code_review':
                    colored_print(f"    Code Review Task", Colors.YELLOW)
                elif task_type == 'git_management':
                    colored_print(f"    Git Operations Task", Colors.YELLOW)
                elif task_type == 'code_rewrite':
                    colored_print(f"    Code Improvement Task", Colors.YELLOW)
                
                task_counter += 1
        
        # Coordinator execution format
        colored_print(f"\nCOORDINATOR EXECUTION FORMAT:", Colors.BRIGHT_MAGENTA)
        colored_print("Copy these commands to coordinator terminal:", Colors.WHITE)
        
        execution_commands = []
        for i, phase in enumerate(plan['execution_phases']):
            for task in phase['tasks']:
                agent = task.get('assigned_to', 'unknown')
                cmd = f'delegate "{task["description"]}" to {agent}'
                execution_commands.append(cmd)
        
        # Show first 3 commands as examples
        for i, cmd in enumerate(execution_commands[:3]):
            colored_print(f"  {i+1}. {cmd}", Colors.CYAN)
        
        if len(execution_commands) > 3:
            colored_print(f"  ... and {len(execution_commands) - 3} more tasks", Colors.WHITE)
        
        # File structure setup command
        if 'ai_consultation' in plan and plan['ai_consultation'].get('file_structure'):
            colored_print(f"\nFILE STRUCTURE SETUP:", Colors.BRIGHT_YELLOW)
            colored_print(f'  delegate "Set up project structure according to AI recommendations" to file_manager', Colors.CYAN)
            
            # Show the structure the coordinator should expect
            ai_info = plan['ai_consultation']
            if ai_info.get('project_type'):
                colored_print(f"  Project type: {ai_info['project_type']}", Colors.WHITE)
                colored_print(f"  Structure includes: {len(ai_info.get('file_structure', {}))} main directories", Colors.WHITE)
        
        if plan.get('risk_assessment'):
            colored_print(f"\nCOORDINATOR WARNINGS:", Colors.RED)
            for risk in plan['risk_assessment']:
                colored_print(f"  • {risk}", Colors.YELLOW)
        
        colored_print(f"\nSUCCESS VALIDATION FOR COORDINATOR:", Colors.GREEN)
        for criteria in plan['success_criteria']:
            colored_print(f"  • {criteria}", Colors.WHITE)
        
        colored_print(f"\n{'='*80}", Colors.CYAN)
        colored_print(f"READY FOR COORDINATOR EXECUTION", Colors.BRIGHT_GREEN)
        colored_print(f"{'='*80}\n", Colors.CYAN)

    def generate_coordinator_commands(self, description: str) -> Dict[str, Any]:
        """
        Generate copy-paste ready commands for the coordinator agent.
        
        Args:
            description: Task description
            
        Returns:
            Dictionary with formatted commands and file structure info
        """
        colored_print(f"[HELPER] Generating coordinator commands...", Colors.MAGENTA)
        
        execution_plan = self.create_execution_plan(description)
        
        # Generate delegate commands
        delegate_commands = []
        file_structure_info = {}
        
        for task in execution_plan['subtasks']:
            agent = task.get('assigned_to', 'unknown')
            task_desc = task['description']
            
            # Format as coordinator delegate command
            command = f'<{agent}> "{task_desc}"'
            delegate_commands.append({
                'command': command,
                'agent': agent,
                'description': task_desc,
                'task_type': task.get('task_type', 'general'),
                'estimated_time': task.get('estimated_time', '15-30 minutes'),
                'priority': task.get('priority', 1)
            })
        
        # Extract file structure information
        if execution_plan.get('ai_consultation', {}).get('file_structure'):
            ai_consultation = execution_plan['ai_consultation']
            file_structure_info = {
                'project_type': ai_consultation.get('project_type'),
                'structure': ai_consultation.get('file_structure'),
                'technologies': ai_consultation.get('technologies', []),
                'setup_command': f'<file_manager> "Set up {ai_consultation.get("project_type", "project")} file structure with directories: {", ".join(ai_consultation.get("recommended_structure", []))}"'
            }
        
        coordinator_package = {
            'original_task': description,
            'delegate_commands': delegate_commands,
            'file_structure': file_structure_info,
            'execution_summary': {
                'total_tasks': len(delegate_commands),
                'estimated_duration': execution_plan['estimated_duration'],
                'agents_involved': list(set(cmd['agent'] for cmd in delegate_commands)),
                'complexity': len(delegate_commands)
            },
            'coordinator_instructions': self._generate_coordinator_instructions(execution_plan)
        }
        
        return coordinator_package

    def _generate_coordinator_instructions(self, execution_plan: Dict) -> List[str]:
        """Generate specific instructions for the coordinator to understand the plan."""
        instructions = []
        
        ai_info = execution_plan.get('ai_consultation', {})
        project_type = ai_info.get('project_type')
        
        if project_type == 'web_development':
            instructions.extend([
                "This is a web development project requiring frontend and backend coordination",
                "Start with research and file structure setup before code generation",
                "Ensure proper testing after implementation phases",
                "Consider deployment pipeline as final step"
            ])
        elif project_type == 'mobile_development':
            instructions.extend([
                "Mobile app development project with platform-specific considerations",
                "Focus on responsive UI and device API integration",
                "Testing should include multiple device types and screen sizes",
                "App store deployment requirements should be considered"
            ])
        elif project_type == 'api_development':
            instructions.extend([
                "API development project requiring backend focus",
                "Prioritize authentication and security implementation",
                "Ensure proper documentation generation",
                "Include comprehensive testing for all endpoints"
            ])
        elif project_type == 'data_science':
            instructions.extend([
                "Data science project requiring pipeline approach",
                "Data collection and cleaning should precede analysis",
                "Model development requires iterative approach",
                "Results validation and documentation are critical"
            ])
        else:
            instructions.extend([
                "General project requiring multi-agent coordination",
                "Follow the suggested task order for dependencies",
                "Monitor progress and adjust as needed",
                "Ensure quality assurance throughout process"
            ])
        
        # Add technology-specific instructions
        technologies = ai_info.get('technologies', [])
        if 'react' in technologies:
            instructions.append("React components should follow modern hooks patterns")
        if 'node.js' in technologies:
            instructions.append("Node.js development should use async/await patterns")
        if 'fastapi' in technologies:
            instructions.append("FastAPI should include automatic OpenAPI documentation")
        
        return instructions

    def print_coordinator_commands(self, description: str):
        """Print copy-paste ready commands for coordinator execution."""
        coordinator_package = self.generate_coordinator_commands(description)
        
        colored_print(f"\n{'='*60}", Colors.BRIGHT_GREEN)
        colored_print(f"COORDINATOR COPY-PASTE COMMANDS", Colors.BRIGHT_GREEN)
        colored_print(f"{'='*60}", Colors.BRIGHT_GREEN)
        
        colored_print(f"\nOriginal Task: {coordinator_package['original_task']}", Colors.CYAN)
        
        # File structure setup (if applicable)
        if coordinator_package['file_structure']:
            fs_info = coordinator_package['file_structure']
            colored_print(f"\nSTEP 1: FILE STRUCTURE SETUP", Colors.BRIGHT_YELLOW)
            colored_print(f"{fs_info['setup_command']}", Colors.WHITE)
            colored_print(f"Project Type: {fs_info['project_type']}", Colors.CYAN)
            colored_print(f"Technologies: {', '.join(fs_info['technologies'])}", Colors.CYAN)
        
        # Delegate commands
        colored_print(f"\nSTEP 2: TASK DELEGATION COMMANDS", Colors.BRIGHT_YELLOW)
        for i, cmd in enumerate(coordinator_package['delegate_commands'], 1):
            colored_print(f"\n[{i}] {cmd['command']}", Colors.WHITE)
            colored_print(f"    Type: {cmd['task_type']} | Time: {cmd['estimated_time']}", Colors.CYAN)
        
        # Coordinator instructions
        colored_print(f"\nCOORDINATOR EXECUTION NOTES:", Colors.BRIGHT_MAGENTA)
        for instruction in coordinator_package['coordinator_instructions']:
            colored_print(f"  • {instruction}", Colors.WHITE)
        
        # Summary
        summary = coordinator_package['execution_summary']
        colored_print(f"\nEXECUTION SUMMARY:", Colors.YELLOW)
        colored_print(f"  Total Tasks: {summary['total_tasks']}", Colors.WHITE)
        colored_print(f"  Duration: {summary['estimated_duration']}", Colors.WHITE)
        colored_print(f"  Agents: {', '.join(summary['agents_involved'])}", Colors.WHITE)
        
        colored_print(f"\n{'='*60}", Colors.BRIGHT_GREEN)
        colored_print(f"READY FOR COORDINATOR EXECUTION!", Colors.BRIGHT_GREEN)
        colored_print(f"{'='*60}\n", Colors.BRIGHT_GREEN)
    
    def _infer_precise_task_type(self, description: str) -> str:
        """Infer precise task type from enhanced description"""
        desc_lower = description.lower()
        
        # More specific task type detection
        if any(word in desc_lower for word in ['create', 'implement', 'generate', 'build']):
            if any(word in desc_lower for word in ['component', 'function', 'class', 'module']):
                return 'code_generation'
            elif any(word in desc_lower for word in ['file', 'directory', 'structure']):
                return 'file_management'
        elif any(word in desc_lower for word in ['review', 'analyze', 'check', 'audit']):
            return 'code_review'
        elif any(word in desc_lower for word in ['fix', 'refactor', 'update', 'modify', 'edit']):
            return 'code_rewrite'
        elif any(word in desc_lower for word in ['test', 'validate', 'verify']):
            return 'testing'
        elif any(word in desc_lower for word in ['setup', 'configure', 'install', 'initialize']):
            return 'file_management'
        
        return 'code_generation'  # Default
    
    def _calculate_ai_task_priority(self, task: str, index: int, total_tasks: int) -> int:
        """Calculate priority for AI-generated tasks"""
        task_lower = task.lower()
        
        # Setup and initialization tasks get high priority
        if index == 0 or any(word in task_lower for word in ['setup', 'initialize', 'configure']):
            return 3
        
        # Critical functionality
        if any(word in task_lower for word in ['critical', 'core', 'main', 'primary']):
            return 3
        
        # Testing and documentation typically lower priority
        if any(word in task_lower for word in ['test', 'document', 'optional']):
            return 1
        
        # Everything else medium priority
        return 2
    
    def _estimate_precise_time(self, description: str) -> str:
        """Provide more precise time estimates"""
        desc_lower = description.lower()
        
        # Complex operations
        if any(word in desc_lower for word in ['complex', 'integration', 'system', 'architecture']):
            return '45-90 minutes'
        
        # Setup and configuration
        elif any(word in desc_lower for word in ['setup', 'configure', 'install', 'initialize']):
            return '15-30 minutes'
        
        # Component creation
        elif 'component' in desc_lower:
            return '25-45 minutes'
        
        # Simple file operations
        elif any(word in desc_lower for word in ['file', 'simple', 'basic', 'quick']):
            return '10-20 minutes'
        
        # Testing
        elif 'test' in desc_lower:
            return '20-35 minutes'
        
        # Default
        else:
            return '20-40 minutes'
    
    def _identify_precise_dependencies(self, description: str, task_index: int) -> List[str]:
        """Identify precise task dependencies"""
        desc_lower = description.lower()
        dependencies = []
        
        # Tasks that depend on setup
        if task_index > 0 and any(word in desc_lower for word in ['component', 'function', 'feature']):
            dependencies.append('project_setup')
        
        # Styling depends on component creation
        if 'style' in desc_lower or 'css' in desc_lower:
            dependencies.append('component_creation')
        
        # Testing depends on implementation
        if 'test' in desc_lower:
            dependencies.append('implementation_complete')
        
        # API integration depends on backend setup
        if 'api' in desc_lower and 'connect' in desc_lower:
            dependencies.append('backend_setup')
        
        return dependencies
    
    def _get_enhanced_task_template(self, task_type: str, description: str) -> List[Dict]:
        """Get enhanced task templates with more specificity"""
        desc_lower = description.lower()
        
        if task_type == 'development':
            if 'react' in desc_lower or 'frontend' in desc_lower:
                return [
                    {'description': 'Setup and initialize React project structure with necessary dependencies', 
                     'type': 'file_management', 'priority': 3, 'time': '20 minutes'},
                    {'description': 'Create and implement core React components with proper props and state management', 
                     'type': 'code_generation', 'priority': 2, 'time': '35 minutes'},
                    {'description': 'Implement styling and responsive design using CSS/SCSS modules', 
                     'type': 'code_generation', 'priority': 2, 'time': '25 minutes', 'depends_on': ['component_creation']},
                    {'description': 'Add error handling, validation, and user feedback mechanisms', 
                     'type': 'code_generation', 'priority': 2, 'time': '20 minutes'},
                    {'description': 'Write comprehensive unit tests using Jest and React Testing Library', 
                     'type': 'code_generation', 'priority': 1, 'time': '30 minutes', 'depends_on': ['implementation_complete']}
                ]
            elif 'backend' in desc_lower or 'api' in desc_lower:
                return [
                    {'description': 'Setup Node.js/Express server with project structure and dependencies', 
                     'type': 'file_management', 'priority': 3, 'time': '25 minutes'},
                    {'description': 'Implement RESTful API endpoints with proper routing and middleware', 
                     'type': 'code_generation', 'priority': 2, 'time': '40 minutes'},
                    {'description': 'Add database integration with connection handling and models', 
                     'type': 'code_generation', 'priority': 2, 'time': '35 minutes'},
                    {'description': 'Implement authentication, authorization, and security measures', 
                     'type': 'code_generation', 'priority': 2, 'time': '30 minutes'},
                    {'description': 'Add comprehensive API testing and documentation', 
                     'type': 'code_generation', 'priority': 1, 'time': '25 minutes'}
                ]
        
        # Default enhanced template
        return [
            {'description': 'Analyze requirements and setup project foundation', 
             'type': 'file_management', 'priority': 3, 'time': '15 minutes'},
            {'description': 'Implement core functionality with proper architecture', 
             'type': 'code_generation', 'priority': 2, 'time': '30 minutes'},
            {'description': 'Add validation, error handling, and user experience enhancements', 
             'type': 'code_generation', 'priority': 2, 'time': '20 minutes'},
            {'description': 'Write tests and verify functionality integration', 
             'type': 'code_generation', 'priority': 1, 'time': '25 minutes'}
        ]
    
    def _apply_context_to_template(self, template_task: Dict, original_description: str, analysis: Dict) -> str:
        """Apply specific context to template task descriptions"""
        description = template_task['description']
        original_lower = original_description.lower()
        
        # Replace generic terms with specific context
        if 'project' in description and 'react' in original_lower:
            description = description.replace('project', 'React project')
        elif 'project' in description and 'node' in original_lower:
            description = description.replace('project', 'Node.js project')
        
        # Add specific technology context
        if 'component' in description and 'todo' in original_lower:
            description = description.replace('components', 'todo management components')
        elif 'api' in description and 'todo' in original_lower:
            description = description.replace('API endpoints', 'todo management API endpoints')
        
        # Add file path specificity
        if 'setup' in description:
            if 'react' in original_lower:
                description += ' in src/ directory with components/, styles/, and utils/ folders'
            elif 'node' in original_lower:
                description += ' with routes/, models/, and middleware/ directories'
        
        return description
    
    def _adjust_time_for_complexity(self, base_time: str, complexity: str) -> str:
        """Adjust time estimates based on complexity assessment"""
        if complexity == 'high':
            return base_time.replace('15', '25').replace('20', '35').replace('30', '50')
        elif complexity == 'low':
            return base_time.replace('25', '15').replace('30', '20').replace('40', '25')
        else:
            return base_time
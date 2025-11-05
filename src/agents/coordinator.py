"""
Coordinator Agent - Smart task delegation and agent coordination with AI-powered workflow management
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

from ..core.base_agent import BaseAgent, TaskInput, TaskResult
from ..core.models import AgentRole, TaskStatus, Colors
from ..core.utils import colored_print


class CoordinatorAgent(BaseAgent):
    """
    Smart coordinator agent for intelligent task delegation and multi-agent workflow orchestration.
    Uses AI to analyze tasks, determine optimal agent assignments, and manage complex workflows.
    """
    
    def __init__(self, agent_id: str, workspace_dir: str, **kwargs):
        super().__init__(agent_id, AgentRole.COORDINATOR, workspace_dir, **kwargs)
        
        # Delegation strategy configuration
        self.delegation_history = []
        self.agent_performance_metrics = {}
        self.active_workflows = {}
        
        # Agent role mapping with capabilities
        self.agent_capabilities = {
            'file_manager': ['file_creation', 'file_modification', 'directory_management', 'project_scaffolding'],
            'coder': ['code_generation', 'implementation', 'development', 'programming'],
            'code_reviewer': ['code_review', 'quality_analysis', 'security_analysis', 'best_practices'],
            'code_rewriter': ['code_refactoring', 'bug_fixing', 'code_improvement', 'optimization'],
            'git_manager': ['version_control', 'git_operations', 'branch_management', 'commit_management'],
            'tester': ['testing', 'unit_testing', 'integration_testing', 'test_generation'],
            'researcher': ['research', 'investigation', 'documentation_search', 'knowledge_gathering'],
            'helper_agent': ['assistance', 'guidance', 'support', 'coordination_help']
        }
        
        colored_print(f"Smart Coordinator '{agent_id}' ready for intelligent task delegation", Colors.BRIGHT_CYAN)
    
    def _define_capabilities(self) -> Dict[str, bool]:
        """Define coordinator-specific capabilities"""
        return {
            'task_delegation': True,
            'workflow_orchestration': True,
            'agent_coordination': True,
            'complexity_analysis': True,
            'multi_step_planning': True,
            'agent_monitoring': True,
            'ai_powered_delegation': True
        }
    
    def _execute_specific_task(self, task_input: TaskInput, context: Dict) -> TaskResult:
        """
        Execute coordinator-specific task - intelligent delegation and workflow management
        """
        description = task_input.description
        task_type = task_input.task_type
        
        colored_print(f"Coordinator analyzing task for optimal delegation", Colors.BRIGHT_CYAN)
        colored_print(f"  Task: {description}", Colors.CYAN)
        
        # Analyze task complexity
        complexity_analysis = self._analyze_task_complexity(description, context)
        
        # Determine delegation strategy
        if complexity_analysis['complexity_level'] == 'high' or complexity_analysis['requires_multiple_agents']:
            # Create multi-step workflow
            result = self._create_multi_step_workflow(task_input, complexity_analysis, context)
        else:
            # Simple single-agent delegation
            result = self._delegate_to_single_agent(task_input, complexity_analysis, context)
        
        # Track delegation
        self._track_delegation(task_input, result)
        
        return result
    
    def _analyze_task_complexity(self, description: str, context: Dict) -> Dict[str, Any]:
        """
        Use AI to analyze task complexity and determine required agents.
        Smart, not hard-coded - adapts to any task description.
        """
        desc_lower = description.lower()
        
        # Use AI to analyze task if enabled
        if self.enable_ai_fallback:
            ai_analysis = self._ai_analyze_task(description, context)
            if ai_analysis:
                return ai_analysis
        
        # Fallback: intelligent keyword-based analysis
        analysis = {
            'complexity_score': 0,
            'complexity_level': 'low',
            'required_agents': [],
            'requires_multiple_agents': False,
            'suggested_workflow': [],
            'estimated_time': 'unknown',
            'reasoning': []
        }
        
        # Identify required agent capabilities
        for agent_role, capabilities in self.agent_capabilities.items():
            for capability in capabilities:
                if any(keyword in desc_lower for keyword in capability.split('_')):
                    if agent_role not in analysis['required_agents']:
                        analysis['required_agents'].append(agent_role)
                        analysis['reasoning'].append(f"{agent_role}: detected '{capability}' requirement")
        
        # Calculate complexity
        complexity_indicators = [
            ('multiple', 2), ('complex', 2), ('integrate', 2), ('full', 2),
            ('complete', 2), ('entire', 2), ('system', 1), ('application', 2),
            ('project', 2), ('deploy', 2), ('production', 2), ('test', 1),
            ('review', 1), ('refactor', 1), ('optimize', 1)
        ]
        
        for keyword, weight in complexity_indicators:
            if keyword in desc_lower:
                analysis['complexity_score'] += weight
        
        # Determine complexity level
        if analysis['complexity_score'] >= 6 or len(analysis['required_agents']) >= 3:
            analysis['complexity_level'] = 'high'
        elif analysis['complexity_score'] >= 3 or len(analysis['required_agents']) >= 2:
            analysis['complexity_level'] = 'medium'
        else:
            analysis['complexity_level'] = 'low'
        
        analysis['requires_multiple_agents'] = len(analysis['required_agents']) > 1
        
        return analysis
    
    def _ai_analyze_task(self, description: str, context: Dict) -> Optional[Dict]:
        """
        Use AI to intelligently analyze task requirements and suggest agent delegation.
        This makes the coordinator truly smart and adaptive.
        """
        try:
            # Build AI prompt for task analysis
            prompt = f"""Analyze this development task and determine which specialized agents should handle it:

Task: {description}

Available agents and their capabilities:
{json.dumps(self.agent_capabilities, indent=2)}

Active agents in system:
{json.dumps([a['id'] for a in self.comm.get_active_agents()], indent=2)}

Analyze:
1. Which agents are needed for this task?
2. What is the complexity level (low/medium/high)?
3. Should this be a single-agent or multi-agent workflow?
4. What is the suggested execution order?

Respond ONLY with a JSON object in this format:
{{
    "required_agents": ["agent1", "agent2"],
    "complexity_level": "medium",
    "requires_multiple_agents": false,
    "suggested_workflow": ["step1", "step2"],
    "reasoning": ["reason1", "reason2"]
}}"""
            
            # Get AI analysis
            response = self.ai_client.generate(
                prompt=prompt,
                model=self.default_model,
                stream=False
            )
            
            if response and 'response' in response:
                # Parse JSON response
                response_text = response['response'].strip()
                
                # Extract JSON from response (handle markdown code blocks)
                if '```json' in response_text:
                    response_text = response_text.split('```json')[1].split('```')[0].strip()
                elif '```' in response_text:
                    response_text = response_text.split('```')[1].split('```')[0].strip()
                
                ai_result = json.loads(response_text)
                
                # Add complexity score based on level
                score_map = {'low': 2, 'medium': 5, 'high': 8}
                ai_result['complexity_score'] = score_map.get(ai_result.get('complexity_level', 'low'), 2)
                
                colored_print("  AI analysis completed successfully", Colors.GREEN)
                return ai_result
                
        except Exception as e:
            colored_print(f"  AI analysis failed, using fallback: {e}", Colors.YELLOW)
        
        return None
    
    def _delegate_to_single_agent(self, task_input: TaskInput, analysis: Dict, context: Dict) -> TaskResult:
        """
        Delegate task to a single best-matched agent.
        Smart agent selection based on task requirements.
        """
        # Determine best agent
        target_agent = self._select_best_agent(task_input.description, analysis)
        
        if not target_agent:
            target_agent = 'coder'  # Default fallback
        
        # Check if target agent is active
        active_agents = self.comm.get_active_agents()
        agent_ids = [a['id'] for a in active_agents]
        
        if target_agent not in [a['role'] for a in active_agents]:
            colored_print(f"  Warning: {target_agent} not active, task may be queued", Colors.YELLOW)
        
        # Create task for target agent
        task_id = self.comm.create_task(
            task_type=task_input.task_type,
            description=task_input.description,
            assigned_to=target_agent,
            created_by=self.agent_id,
            priority=task_input.priority,
            data={
                'analysis': analysis,
                'context': task_input.get_all_inputs(),
                'delegated_at': datetime.now().isoformat()
            }
        )
        
        colored_print(f"  Delegated task {task_id} -> {target_agent}", Colors.GREEN)
        
        return TaskResult(
            success=True,
            message=f"Task delegated to {target_agent}",
            data={
                'delegated_task_id': task_id,
                'delegated_to': target_agent,
                'analysis': analysis
            },
            delegated_tasks=[task_id],
            metadata={'delegation_type': 'single_agent'}
        )
    
    def _select_best_agent(self, description: str, analysis: Dict) -> str:
        """
        Select the best agent for a task based on intelligent analysis.
        Not hard-coded - uses the analysis results.
        """
        required_agents = analysis.get('required_agents', [])
        
        if not required_agents:
            # Try to infer from description
            desc_lower = description.lower()
            
            # Priority-based matching
            if any(word in desc_lower for word in ['file', 'directory', 'folder', 'create', 'organize']):
                return 'file_manager'
            elif any(word in desc_lower for word in ['git', 'commit', 'push', 'branch', 'version']):
                return 'git_manager'
            elif any(word in desc_lower for word in ['test', 'testing', 'unit', 'integration']):
                return 'tester'
            elif any(word in desc_lower for word in ['review', 'check', 'analyze', 'quality']):
                return 'code_reviewer'
            elif any(word in desc_lower for word in ['fix', 'rewrite', 'refactor', 'improve']):
                return 'code_rewriter'
            elif any(word in desc_lower for word in ['research', 'find', 'search', 'investigate']):
                return 'researcher'
            elif any(word in desc_lower for word in ['code', 'implement', 'develop', 'generate']):
                return 'coder'
            
            return 'coder'  # Default
        
        # Return first required agent (or use priority logic)
        return required_agents[0]
    
    def _create_multi_step_workflow(self, task_input: TaskInput, analysis: Dict, context: Dict) -> TaskResult:
        """
        Create intelligent multi-step workflow for complex tasks.
        Adapts based on AI analysis, not hard-coded.
        """
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        required_agents = analysis.get('required_agents', [])
        
        colored_print(f"  Creating multi-step workflow: {workflow_id}", Colors.BRIGHT_YELLOW)
        colored_print(f"    Complexity: {analysis['complexity_level']}", Colors.YELLOW)
        colored_print(f"    Required agents: {', '.join(required_agents)}", Colors.YELLOW)
        
        workflow_steps = []
        delegated_task_ids = []
        
        # Create workflow steps based on logical agent order
        agent_priority_order = [
            'researcher',      # Research first
            'file_manager',    # Setup structure
            'coder',          # Implementation
            'code_reviewer',  # Review
            'code_rewriter',  # Fix issues
            'tester',         # Testing
            'git_manager'     # Version control
        ]
        
        step_num = 1
        for agent_role in agent_priority_order:
            if agent_role in required_agents:
                # Create step-specific description
                step_description = self._generate_step_description(
                    agent_role, task_input.description, step_num, len(required_agents)
                )
                
                # Create task for this step
                task_id = self.comm.create_task(
                    task_type=f"{agent_role}_step",
                    description=step_description,
                    assigned_to=agent_role,
                    created_by=self.agent_id,
                    priority=step_num,
                    data={
                        'workflow_id': workflow_id,
                        'step_number': step_num,
                        'total_steps': len(required_agents),
                        'original_task': task_input.description
                    }
                )
                
                workflow_steps.append({
                    'step': step_num,
                    'task_id': task_id,
                    'agent': agent_role,
                    'description': step_description,
                    'status': 'pending'
                })
                
                delegated_task_ids.append(task_id)
                
                colored_print(f"    Step {step_num}: {agent_role} - Task {task_id}", Colors.CYAN)
                step_num += 1
        
        # Store workflow
        self.active_workflows[workflow_id] = {
            'created_at': datetime.now().isoformat(),
            'original_task': task_input.description,
            'steps': workflow_steps,
            'status': 'active',
            'analysis': analysis
        }
        
        return TaskResult(
            success=True,
            message=f"Multi-step workflow created with {len(workflow_steps)} steps",
            data={
                'workflow_id': workflow_id,
                'total_steps': len(workflow_steps),
                'workflow_steps': workflow_steps,
                'analysis': analysis
            },
            delegated_tasks=delegated_task_ids,
            metadata={'delegation_type': 'multi_step_workflow'}
        )
    
    def _generate_step_description(self, agent_role: str, original_description: str, step_num: int, total_steps: int) -> str:
        """Generate intelligent step description for workflow steps"""
        
        step_templates = {
            'researcher': f"Research and gather requirements for: {original_description}",
            'file_manager': f"Set up file structure and scaffolding for: {original_description}",
            'coder': f"Implement code for: {original_description}",
            'code_reviewer': f"Review and analyze code quality for: {original_description}",
            'code_rewriter': f"Fix issues and refactor code for: {original_description}",
            'tester': f"Create and run tests for: {original_description}",
            'git_manager': f"Manage version control for: {original_description}"
        }
        
        template = step_templates.get(agent_role, f"Execute {agent_role} tasks for: {original_description}")
        return f"[Step {step_num}/{total_steps}] {template}"
    
    def _track_delegation(self, task_input: TaskInput, result: TaskResult):
        """Track delegation history for performance analysis"""
        self.delegation_history.append({
            'timestamp': datetime.now().isoformat(),
            'task_description': task_input.description,
            'delegation_type': result.metadata.get('delegation_type'),
            'success': result.success,
            'delegated_tasks': result.delegated_tasks
        })
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict]:
        """Get status of a specific workflow"""
        return self.active_workflows.get(workflow_id)
    
    def list_active_workflows(self) -> List[Dict]:
        """List all active workflows"""
        return [
            {
                'workflow_id': wf_id,
                'original_task': wf_data['original_task'],
                'total_steps': len(wf_data['steps']),
                'status': wf_data['status'],
                'created_at': wf_data['created_at']
            }
            for wf_id, wf_data in self.active_workflows.items()
        ]
    
    def get_delegation_statistics(self) -> Dict:
        """Get delegation statistics and performance metrics"""
        total_delegations = len(self.delegation_history)
        successful_delegations = sum(1 for d in self.delegation_history if d['success'])
        
        return {
            'total_delegations': total_delegations,
            'successful_delegations': successful_delegations,
            'success_rate': successful_delegations / total_delegations if total_delegations > 0 else 0,
            'active_workflows': len(self.active_workflows),
            'recent_delegations': self.delegation_history[-10:] if self.delegation_history else []
        }
    
    def delegate_task(self, description: str, target_agent: Optional[str] = None) -> TaskResult:
        """
        Delegate a task using simple syntax: delegate "description" to agent_name
        If target_agent is not specified, AI will determine the best agent.
        """
        colored_print(f"Delegating task: {description}", Colors.BRIGHT_CYAN)
        
        # Create task input
        task_input = TaskInput(
            task_description=description,
            task_type='delegation',
            priority=1
        )
        
        if target_agent:
            # Direct delegation to specified agent
            colored_print(f"  Direct delegation to: {target_agent}", Colors.CYAN)
            
            # Validate agent exists
            active_agents = self.comm.get_active_agents()
            available_roles = [a['role'] for a in active_agents]
            
            if target_agent not in available_roles and target_agent not in self.agent_capabilities:
                colored_print(f"  Warning: Agent '{target_agent}' may not be active", Colors.YELLOW)
            
            # Create task for target agent
            task_id = self.comm.create_task(
                task_type='direct_delegation',
                description=description,
                assigned_to=target_agent,
                created_by=self.agent_id,
                priority=1,
                data={
                    'delegation_method': 'direct',
                    'delegated_at': datetime.now().isoformat()
                }
            )
            
            colored_print(f"  Task {task_id} created for {target_agent}", Colors.GREEN)
            
            return TaskResult(
                success=True,
                message=f"Task delegated to {target_agent}",
                data={'task_id': task_id, 'agent': target_agent},
                delegated_tasks=[task_id]
            )
        else:
            # Smart delegation - let AI decide
            colored_print("  Using AI to determine best agent...", Colors.CYAN)
            return self.execute_task(task_input)
    
    def show_agents_status(self) -> Dict:
        """Show status of all agents in the system"""
        active_agents = self.comm.get_active_agents()
        all_agents = self.comm.load_agents()
        
        status_info = {
            'total_agents': len(all_agents),
            'active_agents': len(active_agents),
            'inactive_agents': len(all_agents) - len(active_agents),
            'agents': []
        }
        
        colored_print("\nAgent Status Overview:", Colors.BRIGHT_CYAN)
        colored_print("=" * 60, Colors.CYAN)
        
        for agent in all_agents:
            agent_status = {
                'id': agent['id'],
                'role': agent['role'],
                'status': agent.get('status', 'unknown'),
                'pid': agent.get('pid', 'N/A'),
                'last_seen': agent.get('last_seen', 'N/A')
            }
            status_info['agents'].append(agent_status)
            
            status_symbol = "[ACTIVE]" if agent.get('status') == 'active' else "[INACTIVE]"
            color = Colors.GREEN if agent.get('status') == 'active' else Colors.YELLOW
            
            colored_print(f"{status_symbol} {agent['id']} ({agent['role']})", color)
            colored_print(f"  PID: {agent.get('pid', 'N/A')} | Last seen: {agent.get('last_seen', 'N/A')}", Colors.WHITE)
        
        colored_print(f"\nTotal: {len(active_agents)} active, {len(all_agents) - len(active_agents)} inactive", Colors.CYAN)
        
        return status_info
    
    def show_tasks_status(self) -> Dict:
        """Show status of all tasks in the system"""
        all_tasks = self.comm.load_tasks()
        
        tasks_by_status = {
            'pending': [],
            'in_progress': [],
            'completed': [],
            'failed': []
        }
        
        for task in all_tasks:
            status = task.get('status', 'pending')
            if status in tasks_by_status:
                tasks_by_status[status].append(task)
        
        colored_print("\nTasks Status Overview:", Colors.BRIGHT_CYAN)
        colored_print("=" * 60, Colors.CYAN)
        
        for status, tasks in tasks_by_status.items():
            color = {
                'pending': Colors.YELLOW,
                'in_progress': Colors.BLUE,
                'completed': Colors.GREEN,
                'failed': Colors.RED
            }.get(status, Colors.WHITE)
            
            colored_print(f"\n{status.upper()}: {len(tasks)} tasks", color)
            
            for task in tasks[:5]:
                colored_print(f"  [{task.get('id', 'N/A')}] {task.get('description', 'No description')[:60]}...", Colors.WHITE)
                colored_print(f"    Assigned to: {task.get('assigned_to', 'N/A')} | Priority: {task.get('priority', 'N/A')}", Colors.WHITE)
            
            if len(tasks) > 5:
                colored_print(f"  ... and {len(tasks) - 5} more", Colors.WHITE)
        
        return {
            'total_tasks': len(all_tasks),
            'by_status': {status: len(tasks) for status, tasks in tasks_by_status.items()}
        }
    
    def show_workspace_info(self) -> Dict:
        """Show current workspace information"""
        workspace_info = {
            'workspace_dir': str(self.workspace_dir),
            'exists': self.workspace_dir.exists(),
            'is_directory': self.workspace_dir.is_dir() if self.workspace_dir.exists() else False,
            'comm_dir': str(self.comm.comm_dir),
            'comm_dir_exists': self.comm.comm_dir.exists()
        }
        
        colored_print("\nWorkspace Information:", Colors.BRIGHT_CYAN)
        colored_print("=" * 60, Colors.CYAN)
        colored_print(f"Workspace Directory: {workspace_info['workspace_dir']}", Colors.WHITE)
        colored_print(f"Status: {'EXISTS' if workspace_info['exists'] else 'NOT FOUND'}", 
                     Colors.GREEN if workspace_info['exists'] else Colors.RED)
        colored_print(f"Communication Directory: {workspace_info['comm_dir']}", Colors.WHITE)
        colored_print(f"Status: {'ACTIVE' if workspace_info['comm_dir_exists'] else 'NOT INITIALIZED'}", 
                     Colors.GREEN if workspace_info['comm_dir_exists'] else Colors.YELLOW)
        
        if workspace_info['exists'] and workspace_info['is_directory']:
            try:
                files_count = len(list(self.workspace_dir.rglob('*')))
                py_files = len(list(self.workspace_dir.rglob('*.py')))
                js_files = len(list(self.workspace_dir.rglob('*.js')))
                
                colored_print(f"\nWorkspace Contents:", Colors.CYAN)
                colored_print(f"  Total files: {files_count}", Colors.WHITE)
                colored_print(f"  Python files: {py_files}", Colors.WHITE)
                colored_print(f"  JavaScript files: {js_files}", Colors.WHITE)
                
                workspace_info.update({
                    'total_files': files_count,
                    'python_files': py_files,
                    'javascript_files': js_files
                })
            except Exception as e:
                colored_print(f"  Could not scan workspace: {e}", Colors.YELLOW)
        
        return workspace_info
    
    def set_workspace(self, new_workspace_dir: str) -> bool:
        """Set a new workspace directory"""
        new_path = Path(new_workspace_dir).resolve()
        
        colored_print(f"Setting workspace to: {new_path}", Colors.BRIGHT_CYAN)
        
        if not new_path.exists():
            colored_print(f"Warning: Directory does not exist. Creating...", Colors.YELLOW)
            try:
                new_path.mkdir(parents=True, exist_ok=True)
                colored_print(f"Directory created successfully", Colors.GREEN)
            except Exception as e:
                colored_print(f"Failed to create directory: {e}", Colors.RED)
                return False
        
        self.workspace_dir = new_path
        
        # Reinitialize communication with new workspace
        self.comm = type(self.comm)(str(new_path))
        self.comm.register_agent(self.agent_id, self.role)
        
        colored_print(f"Workspace updated successfully", Colors.GREEN)
        return True
    
    def guide_project_setup(self) -> Dict:
        """
        Interactive guide to help user set up their project.
        Returns project configuration.
        """
        colored_print("\n" + "=" * 60, Colors.BRIGHT_CYAN)
        colored_print("Project Setup Guide", Colors.BRIGHT_CYAN)
        colored_print("=" * 60, Colors.CYAN)
        
        colored_print("\nThis guide will help you:", Colors.WHITE)
        colored_print("  1. Define your project workspace", Colors.WHITE)
        colored_print("  2. Configure project settings", Colors.WHITE)
        colored_print("  3. Initialize the agent system", Colors.WHITE)
        
        colored_print("\nCurrent workspace: " + str(self.workspace_dir), Colors.CYAN)
        
        workspace_valid = self.workspace_dir.exists() and self.workspace_dir.is_dir()
        
        if workspace_valid:
            colored_print("Workspace is valid and ready", Colors.GREEN)
        else:
            colored_print("Workspace needs to be configured", Colors.YELLOW)
            colored_print("\nUse the command: set_workspace <path>", Colors.WHITE)
            colored_print("Example: set_workspace /home/user/myproject", Colors.WHITE)
        
        colored_print("\nAvailable Commands:", Colors.BRIGHT_CYAN)
        colored_print("  delegate \"task description\" to <agent>  - Delegate tasks", Colors.WHITE)
        colored_print("  agents                                   - Show agent status", Colors.WHITE)
        colored_print("  tasks                                    - Show tasks status", Colors.WHITE)
        colored_print("  workspace                                - Show workspace info", Colors.WHITE)
        colored_print("  set_workspace <path>                     - Set workspace directory", Colors.WHITE)
        colored_print("  workflows                                - Show active workflows", Colors.WHITE)
        colored_print("  stats                                    - Show delegation statistics", Colors.WHITE)
        
        return {
            'workspace': str(self.workspace_dir),
            'workspace_valid': workspace_valid,
            'active_agents': len(self.comm.get_active_agents()),
            'available_commands': [
                'delegate', 'agents', 'tasks', 'workspace', 
                'set_workspace', 'workflows', 'stats'
            ]
        }
    
    def parse_delegate_command(self, command: str) -> Optional[tuple]:
        """
        Parse delegation command: delegate "description" to agent_name
        Returns: (description, agent_name) or None if invalid
        """
        command = command.strip()
        
        # Check if command starts with 'delegate'
        if not command.lower().startswith('delegate'):
            return None
        
        # Remove 'delegate' prefix
        command = command[8:].strip()
        
        # Try to extract quoted description and target agent
        if '"' in command:
            # Extract description between quotes
            parts = command.split('"')
            if len(parts) >= 3:
                description = parts[1].strip()
                remainder = parts[2].strip()
                
                # Check for 'to agent_name'
                if remainder.lower().startswith('to '):
                    agent_name = remainder[3:].strip()
                    return (description, agent_name)
                else:
                    # No target agent specified
                    return (description, None)
        
        # Fallback: treat entire text as description
        if ' to ' in command.lower():
            parts = command.lower().split(' to ')
            description = parts[0].strip()
            agent_name = parts[1].strip() if len(parts) > 1 else None
            return (description, agent_name)
        
        return (command, None)
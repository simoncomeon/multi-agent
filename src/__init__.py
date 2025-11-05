"""
Multi-Agent AI Terminal System - Modular Architecture

A sophisticated multi-agent coordination system with specialized AI agents
that collaborate on projects using complete project context.
"""

__version__ = "3.0.0"
__author__ = "Multi-Agent AI Development Team"

# Core imports for easy access
from .core.models import AgentRole, TaskStatus, Task, Colors
from .core.utils import colored_print
from .core.communication import AgentCommunication

# Specialized agents
from .agents import (
    CodeReviewerAgent, EnhancedFileManagerAgent, EnhancedCodeGeneratorAgent,
    CoordinatorAgent, GitManagerAgent, ResearchAgent, 
    TestingAgent, CodeRewriterAgent, HelperAgent
)

# Management systems
from .lifecycle import AgentLifecycleManager
from .project import ProjectManager

__all__ = [
    # Core components
    'AgentRole', 'TaskStatus', 'Task', 'Colors', 'colored_print', 'AgentCommunication',
    
    # Specialized agents
    'CodeReviewerAgent', 'EnhancedFileManagerAgent', 'EnhancedCodeGeneratorAgent',
    'CoordinatorAgent', 'GitManagerAgent', 'ResearchAgent',
    'TestingAgent', 'CodeRewriterAgent', 'HelperAgent',
    
    # Management systems
    'AgentLifecycleManager', 'ProjectManager'
]
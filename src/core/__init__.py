"""
Core system components for the Multi-Agent AI Terminal System
"""

# Core models and enums
from .models import AgentRole, TaskStatus, Task, Colors

# Utility functions
from .utils import colored_print

# Communication system
from .communication import AgentCommunication

__all__ = ['AgentRole', 'TaskStatus', 'Task', 'Colors', 'colored_print', 'AgentCommunication']
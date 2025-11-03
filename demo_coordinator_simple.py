#!/usr/bin/env python3
"""
Simple demonstration of coordinator copy-paste format
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.helper_agent import HelperAgent
from src.core.utils import colored_print, Colors

def demo_coordinator_ready():
    """Demo the coordinator-ready format."""
    
    colored_print("COORDINATOR COPY-PASTE DEMO", Colors.BRIGHT_GREEN)
    
    helper = HelperAgent()
    
    # Simple test
    task = "Create a simple calculator app"
    
    colored_print(f"\nTask: {task}", Colors.YELLOW)
    
    # Generate coordinator commands
    helper.print_coordinator_commands(task)

if __name__ == "__main__":
    demo_coordinator_ready()
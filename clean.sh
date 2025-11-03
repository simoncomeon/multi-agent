#!/bin/bash

# Quick cleanup script for multi-agent system
echo " Quick Agent Cleanup"

# Kill any running multi_agent_terminal processes
pkill -f "multi_agent_terminal.py" 2>/dev/null

# Clean communication files
if [ -d ".agent_comm" ]; then
    echo "[]" > .agent_comm/agents.json
    echo "[]" > .agent_comm/tasks.json  
    echo "[]" > .agent_comm/messages.json
    echo "Communication files cleaned"
fi

echo "All agents deactivated - system is clean!"
echo "Ready for fresh start"
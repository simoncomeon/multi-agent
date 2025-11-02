#!/bin/bash

# Multi-Agent Terminal Launcher
# This script helps launch multiple coordinated AI agents

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERMINAL_SCRIPT="$SCRIPT_DIR/multi_agent_terminal.py"

echo "Multi-Agent AI Terminal System"
echo "=================================="
echo ""
echo "Available agent roles:"
echo "  1. coordinator   - Main orchestrator agent"
echo "  2. coder         - Code analysis and generation"
echo "  3. code_reviewer - Code quality assurance and optimization"
echo "  4. code_rewriter - Fixes issues found by code reviewer"
echo "  5. file_manager  - File operations and organization"
echo "  6. git_manager   - Version control operations"  
echo "  7. researcher    - Information gathering and analysis"
echo ""

if [ $# -eq 0 ]; then
    echo "Usage: $0 <role> [agent_id]"
    echo "Example: $0 coordinator main_coordinator"
    echo "Example: $0 coder"
    echo ""
    echo "Or run interactively:"
    read -p "Enter agent role: " role
    read -p "Enter agent ID (optional): " agent_id
    
    if [ -z "$agent_id" ]; then
        python3 "$TERMINAL_SCRIPT" "$role"
    else
        python3 "$TERMINAL_SCRIPT" "$role" "$agent_id"
    fi
else
    python3 "$TERMINAL_SCRIPT" "$@"
fi
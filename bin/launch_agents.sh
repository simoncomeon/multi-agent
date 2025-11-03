#!/bin/bash

# Multi-Agent Terminal Launcher
# This script helps launch multiple coordinated AI agents

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERMINAL_SCRIPT="$SCRIPT_DIR/multi_agent_terminal.py"

echo "Universal Multi-Agent AI Terminal System"
echo "========================================"
echo ""
echo "FRAMEWORK: Universal AI-Powered Development"
echo "INFO: Framework-agnostic system for React, Vue, Python, Node.js, Java, and more"
echo ""
echo "Available agent roles:"
echo "  1. coordinator   - Universal project orchestration and workflow management"
echo "  2. coder         - Framework-agnostic code generation and analysis"
echo "  3. code_reviewer - Cross-framework quality assurance and error detection"
echo "  4. code_rewriter - Automated code fixing with framework-specific best practices"
echo "  5. file_manager  - Universal project creation across any technology stack"
echo "  6. git_manager   - Framework-aware version control operations"  
echo "  7. researcher    - Technology-agnostic information gathering and best practices"
echo ""
echo "PROCESS: Enhanced Communication Features:"
echo "  - Background and terminal agents share same communication system"
echo "  - Real-time task delegation and status tracking"
echo "  - Project context sharing across all agents"
echo "  - Status monitoring: python3 ../agent_status.py --live 5"
echo ""
echo "LAUNCH: Automated Multi-Agent Setup:"
echo "     python3 ../smart_launcher.py ai-development     # Universal team"
echo "     python3 ../smart_launcher.py code-review --bg   # Background review team"
echo "     python3 ../smart_launcher.py --connect          # Connection guide"
echo ""

if [ $# -eq 0 ]; then
    echo "Usage: $0 <role> [agent_id]"
    echo "Example: $0 coordinator main"
    echo "Example: $0 coder dev"
    echo "Example: $0 file_manager files"
    echo ""
    echo "INFO: Single agent launcher - joins existing communication system"
    echo "LAUNCH: For complete workflows: python3 ../smart_launcher.py --help"
    echo ""
    echo "Or run interactively:"
    read -p "Enter agent role: " role
    read -p "Enter agent ID (optional): " agent_id
    
    if [ -z "$agent_id" ]; then
        # Use role as agent_id if no specific agent_id provided
        python3 "$TERMINAL_SCRIPT" "$role" "$role"
    else
        # Pass agent_id first, then role (as expected by multi_agent_terminal.py)
        python3 "$TERMINAL_SCRIPT" "$agent_id" "$role"
    fi
else
    # For command line usage: ./launch_agents.sh <role> [agent_id]
    # Convert to: python3 script.py <agent_id> <role>
    if [ $# -eq 1 ]; then
        # Only role provided, use role as agent_id
        python3 "$TERMINAL_SCRIPT" "$1" "$1"
    else
        # Both role and agent_id provided: ./launch_agents.sh <role> <agent_id>
        # Convert to: python3 script.py <agent_id> <role>
        python3 "$TERMINAL_SCRIPT" "$2" "$1"
    fi
fi
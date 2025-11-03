#!/bin/bash

# Multi-Agent AI Terminal System Launcher
# Organized directory structure with proper workspace management

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MULTI_AGENT_ROOT="$(dirname "$SCRIPT_DIR")"
BIN_DIR="$MULTI_AGENT_ROOT/bin"
WORKSPACE_DIR="$MULTI_AGENT_ROOT/workspace"
TERMINAL_SCRIPT="$BIN_DIR/multi_agent_terminal.py"

# Ensure workspace directory exists
mkdir -p "$WORKSPACE_DIR"

echo "Universal Multi-Agent AI Terminal System v3.0"
echo "=============================================="
echo "Root Directory: $MULTI_AGENT_ROOT"
echo "Workspace: $WORKSPACE_DIR"
echo ""
echo "FRAMEWORK: Universal AI-Powered Development System"
echo "INFO: Supports React, Vue, Python, Node.js, Java, Go, C#, Rust, and more"
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
echo "PROCESS: Communication System Features:"
echo "  - Real-time inter-agent messaging via .agent_comm/ directory"
echo "  - Universal commands work across all agents"
echo "  - Project_Process paradigm with complete context loading"
echo "  - Status monitoring available with: python3 ../agent_status.py"
echo ""
echo "TIP: For automated multi-agent launches, use:"
echo "     python3 ../smart_launcher.py ai-development"
echo "     python3 ../smart_launcher.py --help"
echo ""

# Change to workspace directory before launching agent
cd "$WORKSPACE_DIR"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <role> [agent_id]"
    echo "Example: $0 coordinator main"
    echo "Example: $0 coder dev"
    echo "Example: $0 file_manager files"
    echo ""
    echo "INFO: Individual agent launcher - connects to existing communication system"
    echo "TIP: Use smart_launcher.py for complete multi-agent workflow setup"
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
    # For command line usage: ./launch.sh <role> [agent_id]
    # Convert to: python3 script.py <agent_id> <role>
    if [ $# -eq 1 ]; then
        # Only role provided, use role as agent_id
        python3 "$TERMINAL_SCRIPT" "$1" "$1"
    else
        # Both role and agent_id provided: ./launch.sh <role> <agent_id>
        # Convert to: python3 script.py <agent_id> <role>
        python3 "$TERMINAL_SCRIPT" "$2" "$1"
    fi
fi
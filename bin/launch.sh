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

echo "Multi-Agent AI Terminal System v2.0"
echo "======================================="
echo "Root Directory: $MULTI_AGENT_ROOT"
echo "Workspace: $WORKSPACE_DIR"
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

# Change to workspace directory before launching agent
cd "$WORKSPACE_DIR"

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
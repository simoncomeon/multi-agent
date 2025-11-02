#!/bin/bash

# Tmux-based Multi-Agent Launcher
# Usage: ./launch_agents_tmux.sh coordinator:main file_manager:files coder:dev

SESSION_NAME="multi-agent-session"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MULTI_AGENT_SCRIPT="$SCRIPT_DIR/bin/multi_agent_terminal.py"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if tmux is available
if ! command -v tmux >/dev/null 2>&1; then
    echo -e "${RED}❌ tmux is not installed. Please install tmux or use launch_agents.sh instead.${NC}"
    exit 1
fi

# Function to create tmux session with agents
create_agent_session() {
    echo -e "${BLUE}Creating multi-agent tmux session...${NC}"
    
    # Kill existing session if it exists
    tmux kill-session -t "$SESSION_NAME" 2>/dev/null
    
    # Create new session (detached)
    tmux new-session -d -s "$SESSION_NAME" -c "$SCRIPT_DIR"
    
    local window_count=0
    
    for agent_spec in "$@"; do
        if [[ "$agent_spec" == *":"* ]]; then
            local role="${agent_spec%%:*}"
            local name="${agent_spec##*:}"
            
            if [[ $window_count -eq 0 ]]; then
                # Use the initial window for first agent
                tmux rename-window -t "$SESSION_NAME:0" "${role}-${name}"
                tmux send-keys -t "$SESSION_NAME:0" "python3 '$MULTI_AGENT_SCRIPT' '$role' '$name'" Enter
            else
                # Create new window for subsequent agents
                tmux new-window -t "$SESSION_NAME" -n "${role}-${name}" -c "$SCRIPT_DIR"
                tmux send-keys -t "$SESSION_NAME:${role}-${name}" "python3 '$MULTI_AGENT_SCRIPT' '$role' '$name'" Enter
            fi
            
            echo -e "${GREEN}Started ${role} agent '${name}' in tmux window${NC}"
            ((window_count++))
            sleep 1
        fi
    done
    
    echo ""
    echo -e "${CYAN}Tmux session '${SESSION_NAME}' created with ${window_count} agent(s)${NC}"
    echo -e "${YELLOW}Attach to session: tmux attach -t ${SESSION_NAME}${NC}"
    echo -e "${YELLOW}List windows: tmux list-windows -t ${SESSION_NAME}${NC}"
    echo -e "${YELLOW}Kill session: tmux kill-session -t ${SESSION_NAME}${NC}"
    
    # Show tmux windows
    echo ""
    echo -e "${BLUE}Tmux Windows:${NC}"
    tmux list-windows -t "$SESSION_NAME"
}

# Show usage
show_usage() {
    echo -e "${CYAN}Tmux Multi-Agent Launcher${NC}"
    echo "================================"
    echo ""
    echo "Usage: $0 <role1:name1> [role2:name2] [role3:name3] ..."
    echo ""
    echo "Examples:"
    echo "  $0 coordinator:main"
    echo "  $0 coordinator:main file_manager:files coder:dev"
    echo ""
    echo "Tmux Commands:"
    echo "  tmux attach -t $SESSION_NAME     # Attach to session"
    echo "  Ctrl+b, n                        # Next window"
    echo "  Ctrl+b, p                        # Previous window"
    echo "  Ctrl+b, d                        # Detach from session"
}

# Main execution
if [[ $# -eq 0 ]]; then
    show_usage
    exit 0
fi

create_agent_session "$@"

# Optionally attach to session
read -p "Attach to tmux session now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    tmux attach -t "$SESSION_NAME"
fi
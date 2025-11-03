#!/bin/bash

# Multi-Agent Launcher - Automated agent creation with separate terminals
# Usage: ./launch_agents.sh coordinator:main file_manager:files coder:dev code_reviewer:reviewer

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MULTI_AGENT_DIR="$SCRIPT_DIR"
MULTI_AGENT_SCRIPT="$MULTI_AGENT_DIR/bin/multi_agent_terminal.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Function to detect terminal emulator
detect_terminal() {
    if command -v gnome-terminal >/dev/null 2>&1; then
        echo "gnome-terminal"
    elif command -v xterm >/dev/null 2>&1; then
        echo "xterm"
    elif command -v konsole >/dev/null 2>&1; then
        echo "konsole"
    elif command -v terminator >/dev/null 2>&1; then
        echo "terminator"
    elif command -v alacritty >/dev/null 2>&1; then
        echo "alacritty"
    elif command -v kitty >/dev/null 2>&1; then
        echo "kitty"
    else
        echo "unknown"
    fi
}

# Function to launch agent in new terminal
launch_agent_terminal() {
    local role="$1"
    local name="$2"
    local terminal="$3"
    
    echo -e "${CYAN}Launching ${role} agent '${name}' in new terminal...${NC}"
    
    case "$terminal" in
        "gnome-terminal")
            gnome-terminal --title="Agent: ${role} (${name})" \
                          --working-directory="$MULTI_AGENT_DIR" \
                          -- bash -c "echo -e '${GREEN}Starting ${role} agent: ${name}${NC}'; \
                                      python3 '$MULTI_AGENT_SCRIPT' '$role' '$name'; \
                                      echo -e '${RED}Agent ${name} terminated${NC}'; \
                                      read -p 'Press Enter to close...'"
            ;;
        "xterm")
            xterm -title "Agent: ${role} (${name})" \
                  -e bash -c "cd '$MULTI_AGENT_DIR'; \
                              echo -e '${GREEN}Starting ${role} agent: ${name}${NC}'; \
                              python3 '$MULTI_AGENT_SCRIPT' '$role' '$name'; \
                              echo -e '${RED}Agent ${name} terminated${NC}'; \
                              read -p 'Press Enter to close...'" &
            ;;
        "konsole")
            konsole --new-tab --title "Agent: ${role} (${name})" \
                    --workdir "$MULTI_AGENT_DIR" \
                    -e bash -c "echo -e '${GREEN}Starting ${role} agent: ${name}${NC}'; \
                                python3 '$MULTI_AGENT_SCRIPT' '$role' '$name'; \
                                echo -e '${RED}Agent ${name} terminated${NC}'; \
                                read -p 'Press Enter to close...'" &
            ;;
        "terminator")
            terminator --new-tab --title="Agent: ${role} (${name})" \
                      --working-directory="$MULTI_AGENT_DIR" \
                      -x bash -c "echo -e '${GREEN}Starting ${role} agent: ${name}${NC}'; \
                                  python3 '$MULTI_AGENT_SCRIPT' '$role' '$name'; \
                                  echo -e '${RED}Agent ${name} terminated${NC}'; \
                                  read -p 'Press Enter to close...'" &
            ;;
        "alacritty")
            alacritty --title "Agent: ${role} (${name})" \
                     --working-directory "$MULTI_AGENT_DIR" \
                     -e bash -c "echo -e '${GREEN}Starting ${role} agent: ${name}${NC}'; \
                                 python3 '$MULTI_AGENT_SCRIPT' '$role' '$name'; \
                                 echo -e '${RED}Agent ${name} terminated${NC}'; \
                                 read -p 'Press Enter to close...'" &
            ;;
        "kitty")
            kitty --title "Agent: ${role} (${name})" \
                  --directory "$MULTI_AGENT_DIR" \
                  bash -c "echo -e '${GREEN}Starting ${role} agent: ${name}${NC}'; \
                           python3 '$MULTI_AGENT_SCRIPT' '$role' '$name'; \
                           echo -e '${RED}Agent ${name} terminated${NC}'; \
                           read -p 'Press Enter to close...'" &
            ;;
        *)
            echo -e "${RED}ERROR: Unknown terminal emulator. Starting in background...${NC}"
            cd "$MULTI_AGENT_DIR"
            python3 "$MULTI_AGENT_SCRIPT" "$role" "$name" &
            ;;
    esac
    
    sleep 1  # Give terminal time to start
}

# Function to show usage
show_usage() {
    echo -e "${WHITE}Multi-Agent Launcher${NC}"
    echo "============================="
    echo ""
    echo -e "${CYAN}Usage:${NC}"
    echo "  $0 <role1:name1> [role2:name2] [role3:name3] ..."
    echo ""
    echo -e "${CYAN}Available Roles:${NC}"
    echo "  • coordinator   - Main orchestrator agent"
    echo "  • coder         - Code analysis and generation"
    echo "  • code_reviewer - Code quality assurance"
    echo "  • code_rewriter - Fixes issues found by code reviewer"
    echo "  • file_manager  - File operations and organization"
    echo "  • git_manager   - Version control operations"
    echo "  • researcher    - Information gathering and analysis"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0 coordinator:main"
    echo "  $0 coordinator:main file_manager:files coder:dev"
    echo "  $0 coordinator:main file_manager:files coder:dev code_reviewer:reviewer code_rewriter:fixer git_manager:git"
    echo ""
    echo -e "${CYAN}Preset Workflows:${NC}"
    echo "  $0 --ai-dev       # Start agents for AI-powered development (any framework)"
    echo "  $0 --full-team    # Start all agent types"
    echo "  $0 --code-review  # Start code quality agents"
    echo ""
}

# Preset configurations
start_ai_dev() {
    echo -e "${MAGENTA}Starting AI-Powered Development Team...${NC}"
    launch_agents "coordinator:main" "file_manager:files" "coder:dev" "code_reviewer:reviewer" "code_rewriter:fixer" "git_manager:git"
}

start_full_team() {
    echo -e "${MAGENTA}Starting Full Agent Team...${NC}"
    launch_agents "coordinator:main" "file_manager:files" "coder:dev" "code_reviewer:reviewer" "code_rewriter:fixer" "git_manager:git" "researcher:research"
}

start_code_review() {
    echo -e "${MAGENTA}Starting Code Review Team...${NC}"
    launch_agents "coordinator:main" "code_reviewer:reviewer" "code_rewriter:fixer"
}

# Function to launch multiple agents
launch_agents() {
    local terminal_type=$(detect_terminal)
    echo -e "${BLUE}Detected terminal: ${terminal_type}${NC}"
    echo ""
    
    local agent_count=0
    
    for agent_spec in "$@"; do
        if [[ "$agent_spec" == *":"* ]]; then
            local role="${agent_spec%%:*}"
            local name="${agent_spec##*:}"
            
            # Validate role
            case "$role" in
                coordinator|coder|code_reviewer|code_rewriter|file_manager|git_manager|researcher)
                    launch_agent_terminal "$role" "$name" "$terminal_type"
                    ((agent_count++))
                    ;;
                *)
                    echo -e "${RED}ERROR: Invalid role: $role${NC}"
                    echo -e "${YELLOW}Valid roles: coordinator, coder, code_reviewer, code_rewriter, file_manager, git_manager, researcher${NC}"
                    return 1
                    ;;
            esac
        else
            echo -e "${RED}ERROR: Invalid format: $agent_spec${NC}"
            echo -e "${YELLOW}Use format: role:name${NC}"
            return 1
        fi
    done
    
    echo ""
    echo -e "${GREEN}Launched ${agent_count} agent(s) in separate terminals${NC}"
    echo -e "${CYAN}Tip: Check agent status with: ./multi-agent status${NC}"
    
    # Wait a moment for agents to start up
    sleep 3
    
    # Show status
    echo ""
    echo -e "${WHITE}Current Agent Status:${NC}"
    cd "$MULTI_AGENT_DIR"
    ./multi-agent status
}

# Main script logic
main() {
    # Check if we're in the right directory
    if [[ ! -f "$MULTI_AGENT_SCRIPT" ]]; then
        echo -e "${RED}ERROR: multi_agent_terminal.py not found in bin/. Please run from multi-agent directory.${NC}"
        exit 1
    fi
    
    # Handle no arguments
    if [[ $# -eq 0 ]]; then
        show_usage
        exit 0
    fi
    
    # Handle preset workflows
    case "$1" in
        --ai-dev)
            start_ai_dev
            ;;
        --full-team)
            start_full_team
            ;;
        --code-review)
            start_code_review
            ;;
        --help|-h)
            show_usage
            ;;
        *)
            # Launch custom agent configuration
            launch_agents "$@"
            ;;
    esac
}

# Run main function
main "$@"
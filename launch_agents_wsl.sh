#!/bin/bash

# WSL-optimized Multi-Agent Launcher
# Designed specifically for Ubuntu on WSL with Windows Terminal integration

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MULTI_AGENT_SCRIPT="$SCRIPT_DIR/bin/multi_agent_terminal.py"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
WHITE='\033[1;37m'
NC='\033[0m'

# Check if we're in WSL
check_wsl() {
    if [[ -f /proc/version ]] && grep -q "WSL" /proc/version; then
        return 0
    fi
    return 1
}

# Launch agent using Windows Terminal (best for WSL)
launch_agent_wt() {
    local role="$1"
    local name="$2"
    
    echo -e "${CYAN}Launching ${role} agent '${name}' in Windows Terminal...${NC}"
    
    # Use Windows Terminal to create new tab
    wt.exe -w 0 new-tab --title "Agent: ${role} (${name})" bash -c "cd '$SCRIPT_DIR' && python3 '$MULTI_AGENT_SCRIPT' '$role' '$name'; echo -e '${RED}Agent ${name} terminated${NC}'; read -p 'Press Enter to close...'"
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}Successfully launched ${role} agent '${name}'${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to launch with Windows Terminal${NC}"
        return 1
    fi
}

# Launch agent using PowerShell (fallback)
launch_agent_powershell() {
    local role="$1"
    local name="$2"
    
    echo -e "${YELLOW}⚠Falling back to PowerShell for ${role} agent '${name}'${NC}"
    
    # Get WSL distribution name
    local wsl_distro=$(wsl.exe -l -v | grep -E "\*|Running" | awk '{print $1}' | tr -d '\r' | head -1)
    [[ -z "$wsl_distro" ]] && wsl_distro="Ubuntu-22.04"
    
    powershell.exe -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', 'wsl -d $wsl_distro -e bash -c \"cd $SCRIPT_DIR && python3 $MULTI_AGENT_SCRIPT $role $name\"'"
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}Successfully launched ${role} agent '${name}' via PowerShell${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to launch with PowerShell${NC}"
        return 1
    fi
}

# Launch agent in background (last resort)
launch_agent_background() {
    local role="$1"
    local name="$2"
    
    echo -e "${YELLOW}⚠Launching ${role} agent '${name}' in background${NC}"
    
    cd "$SCRIPT_DIR"
    python3 "$MULTI_AGENT_SCRIPT" "$role" "$name" &
    
    echo -e "${GREEN}Background process started for ${role} agent '${name}' (PID: $!)${NC}"
    return 0
}

# Main launch function
launch_agent() {
    local role="$1"
    local name="$2"
    
    # Validate role
    case "$role" in
        coordinator|coder|code_reviewer|code_rewriter|file_manager|git_manager|researcher)
            ;;
        *)
            echo -e "${RED}❌ Invalid role: $role${NC}"
            return 1
            ;;
    esac
    
    if check_wsl; then
        echo -e "${BLUE}🐧 WSL environment detected${NC}"
        
        # Try Windows Terminal first
        if command -v wt.exe >/dev/null 2>&1; then
            launch_agent_wt "$role" "$name"
        # Try PowerShell as fallback
        elif command -v powershell.exe >/dev/null 2>&1; then
            launch_agent_powershell "$role" "$name"
        # Background as last resort
        else
            echo -e "${YELLOW}⚠No Windows terminal access found${NC}"
            launch_agent_background "$role" "$name"
        fi
    else
        echo -e "${YELLOW}⚠Not in WSL environment, launching in background${NC}"
        launch_agent_background "$role" "$name"
    fi
    
    sleep 1  # Give process time to start
}

# Preset workflows for WSL
launch_react_dev_wsl() {
    echo -e "${BLUE}Starting React Development Team for WSL...${NC}"
    echo ""
    
    agents=("coordinator:main" "file_manager:files" "coder:dev" "code_reviewer:reviewer" "code_rewriter:fixer" "git_manager:git")
    
    for agent_spec in "${agents[@]}"; do
        role="${agent_spec%%:*}"
        name="${agent_spec##*:}"
        launch_agent "$role" "$name"
    done
    
    echo ""
    echo -e "${GREEN}React development team launched!${NC}"
    echo -e "${CYAN}Tip: Use 'wt.exe' to manage Windows Terminal tabs${NC}"
    echo -e "${CYAN}Check agent status: ./multi-agent status${NC}"
}

launch_code_review_wsl() {
    echo -e "${BLUE}Starting Code Review Team for WSL...${NC}"
    echo ""
    
    agents=("coordinator:main" "code_reviewer:reviewer" "code_rewriter:fixer")
    
    for agent_spec in "${agents[@]}"; do
        role="${agent_spec%%:*}"
        name="${agent_spec##*:}"
        launch_agent "$role" "$name"
    done
    
    echo ""
    echo -e "${GREEN}Code review team launched!${NC}"
}

# Show usage
show_usage() {
    echo -e "${WHITE}🐧 WSL Multi-Agent Launcher${NC}"
    echo "================================"
    echo ""
    echo -e "${CYAN}WSL-Optimized Commands:${NC}"
    echo "  $0 --react-dev     # Launch React development team"
    echo "  $0 --code-review   # Launch code review team"
    echo "  $0 --background    # Launch all agents in background mode"
    echo ""
    echo -e "${CYAN}Individual Agent Launch:${NC}"
    echo "  $0 <role>:<name>   # Launch single agent"
    echo ""
    echo -e "${CYAN}Multiple Agents:${NC}"
    echo "  $0 coordinator:main file_manager:files coder:dev"
    echo ""
    echo -e "${CYAN}Available Roles:${NC}"
    echo "  • coordinator   - Main orchestrator"
    echo "  • file_manager  - File operations" 
    echo "  • coder         - Code development"
    echo "  • code_reviewer - Code quality"
    echo "  • code_rewriter - Issue fixing"
    echo "  • git_manager   - Version control"
    echo "  • researcher    - Information gathering"
    echo ""
    echo -e "${YELLOW}WSL Tips:${NC}"
    echo "  • Use Windows Terminal for best experience"
    echo "  • Each agent opens in separate tab/window"
    echo "  • Background mode if terminal access fails"
    echo "  • Check status with: ./multi-agent status"
}

# Main execution
main() {
    # Check if we have the agent script
    if [[ ! -f "$MULTI_AGENT_SCRIPT" ]]; then
        echo -e "${RED}❌ multi_agent_terminal.py not found${NC}"
        echo "Please run from the multi-agent directory"
        exit 1
    fi
    
    # Handle no arguments
    if [[ $# -eq 0 ]]; then
        show_usage
        exit 0
    fi
    
    # Handle preset workflows
    case "$1" in
        --react-dev)
            launch_react_dev_wsl
            ;;
        --code-review)
            launch_code_review_wsl
            ;;
        --background)
            shift
            echo -e "${BLUE}Launching agents in background mode${NC}"
            for agent_spec in "$@"; do
                if [[ "$agent_spec" == *":"* ]]; then
                    role="${agent_spec%%:*}"
                    name="${agent_spec##*:}"
                    launch_agent_background "$role" "$name"
                fi
            done
            ;;
        --help|-h)
            show_usage
            ;;
        *)
            # Launch individual agents
            for agent_spec in "$@"; do
                if [[ "$agent_spec" == *":"* ]]; then
                    role="${agent_spec%%:*}"
                    name="${agent_spec##*:}"
                    launch_agent "$role" "$name"
                else
                    echo -e "${RED}❌ Invalid format: $agent_spec (use role:name)${NC}"
                fi
            done
            ;;
    esac
}

main "$@"
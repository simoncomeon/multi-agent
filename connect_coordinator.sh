#!/bin/bash

# WSL Coordinator Connection Script
# Connects you directly to the coordinator agent for task delegation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_SCRIPT="$SCRIPT_DIR/bin/multi_agent_terminal.py"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
WHITE='\033[1;37m'
NC='\033[0m'

echo -e "${WHITE}Multi-Agent Coordinator Connection${NC}"
echo "===================================="
echo ""

# Check if agents are running
if [[ -f ".agent_comm/agents.json" ]]; then
    agent_count=$(python3 -c "import json; data=json.load(open('.agent_comm/agents.json')); print(len([a for a in data if a.get('status') == 'active']))" 2>/dev/null || echo "0")
    
    if [[ "$agent_count" -gt 0 ]]; then
        echo -e "${GREEN}Found $agent_count active agent(s)${NC}"
        echo ""
        
        # Show active agents
        echo -e "${CYAN}Active Agents:${NC}"
        python3 -c "
import json
try:
    with open('.agent_comm/agents.json', 'r') as f:
        agents = json.load(f)
    for agent in agents:
        if agent.get('status') == 'active':
            print(f\"   • {agent['role']} ({agent['id']})\")
except:
    print('   Error reading agents')
" 2>/dev/null
        
        echo ""
        echo -e "${BLUE}Connecting to coordinator agent...${NC}"
        echo -e "${YELLOW}You can now delegate tasks to other agents!${NC}"
        echo ""
        echo -e "${CYAN}Example commands:${NC}"
        echo "  delegate \"Create React.js TimeDisplayApp project structure\" to file_manager"
        echo "  delegate \"Create React components for time display\" to coder"
        echo "  delegate \"Review TimeDisplayApp code quality\" to code_reviewer"
        echo ""
        
        # Connect to coordinator
        python3 "$AGENT_SCRIPT" coordinator main
        
    else
        echo -e "${YELLOW}No active agents found${NC}"
        echo ""
        echo "Start agents first:"
        echo "  python3 wsl_launcher.py react-dev"
        echo ""
        exit 1
    fi
else
    echo -e "${YELLOW}No agent communication found${NC}"
    echo ""
    echo "Start agents first:"
    echo "  python3 wsl_launcher.py react-dev"
    echo ""
    exit 1
fi
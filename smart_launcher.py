#!/usr/bin/env python3
"""
Smart Agent Launcher - Configuration-based agent management
"""

import json
import os
import sys
import subprocess
import time
from pathlib import Path

def load_workflows():
 """Load workflow configurations from JSON"""
 config_file = Path(__file__).parent / "agent_workflows.json"
 try:
 with open(config_file, 'r') as f:
 return json.load(f)
 except FileNotFoundError:
 print(" agent_workflows.json not found")
 return {}
 except json.JSONDecodeError:
 print(" Invalid JSON in agent_workflows.json")
 return {}

def launch_agent(role, name, method="terminal"):
 """Launch a single agent"""
 script_dir = Path(__file__).parent
 agent_script = script_dir / "bin" / "multi_agent_terminal.py"
 
 if method == "terminal":
 # Check if we're in WSL
 is_wsl = os.path.exists("/proc/version") and "WSL" in open("/proc/version").read()
 
 if is_wsl:
 # WSL-specific terminal launch using Windows Terminal or PowerShell
 wsl_terminals = [
 # Windows Terminal (preferred)
 ["wt.exe", "-w", "0", "new-tab", "--title", f"Agent: {role} ({name})", 
 "bash", "-c", f"cd {script_dir} && python3 {agent_script} {role} {name}; read -p 'Press Enter to close...'"],
 # PowerShell as fallback
 ["powershell.exe", "-Command", 
 f"Start-Process powershell -ArgumentList '-NoExit -Command wsl -d Ubuntu-22.04 -e bash -c \"cd {script_dir} && python3 {agent_script} {role} {name}\"'"],
 # CMD as last resort
 ["cmd.exe", "/c", "start", "cmd", "/k", 
 f"wsl -d Ubuntu-22.04 -e bash -c \"cd {script_dir} && python3 {agent_script} {role} {name}\""]
 ]
 
 for terminal_cmd in wsl_terminals:
 try:
 subprocess.Popen(terminal_cmd, cwd=script_dir)
 print(f"Launched {role} agent '{name}' in Windows terminal")
 return True
 except FileNotFoundError:
 continue
 else:
 # Standard Linux terminal emulators
 terminals = [
 ["gnome-terminal", "--title", f"Agent: {role} ({name})", 
 "--working-directory", str(script_dir), "--", 
 "python3", str(agent_script), role, name],
 ["xterm", "-title", f"Agent: {role} ({name})", "-e", 
 "bash", "-c", f"cd {script_dir} && python3 {agent_script} {role} {name}"],
 ["konsole", "--new-tab", "--title", f"Agent: {role} ({name})", 
 "--workdir", str(script_dir), "-e", 
 "python3", str(agent_script), role, name]
 ]
 
 for terminal_cmd in terminals:
 try:
 subprocess.Popen(terminal_cmd)
 print(f"Launched {role} agent '{name}' in {terminal_cmd[0]}")
 return True
 except FileNotFoundError:
 continue
 
 for terminal_cmd in terminals:
 try:
 subprocess.Popen(terminal_cmd)
 print(f"Launched {role} agent '{name}' in {terminal_cmd[0]}")
 return True
 except FileNotFoundError:
 continue
 
 # Fallback to background process
 if is_wsl:
 print(f"⚠WSL: No Windows terminal access, launching {role} agent '{name}' in background")
 print(f"Tip: Install Windows Terminal for better WSL experience")
 else:
 print(f"⚠No terminal emulator found, launching {role} agent '{name}' in background")
 
 subprocess.Popen([sys.executable, str(agent_script), role, name], 
 cwd=script_dir)
 return True
 
 elif method == "background":
 subprocess.Popen([sys.executable, str(agent_script), role, name], 
 cwd=script_dir)
 print(f"Launched {role} agent '{name}' in background")
 return True
 
 return False

def launch_workflow(workflow_name, workflows, method="terminal"):
 """Launch all agents for a specific workflow"""
 if workflow_name not in workflows["workflows"]:
 print(f" Workflow '{workflow_name}' not found")
 return False
 
 workflow = workflows["workflows"][workflow_name]
 print(f"Launching workflow: {workflow_name}")
 print(f"Description: {workflow['description']}")
 print()
 
 success_count = 0
 for agent in workflow["agents"]:
 if launch_agent(agent["role"], agent["name"], method):
 success_count += 1
 time.sleep(1) # Small delay between launches
 
 print()
 print(f"Successfully launched {success_count}/{len(workflow['agents'])} agents")
 return True

def show_available_workflows(workflows):
 """Display available workflow configurations"""
 print("Available Workflows:")
 print("=" * 50)
 
 for name, config in workflows["workflows"].items():
 print(f"\n{name}")
 print(f" {config['description']}")
 print(f" Agents: {len(config['agents'])}")
 for agent in config["agents"]:
 print(f" • {agent['role']} ({agent['name']})")

def show_usage():
 """Show usage information"""
 print("Smart Multi-Agent Launcher")
 print("=" * 40)
 print()
 print("Usage:")
 print(" python3 smart_launcher.py <workflow_name> # Launch workflow in terminals")
 print(" python3 smart_launcher.py <workflow_name> --bg # Launch workflow in background") 
 print(" python3 smart_launcher.py --list # List available workflows")
 print(" python3 smart_launcher.py --custom role1:name1 ... # Launch custom agents")
 print()
 print("Examples:")
 print(" python3 smart_launcher.py react-development")
 print(" python3 smart_launcher.py code-review --bg")
 print(" python3 smart_launcher.py --custom coordinator:main coder:dev")

def launch_custom_agents(agent_specs, method="terminal"):
 """Launch custom agent configuration"""
 print("Launching custom agent configuration")
 
 success_count = 0
 for spec in agent_specs:
 if ":" not in spec:
 print(f" Invalid format: {spec} (use role:name)")
 continue
 
 role, name = spec.split(":", 1)
 if launch_agent(role, name, method):
 success_count += 1
 time.sleep(1)
 
 print(f"Successfully launched {success_count}/{len(agent_specs)} agents")

def main():
 """Main entry point"""
 workflows = load_workflows()
 
 if not workflows:
 print(" No workflows available")
 return
 
 if len(sys.argv) < 2:
 show_usage()
 return
 
 command = sys.argv[1]
 method = "background" if "--bg" in sys.argv else "terminal"
 
 if command == "--list":
 show_available_workflows(workflows)
 elif command == "--custom":
 agent_specs = [arg for arg in sys.argv[2:] if not arg.startswith("--")]
 if not agent_specs:
 print(" No agent specifications provided")
 show_usage()
 return
 launch_custom_agents(agent_specs, method)
 elif command in workflows["workflows"]:
 launch_workflow(command, workflows, method)
 else:
 print(f" Unknown workflow or command: {command}")
 show_available_workflows(workflows)

if __name__ == "__main__":
 main()
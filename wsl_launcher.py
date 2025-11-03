#!/usr/bin/env python3
"""
WSL-Friendly Multi-Agent Launcher
Optimized for Ubuntu WSL with Windows integration
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

def is_wsl():
 """Check if running in WSL"""
 try:
 with open('/proc/version', 'r') as f:
 return 'WSL' in f.read()
 except:
 return False

def launch_agent_background(role, name):
 """Launch agent in background with proper WSL handling"""
 script_dir = Path(__file__).parent
 agent_script = script_dir / "bin" / "multi_agent_terminal.py"
 
 # Launch in background
 process = subprocess.Popen(
 [sys.executable, str(agent_script), role, name],
 cwd=script_dir,
 stdout=subprocess.DEVNULL,
 stderr=subprocess.DEVNULL
 )
 
 print(f"Launched {role} agent '{name}' in background (PID: {process.pid})")
 return process.pid

def launch_wsl_workflow(workflow_name):
 """Launch preset workflow optimized for WSL"""
 workflows = {
 "react-dev": [
 ("coordinator", "main"),
 ("file_manager", "files"), 
 ("coder", "dev"),
 ("code_reviewer", "reviewer"),
 ("code_rewriter", "fixer"),
 ("git_manager", "git")
 ],
 "code-review": [
 ("coordinator", "main"),
 ("code_reviewer", "reviewer"), 
 ("code_rewriter", "fixer")
 ],
 "minimal": [
 ("coordinator", "main"),
 ("coder", "dev")
 ]
 }
 
 if workflow_name not in workflows:
 print(f" Unknown workflow: {workflow_name}")
 return False
 
 print(f"WSL: WSL: Starting {workflow_name} workflow in background mode")
 print("=" * 50)
 
 agents = workflows[workflow_name]
 pids = []
 
 for role, name in agents:
 pid = launch_agent_background(role, name)
 pids.append((role, name, pid))
 time.sleep(0.5) # Small delay between launches
 
 print()
 print(f"Successfully launched {len(pids)} agents!")
 print()
 print("Running Agents:")
 for role, name, pid in pids:
 print(f" • {role} ({name}) - PID: {pid}")
 
 print()
 print(" Waiting for agents to register...")
 time.sleep(3) # Give agents time to register
 
 print()
 print("WSL Tips:")
 print(" - Use Windows Terminal for best experience") 
 print(" - Background processes continue running")
 print(" - Use './multi-agent status' to check agents")
 print(" - Use './multi-agent clean' to reset")
 print(" - Each agent operates independently")
 print()
 
 print("Next Steps:")
 
 return True

def show_agent_status():
 """Show current agent status"""
 script_dir = Path(__file__).parent
 status_script = script_dir / "multi-agent"
 
 if status_script.exists():
 subprocess.run([str(status_script), "status"])
 else:
 print(" multi-agent script not found")

def main():
 """Main entry point"""
 if len(sys.argv) < 2:
 print("WSL: WSL Multi-Agent Launcher")
 print("=" * 30)
 print()
 print("Usage:")
 print(" python3 wsl_launcher.py <workflow>")
 print()
 print("Available workflows:")
 print(" react-dev - React.js development team (6 agents)")
 print(" code-review - Code review team (3 agents)") 
 print(" minimal - Minimal setup (2 agents)")
 print(" status - Show current agent status")
 print(" clean - Clean up all agents")
 print()
 if is_wsl():
 print("WSL: WSL detected - agents will run in background mode")
 else:
 print("Not in WSL environment")
 return
 
 command = sys.argv[1]
 
 if command == "status":
 show_agent_status()
 elif command == "clean":
 script_dir = Path(__file__).parent
 clean_script = script_dir / "multi-agent"
 if clean_script.exists():
 subprocess.run([str(clean_script), "clean"])
 else:
 print(" cleanup script not found")
 elif command in ["react-dev", "code-review", "minimal"]:
 launch_wsl_workflow(command)
 else:
 print(f" Unknown command: {command}")

if __name__ == "__main__":
 main()
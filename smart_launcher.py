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
        print("ERROR: agent_workflows.json not found")
        return {}
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON in agent_workflows.json")
        return {}

def detect_system():
    """Detect the current system environment"""
    import platform
    
    # Check if running on Windows
    if platform.system() == "Windows":
        return "windows"
    
    # Check if running in WSL
    if os.path.exists("/proc/version"):
        try:
            with open("/proc/version", "r") as f:
                if "WSL" in f.read() or "Microsoft" in f.read():
                    return "wsl"
        except:
            pass
    
    # Check if running on macOS
    if platform.system() == "Darwin":
        return "macos"
    
    # Default to Linux
    return "linux"

def launch_agent(role, name, method="terminal"):
    """Launch a single agent"""
    script_dir = Path(__file__).parent
    agent_script = script_dir / "bin" / "multi_agent_terminal.py"
    
    if method == "terminal":
        system_type = detect_system()
        print(f"INFO: Detected system: {system_type}")
        
        if system_type == "wsl":
            # WSL-specific terminal launch using Windows Terminal or PowerShell
            # Note: multi_agent_terminal.py expects <agent_id> <role>
            wsl_terminals = [
                # Windows Terminal (preferred) - simplified command without read prompt
                ["wt.exe", "-w", "0", "new-tab", "--title", f"Agent: {role} ({name})", 
                 "bash", "-c", f"cd '{script_dir}' && python3 '{agent_script}' '{name}' '{role}'"],
                # PowerShell as fallback
                ["powershell.exe", "-Command", 
                 f"Start-Process powershell -ArgumentList '-NoExit', '-Command', \"wsl -e bash -c 'cd {script_dir} && python3 {agent_script} {name} {role}'\""],
                # CMD as last resort  
                ["cmd.exe", "/c", "start", "cmd", "/k", 
                 f"wsl -e bash -c \"cd '{script_dir}' && python3 '{agent_script}' '{name}' '{role}'\""]
            ]
            
            for terminal_cmd in wsl_terminals:
                try:
                    subprocess.Popen(terminal_cmd, cwd=script_dir)
                    print(f"SUCCESS: Launched {role} agent '{name}' in Windows terminal")
                    return True
                except (FileNotFoundError, OSError) as e:
                    print(f"WARNING: Failed to launch with {terminal_cmd[0]}: {e}")
                    continue
                    
        elif system_type == "windows":
            # Native Windows terminal launch
            windows_terminals = [
                ["cmd.exe", "/c", "start", "cmd", "/k", 
                 f"cd /d \"{script_dir}\" && python \"{agent_script}\" \"{role}\" \"{name}\""],
                ["powershell.exe", "-Command", 
                 f"Start-Process powershell -ArgumentList '-NoExit', '-Command', \"cd '{script_dir}'; python '{agent_script}' '{role}' '{name}'\""]
            ]
            
            for terminal_cmd in windows_terminals:
                try:
                    subprocess.Popen(terminal_cmd, cwd=script_dir)
                    print(f"SUCCESS: Launched {role} agent '{name}' in Windows terminal")
                    return True
                except (FileNotFoundError, OSError) as e:
                    print(f"WARNING:  Failed to launch with {terminal_cmd[0]}: {e}")
                    continue
                    
        elif system_type == "macos":
            # macOS terminal launch
            macos_terminals = [
                ["osascript", "-e", f'tell app "Terminal" to do script "cd \'{script_dir}\' && python3 \'{agent_script}\' \'{role}\' \'{name}\'"'],
                ["open", "-a", "Terminal", f"{script_dir}"]
            ]
            
            for terminal_cmd in macos_terminals:
                try:
                    subprocess.Popen(terminal_cmd, cwd=script_dir)
                    print(f"SUCCESS: Launched {role} agent '{name}' in macOS Terminal")
                    return True
                except (FileNotFoundError, OSError) as e:
                    print(f"WARNING:  Failed to launch with {terminal_cmd[0]}: {e}")
                    continue
                    
        else:  # Linux
            # Standard Linux terminal emulators
            linux_terminals = [
                ["gnome-terminal", "--title", f"Agent: {role} ({name})", 
                 "--working-directory", str(script_dir), "--", 
                 "python3", str(agent_script), role, name],
                ["xterm", "-title", f"Agent: {role} ({name})", "-e", 
                 "bash", "-c", f"cd '{script_dir}' && python3 '{agent_script}' '{role}' '{name}'; exec bash"],
                ["konsole", "--new-tab", "--title", f"Agent: {role} ({name})", 
                 "--workdir", str(script_dir), "-e", 
                 "python3", str(agent_script), role, name],
                ["terminator", "--new-tab", "--title", f"Agent: {role} ({name})", 
                 "--working-directory", str(script_dir), "-x",
                 "bash", "-c", f"python3 '{agent_script}' '{role}' '{name}'; exec bash"],
                ["alacritty", "--title", f"Agent: {role} ({name})", 
                 "--working-directory", str(script_dir), "-e",
                 "bash", "-c", f"python3 '{agent_script}' '{role}' '{name}'; exec bash"]
            ]
            
            for terminal_cmd in linux_terminals:
                try:
                    subprocess.Popen(terminal_cmd)
                    print(f"SUCCESS: Launched {role} agent '{name}' in {terminal_cmd[0]}")
                    return True
                except (FileNotFoundError, OSError) as e:
                    print(f"WARNING:  Failed to launch with {terminal_cmd[0]}: {e}")
                    continue
        
        # Fallback to background process
        print(f"WARNING:  No terminal emulator found for {system_type}, launching {role} agent '{name}' in background")
        if system_type == "wsl":
            print(f"TIP: Tip: Install Windows Terminal for better WSL experience")
        elif system_type == "linux":
            print(f"TIP: Tip: Install gnome-terminal, xterm, or konsole for terminal support")
        
        subprocess.Popen([sys.executable, str(agent_script), name, role], 
                        cwd=script_dir)
        return True
        
    elif method == "background":
        subprocess.Popen([sys.executable, str(agent_script), name, role], 
                        cwd=script_dir)
        print(f"Launched {role} agent '{name}' in background")
        return True
    
    return False

def monitor_agent_status(script_dir):
    """Monitor and display agent status after launch"""
    comm_dir = script_dir / ".agent_comm"
    agents_file = comm_dir / "agents.json"
    
    if agents_file.exists():
        try:
            with open(agents_file, 'r') as f:
                agents = json.load(f)
            
            if agents:
                print(f"\nSTATUS: Agent Status Monitor:")
                print("=" * 50)
                for agent in agents:
                    status_emoji = "[ACTIVE]" if agent.get("status") == "active" else "[INACTIVE]"
                    pid = agent.get("pid", "unknown")
                    role = agent.get("role", "unknown")
                    agent_id = agent.get("id", "unknown")
                    last_seen = agent.get("last_seen", "unknown")
                    
                    print(f"{status_emoji} {agent_id} ({role})")
                    print(f"   PID: {pid} | Last seen: {last_seen}")
                    
                print("\nTIP: Agent Communication Commands:")
                print("   Connect to coordinator: python3 bin/multi_agent_terminal.py coordinator main")
                print("   View all agents: Use 'agents' command in any agent terminal")
                print("   View tasks: Use 'tasks' command in coordinator")
                print("   Project status: Use 'project' command in coordinator")
            else:
                print("WAITING: Waiting for agents to register...")
        except Exception as e:
            print(f"WARNING:  Could not read agent status: {e}")
    else:
        print("WAITING: Agent communication system initializing...")

def launch_workflow(workflow_name, workflows, method="terminal"):
    """Launch all agents for a specific workflow"""
    if workflow_name not in workflows["workflows"]:
        print(f"ERROR: Workflow '{workflow_name}' not found")
        return False
    
    workflow = workflows["workflows"][workflow_name]
    print(f"LAUNCH: Launching workflow: {workflow_name}")
    print(f"INFO: Description: {workflow['description']}")
    print()
    
    script_dir = Path(__file__).parent
    success_count = 0
    coordinator_launched = False
    
    for agent in workflow["agents"]:
        if launch_agent(agent["role"], agent["name"], method):
            success_count += 1
            if agent["role"] == "coordinator":
                coordinator_launched = True
            time.sleep(1.5)  # Slightly longer delay for proper initialization
    
    print()
    print(f"SUCCESS: Successfully launched {success_count}/{len(workflow['agents'])} agents")
    
    # Give agents time to register
    if success_count > 0:
        print("\nWAITING: Waiting for agent registration...")
        time.sleep(3)
        
        # Show status and communication info
        monitor_agent_status(script_dir)
        
        if coordinator_launched:
            print(f"\nTARGET: Main Coordinator Interface:")
            print(f"   python3 bin/multi_agent_terminal.py coordinator main")
            print(f"\nINFO: Available Commands in Coordinator:")
            print(f"   - agents: View all active agents")
            print(f"   - tasks: View pending tasks")  
            print(f"   - project: Check current project status")
            print(f"   - set_project <name>: Focus on specific project")
            print(f"   - delegate \"task\" to agent_role: Assign tasks")
            print(f"   - files: View loaded project files")
        
        print(f"\n� System Monitoring:")
        print(f"   python3 agent_status.py              # One-time status check")
        print(f"   python3 agent_status.py --live 3     # Live monitoring (3s refresh)")
        
        print(f"\n�PROCESS: Inter-Agent Communication Features:")
        print(f"   SUCCESS: Unified communication system (.agent_comm/)")
        print(f"   SUCCESS: Background and terminal agents share same messaging")
        print(f"   SUCCESS: Real-time task delegation and status updates")
        print(f"   SUCCESS: Cross-agent visibility regardless of launch method")
        print(f"   SUCCESS: Persistent communication state across sessions")
    
    return True

def show_available_workflows(workflows):
    """Display available workflow configurations"""
    print("CONFIG: Available Workflows:")
    print("=" * 50)
    
    for name, config in workflows["workflows"].items():
        print(f"\nPACKAGE: {name}")
        print(f"   {config['description']}")
        print(f"   AGENTS: Agents: {len(config['agents'])}")
        for agent in config["agents"]:
            print(f"   • {agent['role']} ({agent['name']})")

def show_usage():
    """Show usage information"""
    print("AGENT: Smart Multi-Agent Launcher")
    print("=" * 40)
    print()
    print("INFO: Usage:")
    print("  python3 smart_launcher.py guided                   # RECOMMENDED: Interactive guided mode")
    print("  python3 smart_launcher.py <workflow_name>           # Launch workflow in terminals")
    print("  python3 smart_launcher.py <workflow_name> --bg      # Launch workflow in background") 
    print("  python3 smart_launcher.py --list                   # List available workflows")
    print("  python3 smart_launcher.py --custom role1:name1 ... # Launch custom agents")
    print("  python3 smart_launcher.py --connect                # Show connection guide")
    print("  python3 smart_launcher.py --help                   # Show this help + connection guide")
    print()
    print("TIP: Examples:")
    print("  python3 smart_launcher.py guided                   # NEW: Start with coordinator assistant")
    print("  python3 smart_launcher.py ai-development           # Universal AI development team")
    print("  python3 smart_launcher.py code-review --bg         # Background code review team")
    print("  python3 smart_launcher.py --custom coordinator:main coder:dev  # Custom setup")

def launch_custom_agents(agent_specs, method="terminal"):
    """Launch custom agent configuration"""
    print("TOOLS: Launching custom agent configuration")
    
    script_dir = Path(__file__).parent
    success_count = 0
    coordinator_launched = False
    
    for spec in agent_specs:
        if ":" not in spec:
            print(f"ERROR: Invalid format: {spec} (use role:name)")
            continue
        
        role, name = spec.split(":", 1)
        if launch_agent(role, name, method):
            success_count += 1
            if role == "coordinator":
                coordinator_launched = True
            time.sleep(1.5)
    
    print(f"SUCCESS: Successfully launched {success_count}/{len(agent_specs)} agents")
    
    # Show status and connection info for custom launches too
    if success_count > 0:
        print("\nWAITING: Waiting for agent registration...")
        time.sleep(3)
        
        monitor_agent_status(script_dir)
        
        if coordinator_launched:
            print(f"\nTARGET: Connect to Coordinator:")
            print(f"   python3 bin/multi_agent_terminal.py coordinator main")

def show_connection_help():
    """Show help for connecting to agents"""
    print("\nLINK: Agent Connection Guide:")
    print("=" * 40)
    print("INFO: Connect to specific agents:")
    print("   coordinator: python3 bin/multi_agent_terminal.py coordinator main")
    print("   coder:       python3 bin/multi_agent_terminal.py coder dev") 
    print("   file_manager: python3 bin/multi_agent_terminal.py file_manager files")
    print("   code_reviewer: python3 bin/multi_agent_terminal.py code_reviewer reviewer")
    print("   code_rewriter: python3 bin/multi_agent_terminal.py code_rewriter fixer")
    print("   git_manager: python3 bin/multi_agent_terminal.py git_manager git")
    print()
    print("� System Status & Monitoring:")
    print("   python3 agent_status.py              # Check current system status")
    print("   python3 agent_status.py --live 3     # Live monitoring (3 second refresh)")
    print("   python3 agent_status.py --live 10    # Live monitoring (10 second refresh)")
    print()
    print("PROCESS: Agent Communication Features:")
    print("   SUCCESS: Universal communication system works with background & terminal agents")
    print("   SUCCESS: Real-time inter-agent messaging via .agent_comm/ directory")
    print("   SUCCESS: Persistent task delegation and status tracking")
    print("   SUCCESS: Use 'agents' command in any agent to see all active agents")
    print("   SUCCESS: Use 'tasks' command in coordinator to view pending work")
    print("   SUCCESS: Use 'delegate \"task\" to role' for intelligent task assignment")
    print("   SUCCESS: All agents maintain project context regardless of launch method")

def launch_guided_mode():
    """Launch guided interactive mode with main coordinator"""
    print("GUIDED: Starting Interactive AI Development Assistant")
    print("=" * 55)
    print("")
    print("FRAMEWORK: Universal AI-powered development (React, Vue, Python, Node.js, Java, Go, C#, Rust)")
    print("")
    print("LAUNCH: Starting main coordinator...")
    
    # Launch only the coordinator agent
    system_type = detect_system()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    agent_script = os.path.join(script_dir, "bin", "multi_agent_terminal.py")
    
    success = launch_agent("coordinator", "main", method="terminal")
    
    if success:
        print("SUCCESS: Main coordinator started")
        print("")
        print("CONNECT: Connect to your AI assistant:")
        print(f"   python3 bin/multi_agent_terminal.py main coordinator")
        print("")
        print("INFO: The coordinator will guide you through:")
        print("   - Creating new projects")
        print("   - Selecting development frameworks") 
        print("   - Spawning additional specialized agents")
        print("   - Managing your development workflow")
        print("")
        print("TIP: Just connect to the coordinator and say what you want to build!")
    else:
        print("ERROR: Failed to start coordinator")

def main():
    """Main entry point"""
    workflows = load_workflows()
    
    if not workflows:
        print("ERROR: No workflows available")
        return
    
    if len(sys.argv) < 2:
        show_usage()
        return
    
    command = sys.argv[1]
    method = "background" if "--bg" in sys.argv else "terminal"
    
    if command == "--list":
        show_available_workflows(workflows)
    elif command == "--help" or command == "-h":
        show_usage()
        show_connection_help()
    elif command == "--connect":
        show_connection_help()
    elif command == "guided" or command == "--guided":
        launch_guided_mode()
        return
    elif command == "--custom":
        agent_specs = [arg for arg in sys.argv[2:] if not arg.startswith("--")]
        if not agent_specs:
            print("ERROR: No agent specifications provided")
            show_usage()
            return
        launch_custom_agents(agent_specs, method)
    elif command in workflows["workflows"]:
        launch_workflow(command, workflows, method)
    else:
        print(f"ERROR: Unknown workflow or command: {command}")
        show_available_workflows(workflows)
        show_connection_help()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Agent Cleanup Script - Deactivate all agents and clean workspace
"""

import os
import json
import signal
import sys
import subprocess
from pathlib import Path

def get_agent_pids():
    """Get all active agent PIDs from the agents.json file"""
    agents_file = ".agent_comm/agents.json"
    
    if not os.path.exists(agents_file):
        print("❌ No agents file found")
        return []
    
    try:
        with open(agents_file, 'r') as f:
            agents = json.load(f)
        
        pids = []
        for agent in agents:
            if agent.get('status') == 'active' and 'pid' in agent:
                pids.append({
                    'id': agent['id'],
                    'pid': agent['pid'],
                    'role': agent['role']
                })
        
        return pids
    except Exception as e:
        print(f"❌ Error reading agents file: {e}")
        return []

def kill_agent_processes(agent_pids):
    """Safely terminate agent processes"""
    killed_count = 0
    
    for agent_info in agent_pids:
        pid = agent_info['pid']
        agent_id = agent_info['id']
        role = agent_info['role']
        
        try:
            # Check if process exists
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                
                # Check if it's actually a Python process (safety check)
                if 'python' in process.name().lower():
                    print(f"Terminating {role} agent '{agent_id}' (PID: {pid})")
                    process.terminate()
                    
                    # Wait a bit for graceful shutdown
                    try:
                        process.wait(timeout=3)
                        print(f"Agent '{agent_id}' terminated gracefully")
                    except psutil.TimeoutExpired:
                        # Force kill if needed
                        process.kill()
                        print(f"⚠Agent '{agent_id}' force killed")
                    
                    killed_count += 1
                else:
                    print(f"⚠PID {pid} is not a Python process, skipping")
            else:
                print(f"ℹAgent '{agent_id}' (PID: {pid}) already terminated")
                
        except psutil.NoSuchProcess:
            print(f"ℹAgent '{agent_id}' process not found")
        except psutil.AccessDenied:
            print(f"❌ Access denied to terminate agent '{agent_id}' (PID: {pid})")
        except Exception as e:
            print(f"❌ Error terminating agent '{agent_id}': {e}")
    
    return killed_count

def clean_communication_files():
    """Clean up agent communication files"""
    comm_dir = Path(".agent_comm")
    
    if not comm_dir.exists():
        print("ℹNo communication directory found")
        return
    
    files_to_clean = ["agents.json", "tasks.json", "messages.json"]
    
    for filename in files_to_clean:
        file_path = comm_dir / filename
        try:
            if file_path.exists():
                # Create empty file with proper structure
                if filename == "agents.json":
                    with open(file_path, 'w') as f:
                        json.dump([], f, indent=2)
                elif filename == "tasks.json":
                    with open(file_path, 'w') as f:
                        json.dump([], f, indent=2)
                elif filename == "messages.json":
                    with open(file_path, 'w') as f:
                        json.dump([], f, indent=2)
                
                print(f"🧹 Cleaned {filename}")
            else:
                print(f"ℹ{filename} not found")
        except Exception as e:
            print(f"❌ Error cleaning {filename}: {e}")

def kill_orphaned_processes():
    """Find and kill any orphaned multi_agent_terminal processes"""
    killed_count = 0
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Look for Python processes running multi_agent_terminal.py
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('multi_agent_terminal.py' in cmd for cmd in cmdline):
                    print(f"Found orphaned agent process: PID {proc.info['pid']}")
                    
                    process = psutil.Process(proc.info['pid'])
                    process.terminate()
                    
                    try:
                        process.wait(timeout=3)
                        print(f"Orphaned process {proc.info['pid']} terminated")
                    except psutil.TimeoutExpired:
                        process.kill()
                        print(f"⚠Orphaned process {proc.info['pid']} force killed")
                    
                    killed_count += 1
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    except Exception as e:
        print(f"❌ Error scanning for orphaned processes: {e}")
    
    return killed_count

def main():
    """Main cleanup function"""
    print("🧹 Multi-Agent System Cleanup")
    print("=" * 50)
    
    # Change to the correct directory
    if not os.path.exists('.agent_comm'):
        print("❌ Not in multi-agent directory. Please run from the multi-agent folder.")
        sys.exit(1)
    
    # Step 1: Get active agent PIDs
    print("Finding active agents...")
    agent_pids = get_agent_pids()
    
    if agent_pids:
        print(f"Found {len(agent_pids)} active agent(s):")
        for agent_info in agent_pids:
            print(f"   • {agent_info['role']}: {agent_info['id']} (PID: {agent_info['pid']})")
        
        # Step 2: Terminate agent processes
        print(f"\nTerminating {len(agent_pids)} agent(s)...")
        killed_count = kill_agent_processes(agent_pids)
        print(f"Terminated {killed_count} agent(s)")
    else:
        print("ℹNo active agents found in agents.json")
    
    # Step 3: Look for orphaned processes
    print(f"\nScanning for orphaned agent processes...")
    orphaned_count = kill_orphaned_processes()
    if orphaned_count > 0:
        print(f"Cleaned up {orphaned_count} orphaned process(es)")
    else:
        print("ℹNo orphaned processes found")
    
    # Step 4: Clean communication files
    print(f"\n🧹 Cleaning communication files...")
    clean_communication_files()
    
    # Step 5: Final status
    print(f"\nCleanup Complete!")
    print("Multi-agent system is now clean and ready for fresh start")
    print("\nTo start agents again, use:")
    print("   ./bin/multi_agent_terminal.py <role>")
    print("   ./launch_agents.sh")
    print("   ./multi-agent")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Simple Agent Cleanup Script - Deactivate all agents and clean workspace
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
    """Safely terminate agent processes using system calls"""
    killed_count = 0
    
    for agent_info in agent_pids:
        pid = agent_info['pid']
        agent_id = agent_info['id']
        role = agent_info['role']
        
        try:
            # Check if process exists using kill -0
            result = subprocess.run(['kill', '-0', str(pid)], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Terminating {role} agent '{agent_id}' (PID: {pid})")
                
                # Try graceful termination first (SIGTERM)
                subprocess.run(['kill', '-TERM', str(pid)], 
                             capture_output=True, text=True)
                
                # Wait a bit and check if it's gone
                import time
                time.sleep(2)
                
                # Check if still running
                check_result = subprocess.run(['kill', '-0', str(pid)], 
                                            capture_output=True, text=True)
                
                if check_result.returncode == 0:
                    # Still running, force kill
                    print(f"⚠Force killing agent '{agent_id}' (PID: {pid})")
                    subprocess.run(['kill', '-KILL', str(pid)], 
                                 capture_output=True, text=True)
                else:
                    print(f"Agent '{agent_id}' terminated gracefully")
                
                killed_count += 1
            else:
                print(f"ℹAgent '{agent_id}' (PID: {pid}) already terminated")
                
        except Exception as e:
            print(f"❌ Error terminating agent '{agent_id}': {e}")
    
    return killed_count

def kill_orphaned_processes():
    """Find and kill any orphaned multi_agent_terminal processes"""
    killed_count = 0
    
    try:
        # Find processes containing 'multi_agent_terminal.py'
        result = subprocess.run(['pgrep', '-f', 'multi_agent_terminal.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid.strip():
                    print(f"Found orphaned agent process: PID {pid}")
                    
                    # Kill the process
                    subprocess.run(['kill', '-TERM', pid], 
                                 capture_output=True, text=True)
                    
                    import time
                    time.sleep(1)
                    
                    # Force kill if still running
                    check_result = subprocess.run(['kill', '-0', pid], 
                                                capture_output=True, text=True)
                    if check_result.returncode == 0:
                        subprocess.run(['kill', '-KILL', pid], 
                                     capture_output=True, text=True)
                        print(f"⚠Force killed orphaned process {pid}")
                    else:
                        print(f"Orphaned process {pid} terminated")
                    
                    killed_count += 1
        else:
            print("ℹNo orphaned agent processes found")
    
    except Exception as e:
        print(f"❌ Error scanning for orphaned processes: {e}")
    
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
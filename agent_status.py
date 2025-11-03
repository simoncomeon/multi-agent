#!/usr/bin/env python3
"""
Multi-Agent Status Monitor - Real-time agent communication and task visualization
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime

class AgentStatusMonitor:
    def __init__(self, workspace_dir=None):
        if workspace_dir is None:
            # Match multi_agent_terminal.py logic for workspace directory
            current_dir = os.getcwd()
            if current_dir.endswith('/bin'):
                workspace_dir = os.path.join(os.path.dirname(current_dir), 'workspace')
            elif os.path.exists('workspace'):
                workspace_dir = 'workspace'
            else:
                workspace_dir = "."
        self.workspace_dir = Path(workspace_dir)
        self.comm_dir = self.workspace_dir / ".agent_comm"
        
        # Communication files
        self.agents_file = self.comm_dir / "agents.json"
        self.tasks_file = self.comm_dir / "tasks.json"  
        self.messages_file = self.comm_dir / "messages.json"
    
    def load_json_file(self, file_path):
        """Safely load JSON file"""
        try:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            return []
    
    def get_agents(self):
        """Get all registered agents"""
        return self.load_json_file(self.agents_file)
    
    def get_tasks(self):
        """Get all tasks"""
        return self.load_json_file(self.tasks_file)
    
    def get_messages(self):
        """Get all messages"""
        return self.load_json_file(self.messages_file)
    
    def display_status(self):
        """Display comprehensive system status"""
        print("\nAGENT: Multi-Agent System Status")
        print("=" * 60)
        
        # Agent Status
        agents = self.get_agents()
        if agents:
            print(f"\nAGENTS: Active Agents ({len(agents)}):")
            for agent in agents:
                status_emoji = "[ACTIVE]" if agent.get("status") == "active" else "[INACTIVE]"
                pid = agent.get("pid", "unknown")
                role = agent.get("role", "unknown")
                agent_id = agent.get("id", "unknown")
                last_seen = agent.get("last_seen", "unknown")
                
                # Parse last seen time
                try:
                    last_dt = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                    time_diff = datetime.now() - last_dt.replace(tzinfo=None)
                    if time_diff.total_seconds() < 60:
                        time_str = f"{int(time_diff.total_seconds())}s ago"
                    elif time_diff.total_seconds() < 3600:
                        time_str = f"{int(time_diff.total_seconds() / 60)}m ago"
                    else:
                        time_str = f"{int(time_diff.total_seconds() / 3600)}h ago"
                except:
                    time_str = "unknown"
                
                print(f"  {status_emoji} {agent_id:<15} ({role:<15}) PID: {pid:<8} Last: {time_str}")
        else:
            print("\nERROR: No agents currently registered")
        
        # Task Status
        tasks = self.get_tasks()
        if tasks:
            print(f"\nINFO: Tasks ({len(tasks)}):")
            for task in tasks:
                task_id = task.get("id", "unknown")[:8]
                status = task.get("status", "unknown")
                assigned_to = task.get("assigned_to", "unknown")
                description = task.get("description", "No description")[:50]
                
                status_emoji = {"pending": "WAITING:", "in_progress": "PROCESS:", "completed": "SUCCESS:", "failed": "ERROR:"}.get(status, "[UNKNOWN]")
                
                print(f"  {status_emoji} {task_id} → {assigned_to:<15} | {description}...")
        else:
            print("\nINFO: No tasks in system")
        
        # Recent Messages
        messages = self.get_messages()
        if messages:
            recent_messages = sorted(messages, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
            print(f"\nMESSAGE: Recent Messages ({len(recent_messages)}):")
            for msg in recent_messages:
                sender = msg.get("from_agent", "unknown")
                recipient = msg.get("to_agent", "unknown")  
                msg_type = msg.get("type", "unknown")
                timestamp = msg.get("timestamp", "")
                
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime("%H:%M:%S")
                except:
                    time_str = "unknown"
                
                print(f"  MESSAGE: {time_str} | {sender} → {recipient} ({msg_type})")
        
        print(f"\nLINK: Connection Commands:")
        print(f"  Main coordinator: python3 bin/multi_agent_terminal.py coordinator main")
        if agents:
            for agent in agents:
                role = agent.get("role", "unknown")
                agent_id = agent.get("id", "unknown")
                if role != "coordinator":
                    print(f"  {role.capitalize()}: python3 bin/multi_agent_terminal.py {role} {agent_id}")
        
        print(f"\nPROCESS: Communication Status:")
        comm_status = "[ACTIVE] Active" if self.comm_dir.exists() else "[INACTIVE] Inactive"
        print(f"  System: {comm_status}")
        print(f"  Comm directory: {self.comm_dir}")
        print(f"  Agents file: {'SUCCESS:' if self.agents_file.exists() else 'ERROR:'}")
        print(f"  Tasks file: {'SUCCESS:' if self.tasks_file.exists() else 'ERROR:'}")
        print(f"  Messages file: {'SUCCESS:' if self.messages_file.exists() else 'ERROR:'}")

    def monitor_live(self, refresh_interval=5):
        """Monitor system status with live updates"""
        print("PROCESS: Starting live monitor (Ctrl+C to exit)")
        print(f"TIME: Refresh interval: {refresh_interval} seconds")
        
        try:
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')
                self.display_status()
                print(f"\nTIME: Next update in {refresh_interval}s... (Ctrl+C to exit)")
                time.sleep(refresh_interval)
        except KeyboardInterrupt:
            print("\nEXIT: Monitor stopped by user")

def main():
    import sys
    
    monitor = AgentStatusMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        refresh = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        monitor.monitor_live(refresh)
    else:
        monitor.display_status()
        print("\nTIP: Use --live [seconds] for continuous monitoring")
        print("   Example: python3 agent_status.py --live 3")

if __name__ == "__main__":
    main()
"""
Agent Lifecycle Management - Handles agent spawning, monitoring, and cleanup
"""

import os
import signal
import subprocess
import time
from datetime import datetime
from typing import Dict, List

from ..core.models import AgentRole, Colors
from ..core.utils import colored_print


class AgentLifecycleManager:
    """Manages agent lifecycle operations - spawn, kill, restart, status"""
    
    def __init__(self, terminal_instance, comm_instance):
        self.terminal = terminal_instance
        self.comm = comm_instance
        self.workspace_dir = terminal_instance.workspace_dir
    
    def kill_agent(self, agent_id: str) -> Dict:
        """Kill a specific agent by ID"""
        
        colored_print(f"LIFECYCLE: Attempting to kill agent '{agent_id}'", Colors.BRIGHT_RED)
        
        # Get agent information
        agent_info = self.comm.get_agent_status(agent_id)
        if not agent_info:
            colored_print(f"   ERROR: Agent '{agent_id}' not found in registry", Colors.RED)
            return {
                "status": "failed",
                "message": f"Agent '{agent_id}' not found",
                "agent_id": agent_id
            }
        
        # Attempt to kill the process
        success = self.comm.kill_agent_by_pid(agent_id)
        
        if success:
            # Update agent status to inactive
            self.comm.unregister_agent(agent_id)
            
            colored_print(f"   SUCCESS: Agent '{agent_id}' killed successfully", Colors.GREEN)
            return {
                "status": "success",
                "message": f"Agent '{agent_id}' killed successfully",
                "agent_id": agent_id,
                "pid": agent_info.get("pid")
            }
        else:
            colored_print(f"   WARNING: Could not kill agent '{agent_id}' process", Colors.YELLOW)
            # Still mark as inactive since process might already be dead
            self.comm.unregister_agent(agent_id)
            
            return {
                "status": "partial",
                "message": f"Agent '{agent_id}' marked as inactive (process may have already died)",
                "agent_id": agent_id
            }
    
    def restart_agent(self, agent_id: str) -> Dict:
        """Restart a specific agent"""
        
        colored_print(f"LIFECYCLE: Restarting agent '{agent_id}'", Colors.BRIGHT_YELLOW)
        
        # First, kill the existing agent
        kill_result = self.kill_agent(agent_id)
        
        # Wait a moment for cleanup
        time.sleep(1)
        
        # Get the agent role from the old registration
        agent_info = self.comm.get_agent_status(agent_id)
        if agent_info:
            agent_role = agent_info.get("role")
        else:
            # Default role if not found
            agent_role = "general"
        
        # Spawn new agent with same role
        spawn_result = self.spawn_new_agent(agent_role, agent_id)
        
        if spawn_result.get("status") == "success":
            colored_print(f"   SUCCESS: Agent '{agent_id}' restarted successfully", Colors.GREEN)
            return {
                "status": "success",
                "message": f"Agent '{agent_id}' restarted successfully",
                "agent_id": agent_id,
                "new_pid": spawn_result.get("pid"),
                "kill_result": kill_result,
                "spawn_result": spawn_result
            }
        else:
            colored_print(f"   ERROR: Failed to restart agent '{agent_id}'", Colors.RED)
            return {
                "status": "failed",
                "message": f"Failed to restart agent '{agent_id}'",
                "agent_id": agent_id,
                "kill_result": kill_result,
                "spawn_result": spawn_result
            }
    
    def spawn_new_agent(self, role: str, agent_id: str = None) -> Dict:
        """Spawn a new agent with specified role"""
        
        if not agent_id:
            agent_id = f"{role}_{int(time.time())}"
        
        colored_print(f"LIFECYCLE: Spawning new agent '{agent_id}' with role '{role}'", Colors.BRIGHT_GREEN)
        
        try:
            # Determine the script path
            script_path = os.path.join(self.workspace_dir, "bin", "multi_agent_terminal.py")
            if not os.path.exists(script_path):
                # Try alternative paths
                script_path = os.path.join(os.path.dirname(__file__), "..", "..", "bin", "multi_agent_terminal.py")
            
            # Prepare command
            cmd = [
                "python3", script_path,
                "--agent-id", agent_id,
                "--role", role,
                "--workspace", self.workspace_dir
            ]
            
            # Start the process in background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.workspace_dir
            )
            
            # Register the new agent
            try:
                agent_role = AgentRole(role)
            except ValueError:
                agent_role = AgentRole.GENERAL
            
            self.comm.register_agent(agent_id, agent_role, "active")
            
            colored_print(f"   SUCCESS: Agent '{agent_id}' spawned with PID {process.pid}", Colors.GREEN)
            
            return {
                "status": "success",
                "message": f"Agent '{agent_id}' spawned successfully",
                "agent_id": agent_id,
                "role": role,
                "pid": process.pid
            }
            
        except Exception as e:
            colored_print(f"   ERROR: Failed to spawn agent '{agent_id}': {str(e)}", Colors.RED)
            return {
                "status": "failed",
                "message": f"Failed to spawn agent '{agent_id}': {str(e)}",
                "agent_id": agent_id,
                "error": str(e)
            }
    
    def show_agent_status(self) -> Dict:
        """Show status of all agents in the system"""
        
        colored_print(f"LIFECYCLE: Gathering agent status information", Colors.BRIGHT_CYAN)
        
        agents = self.comm.load_agents()
        
        if not agents:
            colored_print(f"   INFO: No agents registered in the system", Colors.YELLOW)
            return {
                "status": "success",
                "total_agents": 0,
                "active_agents": 0,
                "inactive_agents": 0,
                "agents": []
            }
        
        active_count = 0
        inactive_count = 0
        agent_details = []
        
        colored_print(f"\\n=== AGENT STATUS REPORT ===", Colors.BRIGHT_WHITE)
        
        for agent in agents:
            agent_id = agent.get("id", "unknown")
            role = agent.get("role", "unknown")
            status = agent.get("status", "unknown")
            pid = agent.get("pid", "N/A")
            last_seen = agent.get("last_seen", "never")
            
            if status == "active":
                active_count += 1
                status_color = Colors.GREEN
            else:
                inactive_count += 1
                status_color = Colors.RED
            
            # Check if process is actually running
            process_status = "unknown"
            if pid and pid != "N/A":
                try:
                    os.kill(pid, 0)  # Check if process exists
                    process_status = "running"
                except ProcessLookupError:
                    process_status = "dead"
                except PermissionError:
                    process_status = "no_access"
            
            colored_print(f"  Agent: {agent_id}", Colors.BRIGHT_YELLOW)
            colored_print(f"    Role: {role}", Colors.WHITE)
            colored_print(f"    Status: {status}", status_color)
            colored_print(f"    PID: {pid}", Colors.WHITE)
            colored_print(f"    Process: {process_status}", Colors.CYAN)
            colored_print(f"    Last Seen: {last_seen}", Colors.WHITE)
            colored_print("", Colors.WHITE)
            
            agent_details.append({
                "id": agent_id,
                "role": role,
                "status": status,
                "pid": pid,
                "process_status": process_status,
                "last_seen": last_seen
            })
        
        colored_print(f"=== SUMMARY ===", Colors.BRIGHT_WHITE)
        colored_print(f"  Total Agents: {len(agents)}", Colors.WHITE)
        colored_print(f"  Active: {active_count}", Colors.GREEN)
        colored_print(f"  Inactive: {inactive_count}", Colors.RED)
        
        return {
            "status": "success",
            "total_agents": len(agents),
            "active_agents": active_count,
            "inactive_agents": inactive_count,
            "agents": agent_details
        }
    
    def cleanup_inactive_agents(self) -> Dict:
        """Remove inactive agents from the registry"""
        
        colored_print(f"LIFECYCLE: Cleaning up inactive agents", Colors.BRIGHT_YELLOW)
        
        agents = self.comm.load_agents()
        inactive_agents = [agent for agent in agents if agent.get("status") != "active"]
        
        if not inactive_agents:
            colored_print(f"   INFO: No inactive agents to clean up", Colors.GREEN)
            return {
                "status": "success",
                "message": "No inactive agents found",
                "cleaned_count": 0
            }
        
        cleaned_count = 0
        for agent in inactive_agents:
            agent_id = agent.get("id")
            if agent_id:
                self.comm.remove_agent(agent_id)
                cleaned_count += 1
                colored_print(f"   REMOVED: Agent '{agent_id}' from registry", Colors.YELLOW)
        
        colored_print(f"   SUCCESS: Cleaned up {cleaned_count} inactive agents", Colors.GREEN)
        
        return {
            "status": "success",
            "message": f"Cleaned up {cleaned_count} inactive agents",
            "cleaned_count": cleaned_count,
            "cleaned_agents": [agent.get("id") for agent in inactive_agents]
        }
    
    def health_check_agents(self) -> Dict:
        """Perform health check on all registered agents"""
        
        colored_print(f"LIFECYCLE: Performing agent health check", Colors.BRIGHT_CYAN)
        
        agents = self.comm.get_active_agents()
        
        if not agents:
            return {
                "status": "success",
                "message": "No active agents to check",
                "healthy_count": 0,
                "unhealthy_count": 0
            }
        
        healthy_count = 0
        unhealthy_count = 0
        unhealthy_agents = []
        
        for agent in agents:
            agent_id = agent.get("id")
            pid = agent.get("pid")
            
            if not pid:
                unhealthy_count += 1
                unhealthy_agents.append({"id": agent_id, "issue": "no_pid"})
                continue
            
            try:
                # Check if process is running
                os.kill(pid, 0)
                healthy_count += 1
                colored_print(f"   HEALTHY: Agent '{agent_id}' (PID: {pid})", Colors.GREEN)
            except ProcessLookupError:
                unhealthy_count += 1
                unhealthy_agents.append({"id": agent_id, "issue": "process_dead", "pid": pid})
                colored_print(f"   UNHEALTHY: Agent '{agent_id}' process dead (PID: {pid})", Colors.RED)
                
                # Auto-deactivate dead agents
                self.comm.unregister_agent(agent_id)
            except PermissionError:
                # Can't check, assume healthy
                healthy_count += 1
                colored_print(f"   UNKNOWN: Agent '{agent_id}' (PID: {pid}) - permission denied", Colors.YELLOW)
        
        colored_print(f"   HEALTH CHECK COMPLETE: {healthy_count} healthy, {unhealthy_count} unhealthy", Colors.WHITE)
        
        return {
            "status": "success",
            "message": f"Health check complete: {healthy_count} healthy, {unhealthy_count} unhealthy",
            "healthy_count": healthy_count,
            "unhealthy_count": unhealthy_count,
            "unhealthy_agents": unhealthy_agents
        }
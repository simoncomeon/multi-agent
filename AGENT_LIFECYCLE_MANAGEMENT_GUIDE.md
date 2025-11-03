# 🛠️ Agent Lifecycle Management Guide

## Complete Guide to Managing Agent Health, Fault Recovery, and Dynamic Scaling

### 🎯 **Overview**

The multi-agent system now includes production-grade agent lifecycle management for:
- **Health Monitoring** - Real-time agent status and process verification
- **Fault Recovery** - Kill, restart, and respawn problematic agents
- **Dynamic Scaling** - Add/remove agents based on workload needs
- **System Maintenance** - Cleanup inactive agents and optimize registry

---

## 📊 **Agent Health Monitoring**

### **List All Active Agents**
```bash
agents
```
**Output:**
```
Active Agents (6):
  main (coordinator) - PID: 12345
  files (file_manager) - PID: 12346  
  dev (coder) - PID: 12347
  reviewer (code_reviewer) - PID: 12348
  fixer (code_rewriter) - PID: 12349
  git (git_manager) - PID: 12350
```

### **Detailed Agent Status Check**
```bash
status files
```
**Output:**
```
AGENT STATUS: files
   ID: files
   Role: file_manager
   Status: active ✓
   PID: 12346
   Last Seen: 2025-11-03T15:30:25.123456
   Process: RUNNING ✓
   Pending Tasks: 2
      • task_123: Create React component for time display...
      • task_124: Organize project structure for...
```

### **System Overview**
```bash
# Check project focus
project

# View loaded files
files  

# Check task queue
tasks
```

---

## ⚡ **Fault Recovery Operations**

### **Kill Faulty Agent**
```bash
# Remove problematic agent completely
kill agent_name

# Examples:
kill files              # Kill file_manager by name
kill file_manager       # Kill by role  
kill problematic_coder  # Kill by ID
```

**What happens:**
1. **Process Termination** - Sends SIGTERM to agent process
2. **Registry Removal** - Removes from active agents list
3. **Task Cleanup** - Pending tasks remain for reassignment
4. **Clean Shutdown** - Graceful termination when possible

### **Restart Agent (Recommended)**
```bash
# Kill and respawn with same role
restart agent_name

# Examples:
restart reviewer        # Restart code_reviewer
restart files          # Restart file_manager
restart git            # Restart git_manager
```

**Restart Process:**
1. **Health Check** - Verify current agent status
2. **Graceful Kill** - Terminate existing process
3. **Wait Period** - 1-second pause for cleanup
4. **Respawn** - Launch new instance with same role
5. **Re-registration** - Agent re-registers in system
6. **Status Verification** - Confirm successful restart

---

## 🚀 **Dynamic Agent Scaling**

### **Spawn New Specialized Agents**
```bash
spawn <role> <name>

# Examples:
spawn tester qa_specialist
spawn researcher tech_research  
spawn coder frontend_specialist
spawn code_reviewer security_reviewer
```

**Available Roles:**
- `coordinator` - Project orchestration
- `file_manager` - File operations and project structure
- `coder` - Code generation and analysis
- `code_reviewer` - Quality assurance and review
- `code_rewriter` - Bug fixes and optimization  
- `git_manager` - Version control operations
- `researcher` - Information gathering
- `tester` - Testing and validation

### **Specialized Team Examples**

#### **Frontend Development Team**
```bash
spawn coder react_specialist
spawn coder css_specialist  
spawn code_reviewer ui_reviewer
spawn tester frontend_tester
```

#### **Backend Development Team**
```bash
spawn coder api_developer
spawn coder database_specialist
spawn code_reviewer security_reviewer
spawn tester integration_tester
```

#### **Quality Assurance Team**
```bash
spawn code_reviewer quality_lead
spawn code_reviewer performance_reviewer
spawn tester unit_tester
spawn tester integration_tester
```

---

## 🧹 **System Maintenance**

### **Clean Up Inactive Agents**
```bash
cleanup
```
**Output:**
```
AGENT MANAGEMENT: Cleaning up inactive agents
FOUND: 3 inactive agents to remove
SUCCESS: Removed 3 inactive agents  
ACTIVE: 6 agents remain active
```

**What gets cleaned:**
- Agents with status "inactive"
- Orphaned registry entries  
- Zombie processes that failed to unregister
- Corrupted agent records

### **Complete System Health Check**
```bash
# 1. Check all agents
agents

# 2. Clean inactive entries
cleanup

# 3. Verify system status  
./multi-agent status

# 4. Check communication health
ls -la workspace/.agent_comm/
```

---

## 🎯 **Practical Workflows**

### **Scenario 1: File Manager Acting Strange**
```bash
# 1. Check current status
status files

# 2. Check if process is actually running  
# (status command shows this automatically)

# 3. Restart if needed
restart files

# 4. Verify recovery
status files
```

### **Scenario 2: Code Reviewer Stuck on Task**
```bash
# 1. Check what's happening
status reviewer
tasks

# 2. Kill the stuck agent
kill reviewer

# 3. Clean up and spawn new one
cleanup
spawn code_reviewer new_reviewer

# 4. Verify new agent is working
status new_reviewer
```

### **Scenario 3: Scale Up for Complex Project**
```bash
# 1. Assess current team
agents

# 2. Add specialized agents
spawn code_reviewer security_expert
spawn code_reviewer performance_expert  
spawn coder react_specialist
spawn tester automation_tester

# 3. Verify team is ready
agents

# 4. Start delegating specialized tasks
delegate "security audit of authentication system" to security_expert
delegate "performance optimization of React components" to performance_expert
```

### **Scenario 4: Scale Down After Project Completion**
```bash
# 1. Identify temporary agents
agents

# 2. Remove specialized agents
kill security_expert
kill performance_expert
kill react_specialist

# 3. Clean up registry
cleanup

# 4. Keep core team
agents  # Should show basic coordinator, file_manager, coder, reviewer, git_manager
```

---

## 🔧 **Advanced Operations**

### **Agent Health Monitoring Script**
```bash
#!/bin/bash
# health_check.sh - Monitor all agents

echo "=== Agent Health Report ==="
agents
echo ""

echo "=== System Status ==="
./multi-agent status
echo ""

echo "=== Cleanup Report ==="
cleanup
```

### **Emergency Recovery Procedure**
```bash
# If system is completely broken:

# 1. Kill all agents
for agent in main files dev reviewer fixer git; do
    kill $agent 2>/dev/null
done

# 2. Clean communication files
./multi-agent clean

# 3. Remove all agent records  
cleanup

# 4. Restart system
python3 smart_launcher.py ai-development

# 5. Verify recovery
sleep 5
agents
```

### **Monitoring Agent Process Health**
```bash
# Check if agent processes are actually running
ps aux | grep multi_agent_terminal

# Check agent communication directory
ls -la workspace/.agent_comm/

# Verify agent registry integrity
cat workspace/.agent_comm/agents.json | jq '.'
```

---

## 📋 **Best Practices**

### **✅ Regular Maintenance**
- Run `cleanup` weekly to remove inactive agents
- Check `agents` status before starting major tasks
- Use `restart` instead of `kill` when possible for better continuity

### **✅ Fault Recovery**  
- Always check `status` before killing agents
- Use `restart` for temporary issues  
- Use `kill` + `spawn` for persistent problems
- Run `cleanup` after major agent changes

### **✅ Dynamic Scaling**
- Spawn specialized agents for complex projects
- Use descriptive names for temporary agents
- Remove temporary agents when project is complete
- Monitor system resources with large agent teams

### **✅ Monitoring**
- Check `agents` regularly to see team health
- Use `status <agent>` for detailed health checks  
- Monitor `tasks` to see workload distribution
- Watch for agents with high pending task counts

---

## 🚨 **Troubleshooting**

### **Agent Won't Start**
```bash
# Check for name conflicts
agents | grep "desired_name"

# Try different name
spawn coder unique_coder_name

# Check system resources
ps aux | grep python | wc -l
```

### **Agent Not Responding**  
```bash
# Check if process exists
status stuck_agent

# Force restart if needed
kill stuck_agent
spawn role new_name
```

### **Tasks Not Processing**
```bash
# Check agent is active and healthy
status target_agent

# Check task queue  
tasks

# Restart agent if needed
restart target_agent
```

### **Registry Corruption**
```bash
# Clean and rebuild
./multi-agent clean
cleanup
python3 smart_launcher.py ai-development
```

---

## 🎉 **Summary**

Your multi-agent system now has **enterprise-grade lifecycle management**:

- ✅ **Real-time health monitoring** with process verification
- ✅ **Graceful fault recovery** with restart capabilities  
- ✅ **Dynamic agent scaling** for complex projects
- ✅ **Automatic cleanup** of inactive agents
- ✅ **Zero-downtime operations** - other agents continue working
- ✅ **Process management** with PID tracking and verification

**Use these commands to maintain a healthy, scalable agent ecosystem!** 🚀
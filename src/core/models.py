"""
Core data models for the Multi-Agent AI Terminal System
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional


class AgentRole(Enum):
    """Enumeration of available agent roles"""
    COORDINATOR = "coordinator"
    CODER = "coder" 
    CODE_REVIEWER = "code_reviewer"
    CODE_REWRITER = "code_rewriter"
    FILE_MANAGER = "file_manager"
    GIT_MANAGER = "git_manager"
    RESEARCHER = "researcher"
    TESTER = "tester"
    HELPER = "helper"


class TaskStatus(Enum):
    """Enumeration of task statuses"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BRIGHT_RED = '\033[1;91m'
    BRIGHT_GREEN = '\033[1;92m'
    BRIGHT_YELLOW = '\033[1;93m'
    BRIGHT_BLUE = '\033[1;94m'
    BRIGHT_MAGENTA = '\033[1;95m'
    BRIGHT_CYAN = '\033[1;96m'
    BRIGHT_WHITE = '\033[1;97m'
    ENDC = '\033[0m'
    RESET = '\033[0m'  # Alias for ENDC


@dataclass
class Task:
    """Data structure for agent tasks"""
    id: str
    type: str
    description: str
    assigned_to: str
    created_by: str
    status: TaskStatus
    priority: int
    data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "type": self.type,
            "description": self.description,
            "assigned_to": self.assigned_to,
            "created_by": self.created_by,
            "status": self.status.value,
            "priority": self.priority,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary"""
        return cls(
            id=data["id"],
            type=data["type"], 
            description=data["description"],
            assigned_to=data["assigned_to"],
            created_by=data["created_by"],
            status=TaskStatus(data["status"]),
            priority=data["priority"],
            data=data.get("data", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )


@dataclass
class AgentInfo:
    """Data structure for agent information"""
    id: str
    role: AgentRole
    status: str
    pid: int
    last_seen: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent info to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "role": self.role.value,
            "status": self.status,
            "pid": self.pid,
            "last_seen": self.last_seen.isoformat()
        }
    
    @classmethod 
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentInfo':
        """Create agent info from dictionary"""
        return cls(
            id=data["id"],
            role=AgentRole(data["role"]),
            status=data["status"], 
            pid=data["pid"],
            last_seen=datetime.fromisoformat(data["last_seen"])
        )


@dataclass
class ProjectInfo:
    """Data structure for project information"""
    name: str
    path: str
    framework: Optional[str] = None
    components: List[str] = None
    features: List[str] = None
    description: str = ""
    
    def __post_init__(self):
        if self.components is None:
            self.components = []
        if self.features is None:
            self.features = []
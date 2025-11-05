"""
Project Management - Handles project creation, analysis, and structure management
"""

import os
import json
from datetime import datetime
from typing import Dict, List

from ..core.models import Colors
from ..core.utils import colored_print


class ProjectManager:
    """Manages project creation, analysis, and structure operations"""
    
    def __init__(self, terminal_instance, comm_instance):
        self.terminal = terminal_instance
        self.comm = comm_instance
        self.workspace_dir = terminal_instance.workspace_dir
    
    def analyze_project_requirements(self, description: str, task_data: Dict = None) -> Dict:
        """Analyze project requirements from description and task data"""
        
        colored_print(f"   ANALYZING: Project requirements from description", Colors.CYAN)
        
        project_info = {
            "name": "UnknownProject",
            "type": "web",
            "framework": "react",
            "features": [],
            "structure": "standard"
        }
        
        desc_lower = description.lower()
        
        # Extract project name
        if task_data and 'project_name' in task_data:
            project_info["name"] = task_data['project_name']
        elif "todo" in desc_lower:
            project_info["name"] = "TodoApp"
        elif "time" in desc_lower or "clock" in desc_lower:
            project_info["name"] = "TimeApp"
        elif "weather" in desc_lower:
            project_info["name"] = "WeatherApp"
        elif "chat" in desc_lower:
            project_info["name"] = "ChatApp"
        
        # Detect framework
        if "react" in desc_lower:
            project_info["framework"] = "react"
        elif "vue" in desc_lower:
            project_info["framework"] = "vue"
        elif "angular" in desc_lower:
            project_info["framework"] = "angular"
        elif "python" in desc_lower:
            project_info["framework"] = "python"
            project_info["type"] = "backend"
        elif "node" in desc_lower:
            project_info["framework"] = "nodejs"
            project_info["type"] = "backend"
        
        # Extract features
        if "todo" in desc_lower or "task" in desc_lower:
            project_info["features"].extend(["task_management", "crud_operations", "local_storage"])
        if "time" in desc_lower:
            project_info["features"].extend(["time_display", "real_time_updates"])
        if "date" in desc_lower:
            project_info["features"].extend(["date_display", "calendar"])
        if "auth" in desc_lower or "login" in desc_lower:
            project_info["features"].extend(["authentication", "user_management"])
        if "api" in desc_lower:
            project_info["features"].extend(["api_integration", "data_fetching"])
        
        colored_print(f"      Project: {project_info['name']} ({project_info['framework']})", Colors.YELLOW)
        colored_print(f"      Features: {', '.join(project_info['features'])}", Colors.YELLOW)
        
        return project_info
    
    def create_project_structure(self, project_info: Dict) -> str:
        """Create project directory structure based on project info"""
        
        project_name = project_info.get("name", "UnknownProject")
        framework = project_info.get("framework", "react")
        
        colored_print(f"   CREATING: Project structure for '{project_name}'", Colors.BRIGHT_GREEN)
        
        project_path = os.path.join(self.workspace_dir, project_name)
        
        # Create base directory
        os.makedirs(project_path, exist_ok=True)
        
        # Create framework-specific structure
        if framework == "react":
            self._create_react_structure(project_path, project_info)
        elif framework == "vue":
            self._create_vue_structure(project_path, project_info)
        elif framework == "python":
            self._create_python_structure(project_path, project_info)
        elif framework == "nodejs":
            self._create_nodejs_structure(project_path, project_info)
        else:
            self._create_generic_structure(project_path, project_info)
        
        colored_print(f"   SUCCESS: Created project structure at {project_path}", Colors.GREEN)
        
        return project_path
    
    def _create_react_structure(self, project_path: str, project_info: Dict):
        """Create React project structure (AI-only content generation)."""
        
        # Create directories
        directories = [
            "src/components",
            "src/styles",
            "src/utils",
            "src/hooks",
            "public"
        ]
        for directory in directories:
            os.makedirs(os.path.join(project_path, directory), exist_ok=True)

        # AI-generate core files
        self._ai_write(project_path, "package.json", project_info)
        self._ai_write(project_path, "public/index.html", project_info)
        self._ai_write(project_path, "src/index.js", project_info)
        self._ai_write(project_path, "src/App.js", project_info)
        self._ai_write(project_path, "src/styles/App.css", project_info)
        self._ai_write(project_path, "src/styles/index.css", project_info)
    
    def _create_vue_structure(self, project_path: str, project_info: Dict):
        """Create Vue project structure (AI-only content generation)."""

        directories = [
            "src/components",
            "src/views",
            "src/assets",
            "src/router",
            "public"
        ]
        for directory in directories:
            os.makedirs(os.path.join(project_path, directory), exist_ok=True)

        # AI-generate core files
        self._ai_write(project_path, "package.json", project_info)
        self._ai_write(project_path, "public/index.html", project_info)
        self._ai_write(project_path, "src/main.js", project_info)
        self._ai_write(project_path, "src/App.vue", project_info)
    
    def _create_python_structure(self, project_path: str, project_info: Dict):
        """Create Python project structure (AI-only content generation)."""
        
        directories = [
            "src",
            "tests",
            "docs",
            "scripts"
        ]
        for directory in directories:
            os.makedirs(os.path.join(project_path, directory), exist_ok=True)

        # AI-generate typical files
        self._ai_write(project_path, "requirements.txt", project_info)
        self._ai_write(project_path, "setup.py", project_info)
        self._ai_write(project_path, "src/__init__.py", project_info)
    
    def _create_nodejs_structure(self, project_path: str, project_info: Dict):
        """Create Node.js project structure (AI-only content generation)."""
        
        directories = [
            "src",
            "routes",
            "models",
            "controllers",
            "middleware",
            "tests"
        ]
        for directory in directories:
            os.makedirs(os.path.join(project_path, directory), exist_ok=True)

        # AI-generate core files
        self._ai_write(project_path, "package.json", project_info)
        self._ai_write(project_path, "src/index.js", project_info)
    
    def _create_generic_structure(self, project_path: str, project_info: Dict):
        """Create generic project structure (AI-only content generation)."""
        
        directories = [
            "src",
            "assets",
            "docs",
            "tests"
        ]
        for directory in directories:
            os.makedirs(os.path.join(project_path, directory), exist_ok=True)

        # AI-generate README or other top-level files
        self._ai_write(project_path, "README.md", project_info)
    
        def _create_react_files(self, project_path: str, project_info: Dict):
                """Create basic React application files using AI-only content generation."""
                self._ai_write(project_path, "public/index.html", project_info)
                self._ai_write(project_path, "src/index.js", project_info)
                self._ai_write(project_path, "src/App.js", project_info)
                self._ai_write(project_path, "src/styles/App.css", project_info)
                self._ai_write(project_path, "src/styles/index.css", project_info)

        def _ai_write(self, project_path: str, rel_path: str, project_info: Dict):
                """Ask AI for content and write to rel_path under project_path if provided."""
                try:
                        # Use terminal's universal generator to avoid hard-coded content
                        content = self.terminal.generate_universal_file_content(rel_path, "", project_info)
                        abs_path = os.path.join(project_path, rel_path)
                        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                        if content:
                                with open(abs_path, 'w') as f:
                                        f.write(content)
                                colored_print(f"    AI-WROTE: {rel_path}", Colors.GREEN)
                        else:
                                colored_print(f"    SKIP: No AI content for {rel_path}", Colors.YELLOW)
                except Exception as e:
                        colored_print(f"    ERROR: AI write failed for {rel_path}: {e}", Colors.RED)
    
    def list_created_files(self, project_path: str) -> List[str]:
        """List all files created in the project"""
        
        created_files = []
        
        try:
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, project_path)
                    created_files.append(relative_path)
        except:
            pass
        
        return created_files
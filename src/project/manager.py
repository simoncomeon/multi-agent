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
        """Create React project structure"""
        
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
        
        # Create package.json
        package_json = {
            "name": project_info.get("name", "react-app").lower(),
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "browserslist": {
                "production": [">0.2%", "not dead", "not op_mini all"],
                "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
            }
        }
        
        with open(os.path.join(project_path, "package.json"), 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # Create basic React files
        self._create_react_files(project_path, project_info)
    
    def _create_vue_structure(self, project_path: str, project_info: Dict):
        """Create Vue project structure"""
        
        directories = [
            "src/components",
            "src/views",
            "src/assets",
            "src/router",
            "public"
        ]
        
        for directory in directories:
            os.makedirs(os.path.join(project_path, directory), exist_ok=True)
        
        # Create package.json for Vue
        package_json = {
            "name": project_info.get("name", "vue-app").lower(),
            "version": "0.1.0",
            "scripts": {
                "serve": "vue-cli-service serve",
                "build": "vue-cli-service build"
            },
            "dependencies": {
                "vue": "^3.0.0"
            },
            "devDependencies": {
                "@vue/cli-service": "~5.0.0"
            }
        }
        
        with open(os.path.join(project_path, "package.json"), 'w') as f:
            json.dump(package_json, f, indent=2)
    
    def _create_python_structure(self, project_path: str, project_info: Dict):
        """Create Python project structure"""
        
        directories = [
            "src",
            "tests",
            "docs",
            "scripts"
        ]
        
        for directory in directories:
            os.makedirs(os.path.join(project_path, directory), exist_ok=True)
        
        # Create requirements.txt
        requirements = [
            "flask>=2.0.0",
            "requests>=2.25.0",
            "pytest>=6.0.0"
        ]
        
        with open(os.path.join(project_path, "requirements.txt"), 'w') as f:
            f.write("\\n".join(requirements))
        
        # Create setup.py
        setup_content = f'''from setuptools import setup, find_packages

setup(
    name="{project_info.get('name', 'python-app').lower()}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.0",
        "requests>=2.25.0",
    ],
)'''
        
        with open(os.path.join(project_path, "setup.py"), 'w') as f:
            f.write(setup_content)
    
    def _create_nodejs_structure(self, project_path: str, project_info: Dict):
        """Create Node.js project structure"""
        
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
        
        # Create package.json for Node.js
        package_json = {
            "name": project_info.get("name", "node-app").lower(),
            "version": "1.0.0",
            "main": "src/index.js",
            "scripts": {
                "start": "node src/index.js",
                "dev": "nodemon src/index.js",
                "test": "jest"
            },
            "dependencies": {
                "express": "^4.18.0",
                "cors": "^2.8.5",
                "dotenv": "^16.0.0"
            },
            "devDependencies": {
                "nodemon": "^2.0.15",
                "jest": "^28.0.0"
            }
        }
        
        with open(os.path.join(project_path, "package.json"), 'w') as f:
            json.dump(package_json, f, indent=2)
    
    def _create_generic_structure(self, project_path: str, project_info: Dict):
        """Create generic project structure"""
        
        directories = [
            "src",
            "assets",
            "docs",
            "tests"
        ]
        
        for directory in directories:
            os.makedirs(os.path.join(project_path, directory), exist_ok=True)
        
        # Create README
        readme_content = f'''# {project_info.get('name', 'Project')}

## Description
{project_info.get('description', 'A new project created by Multi-Agent AI Terminal')}

## Features
{chr(10).join(f"- {feature}" for feature in project_info.get('features', []))}

## Getting Started

### Installation
1. Clone the repository
2. Install dependencies
3. Run the project

## Usage
Describe how to use your project here.

## Contributing
Guidelines for contributing to the project.

## License
MIT License
'''
        
        with open(os.path.join(project_path, "README.md"), 'w') as f:
            f.write(readme_content)
    
    def _create_react_files(self, project_path: str, project_info: Dict):
        """Create basic React application files"""
        
        # Create public/index.html
        index_html = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>''' + project_info.get('name', 'React App') + '''</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>'''
        
        with open(os.path.join(project_path, "public", "index.html"), 'w') as f:
            f.write(index_html)
        
        # Create src/index.js
        index_js = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);'''
        
        with open(os.path.join(project_path, "src", "index.js"), 'w') as f:
            f.write(index_js)
        
        # Create src/App.js
        app_js = '''import React from 'react';
import './styles/App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>''' + project_info.get('name', 'React App') + '''</h1>
        <p>Welcome to your new React application!</p>
      </header>
    </div>
  );
}

export default App;'''
        
        with open(os.path.join(project_path, "src", "App.js"), 'w') as f:
            f.write(app_js)
        
        # Create basic CSS files
        app_css = '''.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  min-height: 50vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.App-header h1 {
  margin-bottom: 20px;
}'''
        
        with open(os.path.join(project_path, "src", "styles", "App.css"), 'w') as f:
            f.write(app_css)
        
        # Create index.css
        index_css = '''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

* {
  box-sizing: border-box;
}'''
        
        with open(os.path.join(project_path, "src", "styles", "index.css"), 'w') as f:
            f.write(index_css)
    
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
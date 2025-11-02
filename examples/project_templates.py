#!/usr/bin/env python3
"""
Multi-Agent Project Templates

Example project structures that showcase multi-agent collaboration.
"""

import os
import json
from pathlib import Path

def create_web_app_project():
    """
    Example: Create a Flask web application using multi-agent coordination
    
    This demonstrates how different agents work together:
    - Coordinator: Orchestrates the project
    - File Manager: Creates project structure  
    - Coder: Generates application code
    - Git Manager: Handles version control
    - Researcher: Provides best practices
    """
    
    project_name = "flask_todo_app"
    base_dir = Path("workspace") / project_name
    
    # Project structure that File Manager would create
    structure = {
        "app/": {
            "__init__.py": "# Flask application factory",
            "models.py": "# Database models", 
            "routes.py": "# Application routes",
            "templates/": {
                "base.html": "<!-- Base template -->",
                "index.html": "<!-- Home page -->"
            },
            "static/": {
                "css/": {
                    "style.css": "/* Application styles */"
                },
                "js/": {
                    "app.js": "// Application JavaScript"
                }
            }
        },
        "tests/": {
            "__init__.py": "",
            "test_models.py": "# Model tests",
            "test_routes.py": "# Route tests"
        },
        "requirements.txt": "Flask==2.3.3\\nFlask-SQLAlchemy==3.0.5",
        "config.py": "# Configuration settings",
        "app.py": "# Application entry point",
        "README.md": "# Flask TODO Application",
        ".gitignore": "*.pyc\\n__pycache__/\\n.env"
    }
    
    print(f"Creating project structure: {project_name}")
    create_structure(base_dir, structure)
    
    # Task examples that Coordinator would delegate
    tasks = [
        {
            "agent": "file_manager",
            "task": f"create_project_structure",
            "description": f"Create {project_name} directory structure with Flask best practices"
        },
        {
            "agent": "coder", 
            "task": "generate_flask_app",
            "description": "Generate Flask application code with TODO functionality"
        },
        {
            "agent": "researcher",
            "task": "flask_best_practices", 
            "description": "Research Flask security and performance best practices"
        },
        {
            "agent": "git_manager",
            "task": "initialize_repo",
            "description": "Initialize git repository with proper .gitignore"
        }
    ]
    
    print("\n-- Multi-Agent Task Distribution:")
    for task in tasks:
        print(f"  → {task['agent']}: {task['description']}")
    
    return project_name

def create_data_analysis_project():
    """
    Example: Data analysis project with Jupyter notebooks
    """
    
    project_name = "data_analysis_project"
    base_dir = Path("workspace") / project_name
    
    structure = {
        "data/": {
            "raw/": {"README.md": "# Raw data files"},
            "processed/": {"README.md": "# Processed data"},
            "external/": {"README.md": "# External datasets"}
        },
        "notebooks/": {
            "01_data_exploration.ipynb": "# Data exploration notebook",
            "02_data_cleaning.ipynb": "# Data cleaning notebook", 
            "03_analysis.ipynb": "# Main analysis notebook"
        },
        "src/": {
            "__init__.py": "",
            "data_processing.py": "# Data processing utilities",
            "visualization.py": "# Visualization functions",
            "analysis.py": "# Analysis functions"
        },
        "reports/": {
            "figures/": {"README.md": "# Generated figures"},
            "final_report.md": "# Final analysis report"
        },
        "requirements.txt": "pandas==2.0.3\\nnumpy==1.24.3\\nmatplotlib==3.7.2\\njupyter==1.0.0",
        "README.md": "# Data Analysis Project",
        ".gitignore": "*.pyc\\n__pycache__/\\n.ipynb_checkpoints/\\ndata/raw/*"
    }
    
    print(f"-- Creating data analysis project: {project_name}")
    create_structure(base_dir, structure)
    
    return project_name

def create_structure(base_path, structure):
    """Recursively create directory structure"""
    base_path = Path(base_path)
    base_path.mkdir(parents=True, exist_ok=True)
    
    for name, content in structure.items():
        path = base_path / name
        
        if isinstance(content, dict):
            # It's a directory
            path.mkdir(exist_ok=True)
            create_structure(path, content)
        else:
            # It's a file
            path.write_text(content)
            print(f"  -- Created: {path}")

def demo_coordination_workflow():
    """
    Demonstrate how agents would coordinate on a real project
    """
    
    print("-- Multi-Agent Coordination Workflow Demo")
    print("=" * 50)
    
    workflow = [
        {
            "phase": "1. Project Initialization",
            "coordinator_action": "Analyze project requirements",
            "delegations": [
                "delegate 'create Flask project structure' to file_manager",
                "delegate 'research Flask security best practices' to researcher"
            ]
        },
        {
            "phase": "2. Core Development", 
            "coordinator_action": "Coordinate development tasks",
            "delegations": [
                "delegate 'generate Flask app with TODO functionality' to coder",
                "delegate 'create database models for TODO items' to coder",
                "delegate 'organize static files and templates' to file_manager"
            ]
        },
        {
            "phase": "3. Testing & Documentation",
            "coordinator_action": "Ensure quality and documentation",
            "delegations": [
                "delegate 'analyze code for bugs and security issues' to coder", 
                "delegate 'create comprehensive README with setup instructions' to file_manager",
                "delegate 'research deployment best practices' to researcher"
            ]
        },
        {
            "phase": "4. Version Control & Deployment",
            "coordinator_action": "Finalize project",
            "delegations": [
                "delegate 'initialize git repo with proper .gitignore' to git_manager",
                "delegate 'commit all files with descriptive messages' to git_manager",
                "delegate 'create deployment documentation' to file_manager"
            ]
        }
    ]
    
    for step in workflow:
        print(f"\n{step['phase']}")
        print(f"Coordinator: {step['coordinator_action']}")
        print("Delegated tasks:")
        for delegation in step['delegations']:
            print(f"  • {delegation}")

if __name__ == "__main__":
    print("-- Multi-Agent Project Examples")
    print("=" * 35)
    print()
    
    # Create example projects
    web_project = create_web_app_project()
    print()
    data_project = create_data_analysis_project()
    print()
    
    # Show coordination workflow
    demo_coordination_workflow()
    
    print(f"\n-- Example projects created in workspace/")
    print(f"   • {web_project}/")
    print(f"   • {data_project}/")
    print()
    print("-- To see these projects in action:")
    print("   1. Start multiple agents: ./multi-agent start coordinator")
    print("   2. Use delegation commands shown above")
    print("   3. Watch agents collaborate to build the projects!")
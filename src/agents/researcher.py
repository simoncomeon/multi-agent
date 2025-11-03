"""
Research Agent - Handles research and information gathering tasks
"""

import requests
import json
from datetime import datetime
from typing import Dict, List

from ..core.models import Colors
from ..core.utils import colored_print


class ResearchAgent:
    """Specialized agent for research and information gathering"""
    
    def __init__(self, terminal_instance, comm_instance):
        self.terminal = terminal_instance
        self.comm = comm_instance
        self.agent_id = "researcher"
    
    def handle_research_task(self, task: Dict) -> Dict:
        """Handle research tasks"""
        
        description = task["description"]
        colored_print(f"RESEARCHER: Processing research task", Colors.BRIGHT_CYAN)
        colored_print(f"   Task: {description}", Colors.CYAN)
        
        # Analyze research type
        research_type = self.analyze_research_type(description)
        
        if research_type == "framework":
            return self.research_framework(description)
        elif research_type == "library":
            return self.research_library(description)
        elif research_type == "documentation":
            return self.research_documentation(description)
        elif research_type == "best_practices":
            return self.research_best_practices(description)
        elif research_type == "solution":
            return self.research_solution(description)
        else:
            return self.general_research(description)
    
    def analyze_research_type(self, description: str) -> str:
        """Analyze what type of research is needed"""
        
        desc_lower = description.lower()
        
        if any(framework in desc_lower for framework in ["react", "vue", "angular", "django", "flask", "express"]):
            return "framework"
        elif any(keyword in desc_lower for keyword in ["library", "package", "npm", "pip", "dependency"]):
            return "library"
        elif any(keyword in desc_lower for keyword in ["documentation", "docs", "api", "reference"]):
            return "documentation"
        elif any(keyword in desc_lower for keyword in ["best practice", "pattern", "convention", "standard"]):
            return "best_practices"
        elif any(keyword in desc_lower for keyword in ["solution", "how to", "implement", "example"]):
            return "solution"
        else:
            return "general"
    
    def research_framework(self, description: str) -> Dict:
        """Research framework-specific information"""
        
        desc_lower = description.lower()
        framework_info = {}
        
        if "react" in desc_lower:
            framework_info = self.get_react_info()
        elif "vue" in desc_lower:
            framework_info = self.get_vue_info()
        elif "angular" in desc_lower:
            framework_info = self.get_angular_info()
        elif "python" in desc_lower:
            framework_info = self.get_python_info()
        elif "node" in desc_lower or "express" in desc_lower:
            framework_info = self.get_nodejs_info()
        
        colored_print(f"   RESEARCH: Framework analysis completed", Colors.GREEN)
        
        return {
            "status": "success",
            "research_type": "framework",
            "framework_info": framework_info,
            "message": f"Framework research completed for: {description}",
            "recommendations": framework_info.get("recommendations", [])
        }
    
    def get_react_info(self) -> Dict:
        """Get React framework information"""
        
        return {
            "name": "React",
            "version": "18.x (Latest)",
            "description": "A JavaScript library for building user interfaces",
            "key_features": [
                "Component-based architecture",
                "Virtual DOM for performance",
                "Hooks for state management",
                "JSX syntax extension",
                "Large ecosystem"
            ],
            "use_cases": [
                "Single Page Applications (SPAs)",
                "Progressive Web Apps (PWAs)",
                "Mobile apps with React Native",
                "Server-side rendering with Next.js"
            ],
            "getting_started": {
                "installation": "npx create-react-app my-app",
                "dev_server": "npm start",
                "build": "npm run build"
            },
            "recommendations": [
                "Use functional components with hooks",
                "Implement proper state management (Context API or Redux)",
                "Follow React best practices and patterns",
                "Use TypeScript for larger projects",
                "Implement proper error boundaries"
            ],
            "common_packages": [
                "react-router-dom (routing)",
                "styled-components (CSS-in-JS)", 
                "axios (HTTP client)",
                "react-query (data fetching)",
                "formik (form handling)"
            ]
        }
    
    def get_vue_info(self) -> Dict:
        """Get Vue framework information"""
        
        return {
            "name": "Vue.js",
            "version": "3.x (Latest)",
            "description": "The Progressive JavaScript Framework",
            "key_features": [
                "Progressive framework",
                "Component-based architecture", 
                "Reactive data binding",
                "Template syntax",
                "Composition API"
            ],
            "use_cases": [
                "Single Page Applications",
                "Progressive Web Apps",
                "Desktop apps with Electron",
                "Mobile apps with Quasar or NativeScript"
            ],
            "getting_started": {
                "installation": "npm create vue@latest my-project",
                "dev_server": "npm run dev",
                "build": "npm run build"
            },
            "recommendations": [
                "Use Composition API for modern Vue development",
                "Implement proper component structure",
                "Use Vue Router for navigation",
                "Consider Pinia for state management",
                "Follow Vue style guide"
            ],
            "common_packages": [
                "vue-router (routing)",
                "pinia (state management)",
                "axios (HTTP client)",
                "vuetify (UI framework)",
                "vee-validate (form validation)"
            ]
        }
    
    def get_angular_info(self) -> Dict:
        """Get Angular framework information"""
        
        return {
            "name": "Angular",
            "version": "17.x (Latest)",
            "description": "Platform for building mobile and desktop web applications",
            "key_features": [
                "Full framework with CLI",
                "TypeScript by default",
                "Dependency injection",
                "Component-based architecture",
                "Powerful CLI tools"
            ],
            "use_cases": [
                "Enterprise applications",
                "Large-scale SPAs",
                "Progressive Web Apps",
                "Mobile apps with Ionic"
            ],
            "getting_started": {
                "installation": "npm install -g @angular/cli && ng new my-app",
                "dev_server": "ng serve",
                "build": "ng build"
            },
            "recommendations": [
                "Use Angular CLI for project scaffolding",
                "Implement lazy loading for better performance",
                "Use RxJS for reactive programming",
                "Follow Angular style guide",
                "Use Angular Material for UI components"
            ]
        }
    
    def get_python_info(self) -> Dict:
        """Get Python framework information"""
        
        return {
            "name": "Python",
            "version": "3.11+ (Recommended)",
            "description": "High-level programming language for web development",
            "frameworks": {
                "web": ["Django", "Flask", "FastAPI", "Pyramid"],
                "data_science": ["Pandas", "NumPy", "Matplotlib", "Jupyter"],
                "machine_learning": ["TensorFlow", "PyTorch", "Scikit-learn"]
            },
            "getting_started": {
                "virtual_env": "python -m venv venv && source venv/bin/activate",
                "django": "pip install django && django-admin startproject mysite",
                "flask": "pip install flask"
            },
            "recommendations": [
                "Use virtual environments",
                "Follow PEP 8 style guidelines",
                "Use type hints for better code quality",
                "Implement proper error handling",
                "Write comprehensive tests"
            ]
        }
    
    def get_nodejs_info(self) -> Dict:
        """Get Node.js framework information"""
        
        return {
            "name": "Node.js",
            "version": "18.x LTS (Recommended)",
            "description": "JavaScript runtime for server-side development",
            "frameworks": [
                "Express.js (minimal web framework)",
                "Koa.js (next-generation web framework)",
                "NestJS (enterprise-grade framework)",
                "Fastify (fast and efficient)"
            ],
            "getting_started": {
                "installation": "npm init -y && npm install express",
                "basic_server": "Create app.js with Express setup",
                "dev_server": "node app.js or nodemon app.js"
            },
            "recommendations": [
                "Use Express.js for web applications",
                "Implement proper middleware",
                "Use environment variables",
                "Follow REST API best practices",
                "Implement proper error handling"
            ]
        }
    
    def research_library(self, description: str) -> Dict:
        """Research library or package information"""
        
        colored_print(f"   RESEARCH: Analyzing library requirements", Colors.YELLOW)
        
        # Extract library name from description
        library_name = self.extract_library_name(description)
        
        if library_name:
            library_info = self.get_library_info(library_name)
        else:
            library_info = self.suggest_libraries_for_task(description)
        
        return {
            "status": "success",
            "research_type": "library",
            "library_info": library_info,
            "message": f"Library research completed: {library_name or 'task-based suggestions'}",
            "installation": library_info.get("installation", "N/A")
        }
    
    def extract_library_name(self, description: str) -> str:
        """Extract library name from research description"""
        
        import re
        
        # Look for common patterns
        patterns = [
            r'library\\s+([\\w-]+)',
            r'package\\s+([\\w-]+)', 
            r'npm\\s+([\\w-]+)',
            r'pip\\s+([\\w-]+)',
            r'([\\w-]+)\\s+library',
            r'([\\w-]+)\\s+package'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def get_library_info(self, library_name: str) -> Dict:
        """Get information about a specific library"""
        
        # Simulated library database - in real implementation, this would query npm/pip APIs
        library_db = {
            "axios": {
                "description": "Promise-based HTTP client for JavaScript",
                "installation": "npm install axios",
                "usage": "HTTP requests in web applications",
                "alternatives": ["fetch", "request", "superagent"]
            },
            "lodash": {
                "description": "Utility library for JavaScript",
                "installation": "npm install lodash",
                "usage": "Data manipulation and utility functions",
                "alternatives": ["ramda", "underscore"]
            },
            "express": {
                "description": "Fast, minimal web framework for Node.js",
                "installation": "npm install express",
                "usage": "Building web servers and APIs",
                "alternatives": ["koa", "fastify", "hapi"]
            },
            "react-router": {
                "description": "Routing library for React applications",
                "installation": "npm install react-router-dom",
                "usage": "Client-side routing in React apps",
                "alternatives": ["reach-router", "wouter"]
            }
        }
        
        return library_db.get(library_name.lower(), {
            "description": f"Library information for {library_name} not found in database",
            "installation": f"Check package manager for {library_name}",
            "suggestion": "Research specific library documentation"
        })
    
    def research_best_practices(self, description: str) -> Dict:
        """Research best practices for a technology or pattern"""
        
        colored_print(f"   RESEARCH: Gathering best practices", Colors.YELLOW)
        
        practices = self.get_best_practices_for_topic(description)
        
        return {
            "status": "success",
            "research_type": "best_practices",
            "practices": practices,
            "message": f"Best practices research completed for: {description}"
        }
    
    def get_best_practices_for_topic(self, description: str) -> Dict:
        """Get best practices for a specific topic"""
        
        desc_lower = description.lower()
        
        if "react" in desc_lower:
            return {
                "topic": "React Best Practices",
                "practices": [
                    "Use functional components with hooks",
                    "Keep components small and focused",
                    "Use proper prop types or TypeScript",
                    "Implement error boundaries",
                    "Optimize performance with React.memo",
                    "Use proper state management patterns",
                    "Follow consistent naming conventions"
                ]
            }
        elif "api" in desc_lower or "rest" in desc_lower:
            return {
                "topic": "REST API Best Practices",
                "practices": [
                    "Use proper HTTP methods (GET, POST, PUT, DELETE)",
                    "Implement consistent URL structure",
                    "Use appropriate status codes",
                    "Version your APIs",
                    "Implement proper error handling",
                    "Use authentication and authorization",
                    "Document your API endpoints"
                ]
            }
        elif "security" in desc_lower:
            return {
                "topic": "Web Security Best Practices",
                "practices": [
                    "Validate and sanitize all inputs",
                    "Use HTTPS for all communications",
                    "Implement proper authentication",
                    "Use CSRF protection",
                    "Sanitize outputs to prevent XSS",
                    "Keep dependencies updated",
                    "Implement rate limiting"
                ]
            }
        else:
            return {
                "topic": "General Development Best Practices",
                "practices": [
                    "Write clean, readable code",
                    "Use meaningful variable names",
                    "Implement proper error handling",
                    "Write comprehensive tests",
                    "Follow DRY principles",
                    "Use version control effectively",
                    "Document your code"
                ]
            }
    
    def general_research(self, description: str) -> Dict:
        """Handle general research tasks"""
        
        colored_print(f"   RESEARCH: Processing general research request", Colors.YELLOW)
        
        return {
            "status": "success",
            "research_type": "general",
            "message": f"General research completed: {description}",
            "findings": f"Research findings for: {description}",
            "recommendations": [
                "Consult official documentation",
                "Review community best practices", 
                "Check recent tutorials and guides",
                "Explore relevant examples and case studies"
            ]
        }
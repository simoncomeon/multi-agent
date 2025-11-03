"""
Core utility functions for the Multi-Agent AI Terminal System
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from .models import Colors


def colored_print(text: str, color: str) -> None:
    """Print colored text to terminal"""
    print(f"{color}{text}{Colors.ENDC}")


def colored_text(text: str, color: str) -> str:
    """Return colored text string"""
    return f"{color}{text}{Colors.ENDC}"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def validate_agent_name(name: str) -> bool:
    """Validate agent name format"""
    if not name or len(name) < 2:
        return False
    
    # Check for valid characters (alphanumeric, underscore, hyphen)
    allowed_chars = set('abcdefghijklmnopqrstuvwxyz0123456789_-')
    return all(c.lower() in allowed_chars for c in name)


def validate_project_name(name: str) -> bool:
    """Validate project name format"""
    if not name or len(name) < 2:
        return False
    
    # More restrictive for project names (no spaces, special chars)
    allowed_chars = set('abcdefghijklmnopqrstuvwxyz0123456789_-')
    return all(c.lower() in allowed_chars for c in name)


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis if too long"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def format_timestamp(timestamp: str) -> str:
    """Format ISO timestamp for display"""
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp


def safe_filename(filename: str) -> str:
    """Convert string to safe filename"""
    import re
    # Remove or replace unsafe characters
    safe_name = re.sub(r'[^\w\-_\.]', '_', filename)
    return safe_name[:100]  # Limit length


def gather_file_context(file_path: Union[str, Path], max_size: int = 50000) -> Dict:
    """Gather file context for AI input"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        return {
            "error": f"File not found: {file_path}",
            "exists": False
        }
    
    try:
        # Check if it's a text file and reasonable size
        stat = file_path.stat()
        
        if stat.st_size > max_size:
            return {
                "path": str(file_path),
                "size": stat.st_size,
                "size_formatted": format_file_size(stat.st_size),
                "error": f"File too large ({format_file_size(stat.st_size)}), max {format_file_size(max_size)}",
                "exists": True
            }
        
        # Try to read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "path": str(file_path),
            "name": file_path.name,
            "extension": file_path.suffix,
            "size": stat.st_size,
            "size_formatted": format_file_size(stat.st_size),
            "content": content,
            "lines": len(content.splitlines()),
            "exists": True,
            "readable": True
        }
        
    except UnicodeDecodeError:
        return {
            "path": str(file_path),
            "name": file_path.name,
            "extension": file_path.suffix,
            "size": stat.st_size,
            "size_formatted": format_file_size(stat.st_size),
            "error": "Binary file - content not readable as text",
            "exists": True,
            "readable": False
        }
    except Exception as e:
        return {
            "path": str(file_path),
            "error": f"Error reading file: {e}",
            "exists": True,
            "readable": False
        }


def gather_directory_context(dir_path: Union[str, Path], max_files: int = 20, max_depth: int = 3) -> Dict:
    """Gather directory context for AI input"""
    dir_path = Path(dir_path)
    
    if not dir_path.exists():
        return {
            "error": f"Directory not found: {dir_path}",
            "exists": False
        }
    
    if not dir_path.is_dir():
        return {
            "error": f"Path is not a directory: {dir_path}",
            "exists": True,
            "is_directory": False
        }
    
    try:
        # Gather directory structure
        structure = []
        file_contents = {}
        file_count = 0
        
        def scan_directory(current_path: Path, current_depth: int = 0):
            nonlocal file_count
            
            if current_depth > max_depth or file_count >= max_files:
                return
            
            items = []
            try:
                for item in sorted(current_path.iterdir()):
                    # Skip hidden files and common ignore patterns
                    if item.name.startswith('.') or item.name in ['node_modules', '__pycache__', 'dist', 'build']:
                        continue
                    
                    if item.is_file():
                        file_count += 1
                        if file_count <= max_files:
                            # Include file info
                            file_info = {
                                "name": item.name,
                                "path": str(item.relative_to(dir_path)),
                                "size": item.stat().st_size,
                                "size_formatted": format_file_size(item.stat().st_size)
                            }
                            
                            # Try to include content for small text files
                            if item.suffix in ['.js', '.py', '.ts', '.tsx', '.jsx', '.json', '.md', '.txt', '.yml', '.yaml', '.css', '.html']:
                                if item.stat().st_size < 10000:  # Only small files
                                    try:
                                        with open(item, 'r', encoding='utf-8') as f:
                                            file_info["content"] = f.read()
                                    except:
                                        file_info["content_error"] = "Could not read file content"
                            
                            items.append(file_info)
                        
                    elif item.is_dir() and current_depth < max_depth:
                        # Recurse into subdirectory
                        subdir_info = {
                            "name": item.name,
                            "path": str(item.relative_to(dir_path)),
                            "type": "directory",
                            "contents": []
                        }
                        items.append(subdir_info)
                        scan_directory(item, current_depth + 1)
                
            except PermissionError:
                items.append({"error": f"Permission denied accessing {current_path}"})
            
            return items
        
        structure = scan_directory(dir_path)
        
        return {
            "path": str(dir_path),
            "name": dir_path.name,
            "exists": True,
            "is_directory": True,
            "structure": structure,
            "file_count": file_count,
            "max_files_reached": file_count >= max_files,
            "max_depth": max_depth
        }
        
    except Exception as e:
        return {
            "path": str(dir_path),
            "error": f"Error scanning directory: {e}",
            "exists": True,
            "is_directory": True
        }


def gather_project_context(project_path: Union[str, Path], include_files: List[str] = None) -> Dict:
    """Gather comprehensive project context for AI input"""
    project_path = Path(project_path)
    
    context = {
        "project_path": str(project_path),
        "project_name": project_path.name,
        "directory_context": gather_directory_context(project_path),
        "key_files": {},
        "package_info": {},
        "project_type": "unknown"
    }
    
    # Try to identify project type and gather key files
    key_files_to_check = [
        "package.json",      # Node.js/React
        "requirements.txt",  # Python
        "Pipfile",          # Python Pipenv
        "setup.py",         # Python setup
        "README.md",        # Documentation
        "README.txt",       # Documentation
        ".gitignore",       # Git
        "tsconfig.json",    # TypeScript
        "Cargo.toml",       # Rust
        "go.mod",           # Go
        "pom.xml",          # Java Maven
        "build.gradle"      # Java Gradle
    ]
    
    # Add user-specified files
    if include_files:
        key_files_to_check.extend(include_files)
    
    # Gather key files
    for filename in key_files_to_check:
        file_path = project_path / filename
        if file_path.exists():
            file_context = gather_file_context(file_path)
            if file_context.get("readable"):
                context["key_files"][filename] = file_context
    
    # Determine project type based on key files
    if "package.json" in context["key_files"]:
        context["project_type"] = "javascript/node"
        try:
            import json
            package_data = json.loads(context["key_files"]["package.json"]["content"])
            context["package_info"] = {
                "name": package_data.get("name"),
                "version": package_data.get("version"),
                "dependencies": list(package_data.get("dependencies", {}).keys()),
                "scripts": list(package_data.get("scripts", {}).keys()),
                "framework": "react" if "react" in package_data.get("dependencies", {}) else "node"
            }
        except:
            pass
    
    elif any(f in context["key_files"] for f in ["requirements.txt", "setup.py", "Pipfile"]):
        context["project_type"] = "python"
        if "requirements.txt" in context["key_files"]:
            requirements = context["key_files"]["requirements.txt"]["content"].splitlines()
            context["package_info"]["dependencies"] = [req.strip() for req in requirements if req.strip()]
    
    elif "tsconfig.json" in context["key_files"]:
        context["project_type"] = "typescript"
    
    return context
    safe = re.sub(r'[<>:"/\\|?*]', '_', filename)
    safe = re.sub(r'\s+', '_', safe)  # Replace spaces with underscores
    return safe.strip('._')  # Remove leading/trailing dots and underscores
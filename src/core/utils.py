"""
Core utility functions for the Multi-Agent AI Terminal System
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

from .models import Colors


def colored_print(text: str, color: str) -> None:
    """Print colored text to terminal"""
    print(f"{color}{text}{Colors.ENDC}")


def colored_text(text: str, color: str) -> str:
    """Return colored text string"""
    return f"{color}{text}{Colors.ENDC}"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0 or unit == "TB":
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def validate_agent_name(name: str) -> bool:
    """Validate agent name format"""
    if not name or len(name) < 2:
        return False
    return bool(re.match(r"^[a-zA-Z0-9_-]+$", name))


def validate_file_path(path: str) -> bool:
    """Validate file path format"""
    if not path or len(path) < 2:
        return False
    try:
        Path(path)
        return True
    except (ValueError, OSError):
        return False


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def format_timestamp(timestamp: str) -> str:
    """Format ISO timestamp to readable format"""
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return timestamp


def safe_filename(filename: str) -> str:
    """Convert string to safe filename"""
    safe_name = re.sub(r"[^\w\-_\.]", "_", filename)
    return safe_name[:100]


def gather_file_context(
    file_path: Union[str, Path], max_size: int = 50000
) -> Dict[str, Union[str, int, bool, Dict, List]]:
    """Gather comprehensive context about a file"""
    file_path = Path(file_path)

    if not file_path.exists():
        return {
            "path": str(file_path),
            "exists": False,
            "error": "File does not exist",
        }

    try:
        stat = file_path.stat()

        context: Dict[str, Union[str, int, bool, Dict, List]] = {
            "path": str(file_path),
            "exists": True,
            "size": stat.st_size,
            "size_formatted": format_file_size(stat.st_size),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": file_path.suffix.lower(),
            "readable": False,
        }

        # Try to read file content if it's not too large
        if stat.st_size <= max_size:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                context["content"] = content
                context["readable"] = True
                context["lines"] = len(content.splitlines())
                context["characters"] = len(content)

                # Detect file type characteristics
                suffix = file_path.suffix.lower()
                if suffix == ".py":
                    context["file_type"] = "python"
                    context["imports"] = _extract_python_imports(content)
                elif suffix in [".js", ".ts", ".jsx", ".tsx"]:
                    context["file_type"] = "javascript"
                    context["imports"] = _extract_js_imports(content)
                elif suffix == ".json":
                    context["file_type"] = "json"
                    try:
                        json.loads(content)
                        context["valid_json"] = True
                    except json.JSONDecodeError:
                        context["valid_json"] = False

            except UnicodeDecodeError:
                context["readable"] = False
                context["binary"] = True
            except PermissionError:
                context["error"] = "Permission denied"
            except Exception as e:
                context["error"] = f"Error reading file: {str(e)}"
        else:
            context["too_large"] = True
            context["size_limit"] = max_size

        return context
    except Exception as e:
        return {
            "path": str(file_path),
            "exists": file_path.exists(),
            "error": f"Error accessing file: {str(e)}",
        }


def gather_directory_context(dir_path: Union[str, Path]) -> Dict[str, Union[str, int, List, bool, Dict]]:
    """Gather comprehensive context about a directory"""
    dir_path = Path(dir_path)

    if not dir_path.exists():
        return {
            "path": str(dir_path),
            "exists": False,
            "error": "Directory does not exist",
        }

    if not dir_path.is_dir():
        return {
            "path": str(dir_path),
            "exists": True,
            "is_directory": False,
            "error": "Path is not a directory",
        }

    try:
        file_count = 0

        def _scan_directory(
            current_path: Path,
            current_depth: int = 0,
            max_depth: int = 3,
            max_files: int = 100,
        ) -> List[Dict[str, Any]]:
            nonlocal file_count

            if current_depth > max_depth or file_count >= max_files:
                return []

            items: List[Dict[str, Any]] = []
            try:
                for item in sorted(current_path.iterdir()):
                    # Skip hidden files and common excludes
                    if item.name.startswith(".") or item.name in [
                        "__pycache__",
                        "node_modules",
                        ".git",
                        ".vscode",
                        "venv",
                        ".env",
                    ]:
                        continue

                    if item.is_file():
                        file_count += 1
                        if file_count > max_files:
                            break

                        file_info: Dict[str, Any] = {
                            "name": item.name,
                            "type": "file",
                            "size": item.stat().st_size,
                            "size_formatted": format_file_size(item.stat().st_size),
                            "extension": item.suffix.lower(),
                            "path": str(item.relative_to(dir_path)),
                        }

                        # Add content preview for small text files
                        if item.suffix.lower() in [
                            ".py",
                            ".js",
                            ".ts",
                            ".json",
                            ".md",
                            ".txt",
                            ".yml",
                            ".yaml",
                        ]:
                            if item.stat().st_size < 10000:  # Only small files
                                try:
                                    with open(item, "r", encoding="utf-8") as f:
                                        file_info["content"] = f.read()
                                except Exception:
                                    file_info["content"] = None

                        items.append(file_info)

                    elif item.is_dir() and current_depth < max_depth:
                        dir_info: Dict[str, Any] = {
                            "name": item.name,
                            "type": "directory",
                            "path": str(item.relative_to(dir_path)),
                            "children": [],
                        }

                        # Recursively scan subdirectory
                        subdir_items = _scan_directory(
                            item, current_depth + 1, max_depth, max_files
                        )
                        if subdir_items:
                            dir_info["children"] = subdir_items

                        items.append(dir_info)
            except PermissionError:
                items.append(
                    {
                        "error": f"Permission denied accessing {current_path}",
                        "type": "error",
                    }
                )

            return items

        structure = _scan_directory(dir_path)

        return {
            "path": str(dir_path),
            "exists": True,
            "is_directory": True,
            "file_count": file_count,
            "structure": structure,
            "size_info": _calculate_directory_size(dir_path),
        }
    except Exception as e:
        return {
            "path": str(dir_path),
            "exists": dir_path.exists(),
            "error": f"Error scanning directory: {str(e)}",
        }


def gather_project_context(project_path: Union[str, Path]) -> Dict[str, Union[str, Dict, List]]:
    """Gather project-level context and metadata"""
    project_path = Path(project_path)

    if not project_path.exists():
        return {
            "project_path": str(project_path),
            "exists": False,
            "error": "Project path does not exist",
        }

    context: Dict[str, Union[str, Dict, List, bool]] = {
        "project_path": str(project_path),
        "project_name": project_path.name,
        "exists": True,
    }

    # Detect project type and gather metadata
    project_type = _detect_project_type(project_path)
    context["project_type"] = project_type

    # Gather package information
    package_info = _gather_package_info(project_path, project_type)
    if package_info:
        context["package_info"] = package_info

    # Look for common configuration files
    config_files = _find_config_files(project_path)
    if config_files:
        context["config_files"] = config_files

    # Analyze project structure
    structure_analysis = _analyze_project_structure(project_path, project_type)
    context.update(structure_analysis)

    return context


def _extract_python_imports(content: str) -> List[str]:
    """Extract import statements from Python content"""
    imports: List[str] = []
    for line in content.splitlines():
        s = line.strip()
        if s.startswith("import ") or s.startswith("from "):
            imports.append(s)
    return imports


def _extract_js_imports(content: str) -> List[str]:
    """Extract import statements from JavaScript/TypeScript content"""
    imports: List[str] = []
    for line in content.splitlines():
        s = line.strip()
        if s.startswith("import ") or (s.startswith("const ") and "require(" in s):
            imports.append(s)
    return imports


def _calculate_directory_size(dir_path: Path) -> Dict[str, Union[int, str]]:
    """Calculate total size of directory"""
    total_size = 0
    file_count = 0

    try:
        for item in dir_path.rglob("*"):
            if item.is_file():
                file_count += 1
                total_size += item.stat().st_size
    except Exception:
        return {"error": "Could not calculate directory size"}

    return {
        "total_size": total_size,
        "total_size_formatted": format_file_size(total_size),
        "total_files": file_count,
    }


def _detect_project_type(project_path: Path) -> str:
    """Detect the type of project based on files present"""
    if (project_path / "package.json").exists():
        return "javascript/node"
    if (project_path / "requirements.txt").exists() or (project_path / "setup.py").exists():
        return "python"
    if (project_path / "pyproject.toml").exists():
        return "python"
    if (project_path / "Cargo.toml").exists():
        return "rust"
    if (project_path / "pom.xml").exists():
        return "java/maven"
    if (project_path / "build.gradle").exists():
        return "java/gradle"
    if (project_path / "composer.json").exists():
        return "php"
    return "unknown"


def _gather_package_info(project_path: Path, project_type: str) -> Optional[Dict]:
    """Gather package/dependency information"""
    try:
        if project_type == "javascript/node":
            package_json = project_path / "package.json"
            if package_json.exists():
                with open(package_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return {
                    "name": data.get("name", ""),
                    "version": data.get("version", ""),
                    "dependencies": list(data.get("dependencies", {}).keys()),
                    "devDependencies": list(data.get("devDependencies", {}).keys()),
                }
        elif project_type == "python":
            # Try requirements.txt first
            requirements_txt = project_path / "requirements.txt"
            if requirements_txt.exists():
                with open(requirements_txt, "r", encoding="utf-8") as f:
                    deps = [
                        line.split("==")[0].split(">=")[0].strip()
                        for line in f.readlines()
                        if line.strip() and not line.startswith("#")
                    ]
                return {
                    "dependencies": deps,
                    "source": "requirements.txt",
                }

            # Try pyproject.toml (without parsing to avoid extra deps)
            pyproject_toml = project_path / "pyproject.toml"
            if pyproject_toml.exists():
                return {"source": "pyproject.toml", "dependencies": []}
    except Exception:
        pass

    return None


def _find_config_files(project_path: Path) -> List[str]:
    """Find common configuration files in project"""
    config_patterns = [
        ".env",
        ".env.example",
        "config.json",
        "config.yml",
        "config.yaml",
        ".gitignore",
        "README.md",
        "LICENSE",
        "Dockerfile",
        "docker-compose.yml",
        ".eslintrc.js",
        ".eslintrc.json",
        "tsconfig.json",
        "webpack.config.js",
        "babel.config.js",
        ".babelrc",
        "jest.config.js",
        ".prettierrc",
    ]

    found_configs: List[str] = []
    for pattern in config_patterns:
        config_file = project_path / pattern
        if config_file.exists():
            found_configs.append(pattern)

    return found_configs


def _analyze_project_structure(project_path: Path, project_type: str) -> Dict[str, Union[List, bool]]:
    """Analyze project structure for common patterns"""
    analysis: Dict[str, Union[List, bool]] = {}

    # Common directory patterns
    common_dirs = [
        "src",
        "lib",
        "app",
        "components",
        "utils",
        "tests",
        "test",
        "docs",
        "public",
        "static",
    ]
    found_dirs: List[str] = []

    for dir_name in common_dirs:
        if (project_path / dir_name).is_dir():
            found_dirs.append(dir_name)

    analysis["common_directories"] = found_dirs

    # Check for testing setup
    has_tests = any(
        (project_path / test_dir).exists() for test_dir in ["tests", "test", "__tests__"]
    )
    analysis["has_tests"] = has_tests

    # Check for documentation
    has_docs = any(
        (project_path / doc_file).exists() for doc_file in ["README.md", "README.rst", "docs"]
    )
    analysis["has_documentation"] = has_docs

    # Type-specific analysis
    if project_type == "javascript/node":
        analysis["has_typescript"] = (project_path / "tsconfig.json").exists()
        analysis["has_eslint"] = any(
            (project_path / eslint_file).exists()
            for eslint_file in [".eslintrc.js", ".eslintrc.json", ".eslintrc.yml"]
        )
    elif project_type == "python":
        analysis["has_virtual_env"] = any(
            (project_path / venv_dir).exists() for venv_dir in ["venv", ".venv", "env", ".env"]
        )
        analysis["has_setup_py"] = (project_path / "setup.py").exists()
        analysis["has_pyproject_toml"] = (project_path / "pyproject.toml").exists()

    return analysis
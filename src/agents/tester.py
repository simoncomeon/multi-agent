"""
Testing Agent - Handles test creation and execution tasks
"""

import os
import subprocess
from datetime import datetime
from typing import Dict, List

from ..core.models import Colors
from ..core.utils import colored_print


class TestingAgent:
    """Specialized agent for testing operations"""
    
    def __init__(self, terminal_instance, comm_instance):
        self.terminal = terminal_instance
        self.comm = comm_instance
        self.agent_id = "tester"
        self.workspace_dir = terminal_instance.workspace_dir
    
    def handle_testing_task(self, task: Dict) -> Dict:
        """Handle testing tasks"""
        
        description = task["description"]
        colored_print(f"TESTER: Processing testing task", Colors.BRIGHT_CYAN)
        colored_print(f"   Task: {description}", Colors.CYAN)
        
        desc_lower = description.lower()
        
        if "create" in desc_lower or "generate" in desc_lower:
            return self.create_tests(description)
        elif "run" in desc_lower or "execute" in desc_lower:
            return self.run_tests(description)
        elif "unit" in desc_lower:
            return self.handle_unit_tests(description)
        elif "integration" in desc_lower:
            return self.handle_integration_tests(description)
        elif "e2e" in desc_lower or "end-to-end" in desc_lower:
            return self.handle_e2e_tests(description)
        else:
            return self.general_testing(description)
    
    def create_tests(self, description: str) -> Dict:
        """Create test files and test cases"""
        
        colored_print(f"   ACTION: Creating tests", Colors.YELLOW)
        
        # Analyze project structure to determine testing framework
        test_framework = self.detect_testing_framework()
        
        if test_framework == "jest":
            return self.create_jest_tests(description)
        elif test_framework == "pytest":
            return self.create_pytest_tests(description)
        elif test_framework == "mocha":
            return self.create_mocha_tests(description)
        else:
            return self.create_generic_tests(description)
    
    def detect_testing_framework(self) -> str:
        """Detect the appropriate testing framework for the project"""
        
        # Check for package.json (JavaScript/Node.js projects)
        package_json_path = os.path.join(self.workspace_dir, "package.json")
        if os.path.exists(package_json_path):
            try:
                import json
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                
                dependencies = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
                
                if 'jest' in dependencies:
                    return "jest"
                elif 'mocha' in dependencies:
                    return "mocha"
                else:
                    return "jest"  # Default for JavaScript projects
            except:
                return "jest"
        
        # Check for Python files
        python_files = []
        for root, dirs, files in os.walk(self.workspace_dir):
            python_files.extend([f for f in files if f.endswith('.py')])
        
        if python_files:
            return "pytest"
        
        return "generic"
    
    def create_jest_tests(self, description: str) -> Dict:
        """Create Jest test files"""
        
        test_files_created = []
        
        # Create basic test structure
        test_dir = os.path.join(self.workspace_dir, "__tests__")
        os.makedirs(test_dir, exist_ok=True)
        
        # Create a sample test file
        test_file_content = '''import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Import your component here
// import MyComponent from '../src/components/MyComponent';

describe('Component Tests', () => {
  test('renders without crashing', () => {
    // Add your test cases here
    expect(true).toBe(true);
  });
  
  test('displays correct content', () => {
    // Test component rendering
    // render(<MyComponent />);
    // expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });
});'''
        
        test_file_path = os.path.join(test_dir, "component.test.js")
        with open(test_file_path, 'w') as f:
            f.write(test_file_content)
        
        test_files_created.append(test_file_path)
        
        # Update package.json with test dependencies if needed
        self.ensure_jest_dependencies()
        
        colored_print(f"   SUCCESS: Created Jest test files", Colors.GREEN)
        
        return {
            "status": "success",
            "framework": "jest",
            "files_created": test_files_created,
            "message": "Jest test files created successfully",
            "next_steps": [
                "Install testing dependencies: npm install --save-dev @testing-library/react @testing-library/jest-dom",
                "Update test cases with actual component imports",
                "Run tests with: npm test"
            ]
        }
    
    def create_pytest_tests(self, description: str) -> Dict:
        """Create pytest test files"""
        
        test_files_created = []
        
        # Create test directory
        test_dir = os.path.join(self.workspace_dir, "tests")
        os.makedirs(test_dir, exist_ok=True)
        
        # Create __init__.py
        init_file = os.path.join(test_dir, "__init__.py")
        with open(init_file, 'w') as f:
            f.write("# Test package initialization\\n")
        
        # Create sample test file
        test_file_content = '''import pytest
import sys
import os

# Add src to path if needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestExample:
    """Example test class"""
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        assert True
    
    def test_with_setup(self):
        """Test with setup"""
        # Setup test data
        test_data = {"key": "value"}
        
        # Test assertions
        assert test_data["key"] == "value"
        assert len(test_data) == 1
    
    def test_exception_handling(self):
        """Test exception handling"""
        with pytest.raises(ValueError):
            raise ValueError("Test exception")

def test_standalone_function():
    """Standalone test function"""
    result = 2 + 2
    assert result == 4'''
        
        test_file_path = os.path.join(test_dir, "test_example.py")
        with open(test_file_path, 'w') as f:
            f.write(test_file_content)
        
        test_files_created.extend([init_file, test_file_path])
        
        colored_print(f"   SUCCESS: Created pytest test files", Colors.GREEN)
        
        return {
            "status": "success",
            "framework": "pytest",
            "files_created": test_files_created,
            "message": "Pytest test files created successfully",
            "next_steps": [
                "Install pytest: pip install pytest",
                "Update test cases with actual imports",
                "Run tests with: pytest"
            ]
        }
    
    def run_tests(self, description: str) -> Dict:
        """Run existing tests"""
        
        colored_print(f"   ACTION: Running tests", Colors.YELLOW)
        
        test_framework = self.detect_testing_framework()
        
        try:
            if test_framework == "jest":
                return self.run_jest_tests()
            elif test_framework == "pytest":
                return self.run_pytest_tests()
            elif test_framework == "mocha":
                return self.run_mocha_tests()
            else:
                return self.run_generic_tests()
                
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Test execution failed: {str(e)}",
                "error": str(e)
            }
    
    def run_jest_tests(self) -> Dict:
        """Run Jest tests"""
        
        try:
            result = subprocess.run(
                ["npm", "test", "--", "--watchAll=false"],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            tests_passed = "failed" not in result.stdout.lower()
            
            colored_print(f"   RESULT: Jest tests {'passed' if tests_passed else 'failed'}", 
                         Colors.GREEN if tests_passed else Colors.RED)
            
            return {
                "status": "success" if tests_passed else "failed",
                "framework": "jest",
                "output": result.stdout,
                "error_output": result.stderr,
                "tests_passed": tests_passed,
                "message": f"Jest tests {'passed' if tests_passed else 'failed'}"
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "message": "Jest tests timed out after 60 seconds"
            }
        except FileNotFoundError:
            return {
                "status": "failed",
                "message": "npm not found. Ensure Node.js and npm are installed."
            }
    
    def run_pytest_tests(self) -> Dict:
        """Run pytest tests"""
        
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "-v"],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            tests_passed = result.returncode == 0
            
            colored_print(f"   RESULT: Pytest tests {'passed' if tests_passed else 'failed'}", 
                         Colors.GREEN if tests_passed else Colors.RED)
            
            return {
                "status": "success" if tests_passed else "failed",
                "framework": "pytest",
                "output": result.stdout,
                "error_output": result.stderr,
                "tests_passed": tests_passed,
                "return_code": result.returncode,
                "message": f"Pytest tests {'passed' if tests_passed else 'failed'}"
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "message": "Pytest tests timed out after 60 seconds"
            }
        except FileNotFoundError:
            return {
                "status": "failed",
                "message": "Python or pytest not found. Ensure they are installed."
            }
    
    def handle_unit_tests(self, description: str) -> Dict:
        """Handle unit test specific operations"""
        
        colored_print(f"   FOCUS: Unit testing", Colors.YELLOW)
        
        return {
            "status": "success",
            "test_type": "unit",
            "message": "Unit testing task completed",
            "recommendations": [
                "Test individual functions and methods in isolation",
                "Mock external dependencies",
                "Aim for high code coverage",
                "Keep tests fast and focused",
                "Use descriptive test names"
            ]
        }
    
    def handle_integration_tests(self, description: str) -> Dict:
        """Handle integration test specific operations"""
        
        colored_print(f"   FOCUS: Integration testing", Colors.YELLOW)
        
        return {
            "status": "success",
            "test_type": "integration",
            "message": "Integration testing task completed",
            "recommendations": [
                "Test interactions between components",
                "Test API endpoints and database operations",
                "Use test databases or mock services",
                "Test error handling and edge cases",
                "Validate data flow between modules"
            ]
        }
    
    def handle_e2e_tests(self, description: str) -> Dict:
        """Handle end-to-end test specific operations"""
        
        colored_print(f"   FOCUS: End-to-end testing", Colors.YELLOW)
        
        return {
            "status": "success",
            "test_type": "e2e",
            "message": "End-to-end testing task completed",
            "recommendations": [
                "Test complete user workflows",
                "Use tools like Cypress, Playwright, or Selenium",
                "Test in realistic environments",
                "Focus on critical user paths",
                "Include visual regression testing"
            ],
            "suggested_tools": ["Cypress", "Playwright", "Selenium", "Puppeteer"]
        }
    
    def ensure_jest_dependencies(self):
        """Ensure Jest testing dependencies are available"""
        
        package_json_path = os.path.join(self.workspace_dir, "package.json")
        if os.path.exists(package_json_path):
            colored_print(f"   INFO: Verify Jest dependencies in package.json", Colors.CYAN)
        else:
            colored_print(f"   WARNING: No package.json found. Create one with npm init", Colors.YELLOW)
    
    def create_generic_tests(self, description: str) -> Dict:
        """Create generic test structure"""
        
        test_dir = os.path.join(self.workspace_dir, "tests")
        os.makedirs(test_dir, exist_ok=True)
        
        readme_content = '''# Tests Directory

This directory contains test files for the project.

## Test Types
- Unit tests: Test individual functions/methods
- Integration tests: Test component interactions  
- End-to-end tests: Test complete user workflows

## Running Tests
Refer to your project's testing framework documentation for running instructions.
'''
        
        readme_path = os.path.join(test_dir, "README.md")
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        return {
            "status": "success",
            "framework": "generic",
            "files_created": [readme_path],
            "message": "Generic test structure created"
        }
    
    def run_generic_tests(self) -> Dict:
        """Run generic tests"""
        
        return {
            "status": "partial",
            "message": "No specific testing framework detected. Please specify test runner.",
            "suggestion": "Install and configure a testing framework like Jest, pytest, or Mocha"
        }
    
    def general_testing(self, description: str) -> Dict:
        """Handle general testing tasks"""
        
        colored_print(f"   INFO: Processing general testing request", Colors.YELLOW)
        
        return {
            "status": "success",
            "message": f"Testing task processed: {description}",
            "recommendations": [
                "Identify appropriate testing strategy",
                "Choose suitable testing framework",
                "Create comprehensive test cases",
                "Implement continuous testing",
                "Monitor test coverage"
            ]
        }
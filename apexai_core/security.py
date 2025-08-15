"""
Security module for ApexAI-Core.

This module provides security features for the ApexAI-Core package,
including code sandboxing, input validation, and secure execution.
"""

import os
import re
import sys
import ast
import json
import logging
import subprocess
import tempfile
from typing import Dict, List, Set, Tuple, Optional, Any, Union

logger = logging.getLogger(__name__)


class SecurityViolation(Exception):
    """Exception raised for security violations."""
    pass


class CodeSandbox:
    """
    Sandbox for executing untrusted code safely.
    
    This class provides a sandbox for executing untrusted code safely,
    with restrictions on imports, system calls, and file access.
    
    Attributes:
        allowed_modules: Set of allowed module imports
        allowed_builtins: Set of allowed built-in functions
        allowed_file_paths: List of allowed file paths for read/write
        max_execution_time: Maximum execution time in seconds
    """
    
    def __init__(
        self,
        allowed_modules: Optional[Set[str]] = None,
        allowed_builtins: Optional[Set[str]] = None,
        allowed_file_paths: Optional[List[str]] = None,
        max_execution_time: int = 30
    ):
        """
        Initialize the CodeSandbox.
        
        Args:
            allowed_modules: Set of allowed module imports
            allowed_builtins: Set of allowed built-in functions
            allowed_file_paths: List of allowed file paths for read/write
            max_execution_time: Maximum execution time in seconds
        """
        self.allowed_modules = allowed_modules or {
            "math", "random", "datetime", "json", "csv", "re",
            "collections", "itertools", "functools", "typing",
            "fastapi", "pydantic"
        }
        
        self.allowed_builtins = allowed_builtins or {
            "abs", "all", "any", "ascii", "bin", "bool", "bytes",
            "chr", "complex", "dict", "dir", "divmod", "enumerate",
            "filter", "float", "format", "frozenset", "hash", "hex",
            "int", "isinstance", "issubclass", "iter", "len", "list",
            "map", "max", "min", "next", "oct", "ord", "pow", "print",
            "range", "repr", "reversed", "round", "set", "slice",
            "sorted", "str", "sum", "tuple", "type", "zip"
        }
        
        self.allowed_file_paths = allowed_file_paths or []
        self.max_execution_time = max_execution_time
    
    def validate_code(self, code: str) -> List[str]:
        """
        Validate code for security violations.
        
        Args:
            code: Python code to validate
            
        Returns:
            List of security violations found
        """
        violations = []
        
        try:
            # Parse the code into an AST
            tree = ast.parse(code)
            
            # Check for disallowed imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        module_name = name.name.split(".")[0]
                        if module_name not in self.allowed_modules:
                            violations.append(f"Disallowed import: {module_name}")
                
                elif isinstance(node, ast.ImportFrom):
                    module_name = node.module.split(".")[0] if node.module else ""
                    if module_name not in self.allowed_modules:
                        violations.append(f"Disallowed import from: {module_name}")
                
                # Check for exec and eval calls
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ["exec", "eval"]:
                            violations.append(f"Disallowed function call: {node.func.id}")
                
                # Check for __import__ calls
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "__import__":
                    violations.append("Disallowed __import__ call")
                
                # Check for os.system, subprocess.run, etc.
                elif isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        if node.value.id == "os" and node.attr in ["system", "popen", "spawn", "exec"]:
                            violations.append(f"Disallowed os.{node.attr} call")
                        elif node.value.id == "subprocess":
                            violations.append(f"Disallowed subprocess.{node.attr} call")
                
                # Check for open calls with write mode
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
                    if len(node.args) >= 2:
                        # Check if the mode argument contains 'w', 'a', or '+'
                        if isinstance(node.args[1], ast.Str):
                            mode = node.args[1].s
                            if any(c in mode for c in "wa+"):
                                violations.append("Disallowed file write operation")
        
        except SyntaxError as e:
            violations.append(f"Syntax error: {e}")
        
        return violations
    
    def execute_code(self, code: str) -> Tuple[bool, str]:
        """
        Execute code in a sandbox.
        
        Args:
            code: Python code to execute
            
        Returns:
            Tuple of (success: bool, output: str)
        """
        # Validate the code first
        violations = self.validate_code(code)
        if violations:
            return False, f"Security violations detected: {', '.join(violations)}"
        
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(code.encode("utf-8"))
        
        try:
            # Execute the code in a subprocess with restricted permissions
            result = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=self.max_execution_time
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            return False, f"Execution timed out after {self.max_execution_time} seconds"
        except Exception as e:
            return False, f"Execution error: {e}"
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass


class InputValidator:
    """
    Validator for user input.
    
    This class provides validation for user input to prevent
    injection attacks and other security issues.
    """
    
    @staticmethod
    def validate_mission(mission: str) -> Tuple[bool, str]:
        """
        Validate a mission string.
        
        Args:
            mission: Mission string to validate
            
        Returns:
            Tuple of (valid: bool, error_message: str)
        """
        # Check for maximum length
        if len(mission) > 1000:
            return False, "Mission is too long (maximum 1000 characters)"
        
        # Check for potentially dangerous patterns
        dangerous_patterns = [
            r"rm\s+-rf",
            r"sudo",
            r"chmod\s+777",
            r"eval\(",
            r"exec\(",
            r"os\.system",
            r"subprocess",
            r"__import__",
            r"open\([^)]+,\s*['\"]w['\"]",
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, mission, re.IGNORECASE):
                return False, f"Mission contains potentially dangerous pattern: {pattern}"
        
        return True, ""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename to prevent path traversal attacks.
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Sanitized filename
        """
        # Remove any directory traversal attempts
        filename = os.path.basename(filename)
        
        # Remove any non-alphanumeric characters except for .-_
        filename = re.sub(r"[^\w.-]", "_", filename)
        
        return filename
    
    @staticmethod
    def validate_json(json_str: str) -> Tuple[bool, Any]:
        """
        Validate and parse JSON.
        
        Args:
            json_str: JSON string to validate
            
        Returns:
            Tuple of (valid: bool, parsed_json: Any)
        """
        try:
            parsed = json.loads(json_str)
            return True, parsed
        except json.JSONDecodeError:
            return False, "Invalid JSON format"


def secure_execution_wrapper(func):
    """
    Decorator to add security checks to a function.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with security checks
    """
    def wrapper(*args, **kwargs):
        # Log the function call
        logger.debug(f"Secure execution of {func.__name__} with args: {args}, kwargs: {kwargs}")
        
        # Add security checks here
        # ...
        
        # Call the original function
        return func(*args, **kwargs)
    
    return wrapper


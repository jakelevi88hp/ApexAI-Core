"""
GODCodeAgentOllama - A Python-based code generation and execution framework.

This module provides a code agent that uses the Ollama API to recursively generate,
execute, and refine Python scripts for specified tasks.
"""

import os
import re
import sys
import logging
import subprocess
import requests
from typing import Dict, List, Tuple, Optional, Any, Union

# === CONFIGURATION ===
# Default configuration values, can be overridden by environment variables
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "codellama:instruct"
DEFAULT_MAX_CYCLES = 7
DEFAULT_PROJECT_ROOT = "apex_auto_project"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OllamaAPIError(Exception):
    """Exception raised for errors in the Ollama API."""
    pass


class CodeGenerationError(Exception):
    """Exception raised for errors in code generation."""
    pass


class CodeExecutionError(Exception):
    """Exception raised for errors in code execution."""
    pass


class GODCodeAgentOllama:
    """
    A recursive code generation and execution agent using Ollama API.
    
    This agent can generate Python code based on natural language missions,
    execute the code, and recursively refine it to achieve the desired outcome.
    It supports FastAPI applications and can auto-install missing dependencies.
    
    Attributes:
        project_root (str): Directory where generated modules are stored
        max_cycles (int): Maximum number of recursive cycles allowed
        verbose (bool): Whether to enable verbose logging output
        ollama_base_url (str): Base URL for the Ollama API
        ollama_model (str): Model to use for code generation
    """
    
    def __init__(
        self, 
        project_root: Optional[str] = None, 
        max_cycles: Optional[int] = None, 
        verbose: bool = True,
        ollama_base_url: Optional[str] = None,
        ollama_model: Optional[str] = None
    ):
        """
        Initialize the GODCodeAgentOllama instance.
        
        Args:
            project_root: Directory for storing generated modules. Defaults to environment 
                         variable PROJECT_ROOT or DEFAULT_PROJECT_ROOT
            max_cycles: Maximum recursive cycles. Defaults to environment variable 
                       MAX_CYCLES or DEFAULT_MAX_CYCLES
            verbose: Enable verbose output logging
            ollama_base_url: Base URL for the Ollama API. Defaults to environment variable
                           OLLAMA_BASE_URL or DEFAULT_OLLAMA_BASE_URL
            ollama_model: Model to use for code generation. Defaults to environment variable
                        OLLAMA_MODEL or DEFAULT_OLLAMA_MODEL
        """
        self.project_root = project_root or os.getenv("PROJECT_ROOT", DEFAULT_PROJECT_ROOT)
        self.max_cycles = max_cycles or int(os.getenv("MAX_CYCLES", str(DEFAULT_MAX_CYCLES)))
        self.verbose = verbose
        self.ollama_base_url = ollama_base_url or os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)
        self.ollama_model = ollama_model or os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
        
        # Create project directory if it doesn't exist
        try:
            if not os.path.exists(self.project_root):
                os.makedirs(self.project_root)
                logger.info(f"Created project directory: {self.project_root}")
        except OSError as e:
            logger.error(f"Failed to create project directory {self.project_root}: {e}")
            raise

    def ollama_generate(self, mission: str, context: str = "") -> str:
        """
        Generate Python code using the Ollama API based on the given mission.
        
        Args:
            mission: The task description for code generation
            context: Additional context from previous iterations
            
        Returns:
            Generated Python code as a string
            
        Raises:
            OllamaAPIError: If API request fails
            CodeGenerationError: If code generation fails
        """
        prompt = (
            f"Write a single, fully working Python script for the following task. "
            f"Output only valid, executable code—no markdown, no explanations, no '[PYTHON]' tokens, no ellipses. "
            f"If you cannot solve the task, output: print('Hello world from GODCodeAgent').\n"
            f"Task: {mission}\n"
            f"Context/output: {context}\n"
        )
        
        try:
            logger.debug(f"Sending request to Ollama API: {self.ollama_base_url}")
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30  # Add timeout to prevent hanging
            )
            response.raise_for_status()  # Raise exception for HTTP errors
            
            response_data = response.json()
            if 'response' not in response_data:
                logger.error(f"Invalid API response format: {response_data}")
                raise OllamaAPIError("API response missing 'response' field")
                
            raw = response_data['response']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed: {e}")
            raise OllamaAPIError(f"API request failed: {e}")
        except ValueError as e:
            logger.error(f"Invalid API response: {e}")
            raise OllamaAPIError(f"Invalid API response: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in ollama_generate: {e}")
            raise CodeGenerationError(f"Unexpected error: {e}")

        return self._clean_generated_code(raw)

    def _clean_generated_code(self, raw_code: str) -> str:
        """
        Clean and filter the raw code generated by Ollama API.
        
        Args:
            raw_code: Raw code string from API response
            
        Returns:
            Cleaned and filtered Python code
        """
        # Remove markdown, ellipses, [PYTHON] tokens, etc.
        for bad_token in ["```python", "```", "[PYTHON]", "[/PYTHON]", "..."]:
            raw_code = raw_code.replace(bad_token, "")
        raw_code = raw_code.strip()

        allowed_starts = (
            'import ', 'from ', 'def ', 'class ', '@', 'print(', 'if ', 'for ', 'while ',
            'with ', 'try:', 'except ', 'return ', 'async ', '#', 'else:', 'elif ',
            'app.', 'output', 'result', 'input', 'pass', 'raise ', 'yield ', 'global ',
            'nonlocal ', 'assert ', 'lambda ', 'open(', 'subprocess', 'BaseModel', 'os.', 'sys.', 'main', ''
        )
        banned_phrases = [
            'This script', 'To test', 'curl', 'python ', '```', 'Note that', 'also note', 'you can use',
            'The `/status`', 'The `/execute`', 'If you', 'To run', 'For example', 'Here is', 'To start', 'After running'
        ]
        
        lines = raw_code.splitlines()
        code_lines = []
        for line in lines:
            line_strip = line.strip()
            if (
                line_strip.startswith(allowed_starts)
                or line_strip == ""
                or (len(line_strip) > 0 and line_strip[0] in ('"', "'"))
                or (line_strip.isdigit())
            ):
                if not any(bp.lower() in line_strip.lower() for bp in banned_phrases):
                    code_lines.append(line)
        
        code = "\n".join(code_lines).strip()
        if not code or len(code) < 10:
            logger.warning("Generated code too short or empty, using fallback")
            code = "print('Hello world from GODCodeAgent')"
        
        return code

    def operator_review(self, code: str, filename: str) -> bool:
        """
        Review generated code to determine if it meets basic quality criteria.
        
        Args:
            code: The generated Python code to review
            filename: The filename for the code (for logging purposes)
            
        Returns:
            True if code passes review, False otherwise
        """
        review_keywords = ["def ", "class ", "print(", "FastAPI"]
        passed = any(word in code for word in review_keywords)
        
        if self.verbose:
            status = "PASSED" if passed else "FAILED"
            logger.info(f"Operator review for {filename}: {status}")
            
        return passed

    def destroyer_prune(self, file_path: str) -> None:
        """
        Remove a failed code file from the filesystem.
        
        Args:
            file_path: Path to the file to be removed
        """
        try:
            os.remove(file_path)
            logger.info(f"Destroyed broken file: {file_path}")
        except OSError as e:
            logger.error(f"Failed to destroy file: {file_path}. Reason: {e}")
        except Exception as e:
            logger.error(f"Unexpected error destroying file {file_path}: {e}")

    def auto_install_module(self, error_output: str) -> List[str]:
        """
        Automatically install missing Python modules based on error output.
        
        Args:
            error_output: The error message containing module not found errors
            
        Returns:
            List of installed modules
        """
        installed_modules = []
        matches = re.findall(r"No module named '([\w_]+)'", error_output)
        for module in matches:
            logger.info(f"Auto-installing missing module: {module}")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", module], 
                    check=True,
                    capture_output=True,
                    text=True
                )
                logger.info(f"Successfully installed module: {module}")
                installed_modules.append(module)
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to auto-install module {module}: {e.stderr}")
            except Exception as e:
                logger.error(f"Unexpected error installing module {module}: {e}")
        
        return installed_modules

    def should_run_with_uvicorn(self, code: str, file_path: str) -> bool:
        """
        Determine if the code should be run with uvicorn (FastAPI server).
        
        Args:
            code: The Python code to analyze
            file_path: Path to the code file (for logging)
            
        Returns:
            True if code appears to be a FastAPI application
        """
        is_fastapi = ("FastAPI" in code or "uvicorn" in code) and ("app = FastAPI()" in code)
        if is_fastapi:
            logger.debug(f"Detected FastAPI application in {file_path}")
        return is_fastapi

    def _execute_with_uvicorn(self, code: str, file_path: str) -> Tuple[bool, str]:
        """
        Execute a FastAPI application using uvicorn.
        
        Args:
            code: The Python code containing FastAPI app
            file_path: Path to the code file
            
        Returns:
            Tuple of (success: bool, output: str)
            
        Raises:
            CodeExecutionError: If execution fails
        """
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        logger.info(f"Running FastAPI app with uvicorn: {module_name}:app")
        
        try:
            completed = subprocess.run(
                ["uvicorn", f"{module_name}:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
                check=True,
                capture_output=True,
                text=True,
                timeout=20,
                cwd=os.path.dirname(file_path)
            )
            # If the server exits by itself, that's abnormal (usually a crash)
            return True, completed.stdout
        except subprocess.TimeoutExpired:
            logger.info("Uvicorn server launched and is running at http://localhost:8000")
            return True, "Uvicorn server running—manual test at http://localhost:8000"
        except subprocess.CalledProcessError as e:
            logger.error(f"Uvicorn execution failed: {e.stderr}")
            raise CodeExecutionError(f"Uvicorn execution failed: {e.stderr}")
        except Exception as e:
            logger.error(f"Unexpected error running uvicorn: {e}")
            raise CodeExecutionError(f"Unexpected error running uvicorn: {e}")

    def _execute_regular_python(self, file_path: str) -> Tuple[bool, str]:
        """
        Execute a regular Python script.
        
        Args:
            file_path: Path to the Python file to execute
            
        Returns:
            Tuple of (success: bool, output: str)
            
        Raises:
            CodeExecutionError: If execution fails
        """
        try:
            completed = subprocess.run(
                ["python", file_path],
                check=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            return True, completed.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Python execution failed: {e.stderr}")
            raise CodeExecutionError(f"Python execution failed: {e.stderr}")
        except subprocess.TimeoutExpired:
            logger.error(f"Python execution timed out for {file_path}")
            raise CodeExecutionError(f"Python execution timed out for {file_path}")
        except Exception as e:
            logger.error(f"Unexpected error executing Python: {e}")
            raise CodeExecutionError(f"Unexpected error executing Python: {e}")

    def write_and_execute(self, code: str, file_path: str) -> Tuple[bool, str]:
        """
        Write code to file and execute it, handling both regular Python and FastAPI apps.
        
        Args:
            code: Python code to write and execute
            file_path: Path where the code file should be written
            
        Returns:
            Tuple of (success: bool, output: str)
        """
        # Write code to file
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            logger.debug(f"Code written to {file_path}")
        except IOError as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            return False, f"File write error: {e}"

        # Execute the code
        try:
            if self.should_run_with_uvicorn(code, file_path):
                return self._execute_with_uvicorn(code, file_path)
            else:
                return self._execute_regular_python(file_path)
                
        except CodeExecutionError as e:
            # Check if it's a ModuleNotFoundError
            error_message = str(e)
            if "ModuleNotFoundError" in error_message:
                logger.info("Attempting to auto-install missing modules")
                installed_modules = self.auto_install_module(error_message)
                
                if installed_modules:
                    # Retry execution after installing modules
                    try:
                        if self.should_run_with_uvicorn(code, file_path):
                            return self._execute_with_uvicorn(code, file_path)
                        else:
                            return self._execute_regular_python(file_path)
                    except Exception as retry_error:
                        logger.error(f"Execution failed even after installing modules: {retry_error}")
                        return False, str(retry_error)
            
            return False, error_message
            
        except Exception as e:
            logger.error(f"General execution error in {file_path}: {e}")
            return False, str(e)

    def recursive_build(self, mission: str, context: str = "", cycle: int = 1) -> None:
        """
        Recursively generate, execute, and refine code to complete the given mission.
        
        This method implements the core recursive logic where code is generated,
        executed, reviewed, and if successful, enhanced in subsequent cycles.
        
        Args:
            mission: The task description to accomplish
            context: Context from previous iterations (execution output)
            cycle: Current cycle number (starts at 1)
        """
        if cycle > self.max_cycles:
            logger.warning(f"Max recursion reached ({self.max_cycles} cycles). Stopping.")
            return

        filename = f"module_{cycle}.py"
        file_path = os.path.join(self.project_root, filename)

        logger.info(f"=== CYCLE {cycle}: GENERATOR ===")
        try:
            code = self.ollama_generate(mission, context)
        except (OllamaAPIError, CodeGenerationError) as e:
            logger.error(f"Code generation failed in cycle {cycle}: {e}")
            return

        # Write generated code to file
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            logger.debug(f"Generated code written to {filename}")
        except IOError as e:
            logger.error(f"Failed to write generated code to {filename}: {e}")
            return

        if self.verbose:
            preview = code[:300] + "..." if len(code) > 300 else code
            logger.info(f"Code generated for {filename}:\n{preview}")

        logger.info(f"=== CYCLE {cycle}: OPERATOR ===")
        success, output = self.write_and_execute(code, file_path)
        
        if self.operator_review(code, filename) and success:
            if self.verbose:
                output_preview = output[:300] + "..." if len(output) > 300 else output
                logger.info(f"Execution output: {output_preview}")
            
            # Continue to next cycle if we haven't reached the limit
            if cycle < self.max_cycles:
                next_mission = f"Expand, optimize, or add new required modules to complete: {mission}"
                logger.info(f"Proceeding to cycle {cycle + 1}")
                self.recursive_build(next_mission, output, cycle + 1)
            else:
                logger.info(f"Successfully completed all {self.max_cycles} cycles")
        else:
            logger.warning(f"=== CYCLE {cycle}: DESTROYER (Failed Review or Execution) ===")
            if self.verbose:
                logger.debug(f"FAILED CODE:\n{code}")
                logger.debug(f"ERROR OUTPUT:\n{output}")
            self.destroyer_prune(file_path)


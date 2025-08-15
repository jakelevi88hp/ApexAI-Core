"""
AsyncAgent - Asynchronous version of GODCodeAgentOllama.

This module provides an asynchronous implementation of the GODCodeAgentOllama
for better performance with I/O-bound operations.
"""

import os
import sys
import json
import logging
import traceback
import asyncio
import aiohttp
import aiofiles
from typing import Dict, List, Tuple, Optional, Any, Union

from apexai_core.agents.god_code_agent import OllamaAPIError, CodeGenerationError, CodeExecutionError
from apexai_core.utils import is_fastapi_code

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AsyncAgent:
    """
    Asynchronous agent for code generation and execution.
    
    This class provides asynchronous versions of the GODCodeAgentOllama methods
    for better performance with I/O-bound operations.
    
    Attributes:
        project_root (str): Directory for storing generated modules
        max_cycles (int): Maximum recursive cycles for code generation
        verbose (bool): Whether to enable verbose logging
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
        Initialize the AsyncAgent.
        
        Args:
            project_root: Directory for storing generated modules
            max_cycles: Maximum recursive cycles for code generation
            verbose: Enable verbose output logging
            ollama_base_url: Base URL for the Ollama API
            ollama_model: Model to use for code generation
        """
        self.project_root = project_root or os.getenv("PROJECT_ROOT", "apex_auto_project")
        self.max_cycles = max_cycles or int(os.getenv("MAX_CYCLES", "7"))
        self.verbose = verbose
        self.ollama_base_url = ollama_base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = ollama_model or os.getenv("OLLAMA_MODEL", "codellama:instruct")
        
        # Create project directory if it doesn't exist
        if not os.path.exists(self.project_root):
            os.makedirs(self.project_root)
            logger.info(f"Created project directory: {self.project_root}")
            
        if self.verbose:
            logger.info(f"AsyncAgent initialized with model {self.ollama_model}")
            logger.info(f"Project root: {self.project_root}")
            logger.info(f"Max cycles: {self.max_cycles}")

    async def ollama_generate_async(self, mission: str, context: str = "") -> str:
        """
        Generate code using Ollama API asynchronously.
        
        Args:
            mission: The task description for code generation
            context: Additional context from previous iterations
            
        Returns:
            Generated code
            
        Raises:
            OllamaAPIError: If API request fails
            CodeGenerationError: If code generation fails
        """
        if self.verbose:
            logger.info(f"Generating code for mission: {mission[:50]}{'...' if len(mission) > 50 else ''}")
            
        prompt = f"""
        You are an expert Python developer. Your task is to write Python code based on the following mission:
        
        {mission}
        
        {context}
        
        Write only the Python code without any explanations. The code should be complete, well-structured, and ready to run.
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=300  # 5 minutes timeout
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise OllamaAPIError(f"Ollama API error: {response.status} - {error_text}")
                        
                    data = await response.json()
                    code = data.get("response", "")
                    
                    if not code:
                        raise CodeGenerationError("Empty response from Ollama API")
                        
                    # Clean up the code
                    code = self._clean_code(code)
                    
                    if self.verbose:
                        logger.info("Code generation successful")
                        
                    return code
                    
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error: {e}")
            raise OllamaAPIError(f"HTTP error: {e}")
        except asyncio.TimeoutError:
            logger.error("Request timed out")
            raise OllamaAPIError("Request timed out")
        except json.JSONDecodeError:
            logger.error("Invalid JSON response")
            raise OllamaAPIError("Invalid JSON response")
        except (OllamaAPIError, CodeGenerationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.debug(traceback.format_exc())
            raise CodeGenerationError(f"Unexpected error: {e}")

    def _clean_code(self, code: str) -> str:
        """
        Clean up the generated code.
        
        Args:
            code: Generated code
            
        Returns:
            Cleaned code
        """
        # Remove code blocks if present
        if "```python" in code:
            code = code.split("```python")[1]
            
        if "```" in code:
            code = code.split("```")[0]
            
        # Remove leading/trailing whitespace
        code = code.strip()
        
        return code

    async def write_and_execute_async(self, code: str, filename: str) -> Tuple[bool, str]:
        """
        Write code to a file and execute it asynchronously.
        
        Args:
            code: Code to write and execute
            filename: Name of the file to write
            
        Returns:
            Tuple of (success: bool, output: str)
            
        Raises:
            CodeExecutionError: If code execution fails
        """
        file_path = os.path.join(self.project_root, filename)
        
        try:
            # Write code to file
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(code)
                
            if self.verbose:
                logger.info(f"Code written to {file_path}")
                
            # Check if it's a FastAPI app
            if is_fastapi_code(code):
                if self.verbose:
                    logger.info("Detected FastAPI code, executing with uvicorn")
                return await self._execute_with_uvicorn_async(file_path)
            else:
                if self.verbose:
                    logger.info("Executing regular Python code")
                return await self._execute_regular_python_async(file_path)
                
        except IOError as e:
            logger.error(f"Failed to write code to file: {e}")
            raise CodeExecutionError(f"Failed to write code to file: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.debug(traceback.format_exc())
            raise CodeExecutionError(f"Unexpected error: {e}")

    async def _execute_regular_python_async(self, file_path: str) -> Tuple[bool, str]:
        """
        Execute regular Python code asynchronously.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Tuple of (success: bool, output: str)
        """
        try:
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                sys.executable, file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for process to complete
            stdout, stderr = await process.communicate()
            
            # Check if execution was successful
            if process.returncode == 0:
                output = stdout.decode("utf-8")
                if self.verbose:
                    logger.info("Code execution successful")
                return True, output
            else:
                error = stderr.decode("utf-8")
                if self.verbose:
                    logger.warning(f"Code execution failed: {error}")
                    
                # Check for missing module errors
                if "ModuleNotFoundError" in error or "ImportError" in error:
                    if self.verbose:
                        logger.info("Attempting to install missing modules")
                        
                    # Install missing modules
                    installed_modules = await self.auto_install_module_async(error)
                    
                    if installed_modules:
                        if self.verbose:
                            logger.info(f"Installed modules: {', '.join(installed_modules)}")
                            logger.info("Retrying execution")
                            
                        # Retry execution
                        return await self._execute_regular_python_async(file_path)
                        
                return False, error
                
        except Exception as e:
            logger.error(f"Execution error: {e}")
            logger.debug(traceback.format_exc())
            return False, str(e)

    async def _execute_with_uvicorn_async(self, file_path: str) -> Tuple[bool, str]:
        """
        Execute FastAPI code with uvicorn asynchronously.
        
        Args:
            file_path: Path to the FastAPI file
            
        Returns:
            Tuple of (success: bool, output: str)
        """
        try:
            # Get module name from file path
            module_name = os.path.basename(file_path).replace(".py", "")
            
            # Check if uvicorn is installed
            try:
                import uvicorn
            except ImportError:
                if self.verbose:
                    logger.info("Installing uvicorn")
                    
                # Install uvicorn
                process = await asyncio.create_subprocess_exec(
                    sys.executable, "-m", "pip", "install", "uvicorn",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                # Wait for process to complete
                await process.communicate()
                
                # Check if installation was successful
                if process.returncode != 0:
                    return False, "Failed to install uvicorn"
                    
            # Start uvicorn server
            if self.verbose:
                logger.info(f"Starting uvicorn server for module {module_name}")
                
            # Create a message to display
            message = (
                f"FastAPI app detected. Starting uvicorn server for module {module_name}.\n"
                f"API will be available at http://127.0.0.1:8000\n"
                f"Press Ctrl+C to stop the server."
            )
            
            return True, message
            
        except Exception as e:
            logger.error(f"Uvicorn execution error: {e}")
            logger.debug(traceback.format_exc())
            return False, str(e)

    async def auto_install_module_async(self, error_message: str) -> List[str]:
        """
        Automatically install missing modules from error message asynchronously.
        
        Args:
            error_message: Error message from code execution
            
        Returns:
            List of installed modules
        """
        installed_modules = []
        
        # Extract module names from error message
        if "ModuleNotFoundError: No module named" in error_message:
            # Extract module name from error message
            import re
            matches = re.findall(r"No module named '([^']+)'", error_message)
            
            for module_name in matches:
                # Skip standard library modules
                if module_name in sys.modules or module_name.startswith("_"):
                    continue
                    
                # Install module
                if self.verbose:
                    logger.info(f"Installing module: {module_name}")
                    
                process = await asyncio.create_subprocess_exec(
                    sys.executable, "-m", "pip", "install", module_name,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                # Wait for process to complete
                stdout, stderr = await process.communicate()
                
                # Check if installation was successful
                if process.returncode == 0:
                    installed_modules.append(module_name)
                    if self.verbose:
                        logger.info(f"Successfully installed module: {module_name}")
                else:
                    if self.verbose:
                        logger.warning(f"Failed to install module: {module_name}")
                        logger.warning(stderr.decode("utf-8"))
                        
        return installed_modules

    def operator_review(self, code: str, output: str) -> bool:
        """
        Simulate operator review of code and output.
        
        Args:
            code: Generated code
            output: Output from code execution
            
        Returns:
            True if code is acceptable, False otherwise
        """
        # In a real system, this would prompt for user input
        # For now, we'll just return True
        return True

    async def recursive_build_async(self, mission: str, context: str = "") -> None:
        """
        Recursively build and refine code based on mission asynchronously.
        
        Args:
            mission: The task description for code generation
            context: Additional context from previous iterations
            
        Raises:
            OllamaAPIError: If API request fails
            CodeGenerationError: If code generation fails
            CodeExecutionError: If code execution fails
        """
        if self.verbose:
            logger.info(f"Starting recursive build for mission: {mission[:50]}{'...' if len(mission) > 50 else ''}")
            
        cycle = 0
        filename = "generated_code.py"
        
        while cycle < self.max_cycles:
            cycle += 1
            
            if self.verbose:
                logger.info(f"Cycle {cycle}/{self.max_cycles}")
                
            try:
                # Generate code
                code = await self.ollama_generate_async(mission, context)
                
                # Write and execute code
                success, output = await self.write_and_execute_async(code, filename)
                
                if success:
                    # Check if code is acceptable
                    if self.operator_review(code, output):
                        if self.verbose:
                            logger.info("Code accepted, ending recursive build")
                        break
                        
                    # Add output to context for next iteration
                    context += f"\nPrevious output:\n{output}\n"
                else:
                    # Add error to context for next iteration
                    context += f"\nPrevious error:\n{output}\n"
                    
            except (OllamaAPIError, CodeGenerationError, CodeExecutionError) as e:
                logger.error(f"Error in cycle {cycle}: {e}")
                # Add error to context for next iteration
                context += f"\nPrevious error:\n{str(e)}\n"
                
        if cycle >= self.max_cycles:
            logger.warning(f"Reached maximum cycles ({self.max_cycles})")
            
        # Save final context
        async with aiofiles.open(os.path.join(self.project_root, "context.txt"), "w", encoding="utf-8") as f:
            await f.write(context)
            
        if self.verbose:
            logger.info("Recursive build completed")


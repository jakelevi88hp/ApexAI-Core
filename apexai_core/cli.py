"""
Command-line interface for ApexAI-Core.

This module provides a command-line interface for the ApexAI-Core package.
"""

import os
import sys
import json
import argparse
import logging
import asyncio
from typing import List, Optional, Dict, Any

from apexai_core.agents import GODCodeAgentOllama, MultiModelAgent, AsyncAgent
from apexai_core.config import load_config
from apexai_core.utils import check_ollama_availability, list_available_models
from apexai_core.security import InputValidator, CodeSandbox

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="ApexAI-Core - AI automation stack for business operations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Common arguments
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Enable verbose output"
    )
    parser.add_argument(
        "--project-root", "-p", 
        type=str, 
        default=os.getenv("PROJECT_ROOT", "apex_auto_project"),
        help="Directory for storing generated modules"
    )
    parser.add_argument(
        "--max-cycles", "-m", 
        type=int, 
        default=int(os.getenv("MAX_CYCLES", "7")),
        help="Maximum recursive cycles for code generation"
    )
    parser.add_argument(
        "--ollama-base-url", 
        type=str, 
        default=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        help="Base URL for the Ollama API"
    )
    parser.add_argument(
        "--ollama-model", 
        type=str, 
        default=os.getenv("OLLAMA_MODEL", "codellama:instruct"),
        help="Model to use for code generation"
    )
    
    # Subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run a mission")
    run_parser.add_argument(
        "mission", 
        type=str, 
        help="The task description for code generation"
    )
    run_parser.add_argument(
        "--context", "-c", 
        type=str, 
        default="",
        help="Additional context for code generation"
    )
    run_parser.add_argument(
        "--model-type", "-t", 
        type=str, 
        choices=["auto", "code", "general"],
        default="auto",
        help="Model type to use (auto selects based on mission content)"
    )
    run_parser.add_argument(
        "--async", "-a",
        action="store_true",
        dest="use_async",
        help="Use asynchronous execution"
    )
    
    # GUI command
    gui_parser = subparsers.add_parser("gui", help="Launch the GUI")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate code without executing")
    generate_parser.add_argument(
        "mission", 
        type=str, 
        help="The task description for code generation"
    )
    generate_parser.add_argument(
        "--output", "-o", 
        type=str, 
        default="generated_code.py",
        help="Output file for generated code"
    )
    generate_parser.add_argument(
        "--async", "-a",
        action="store_true",
        dest="use_async",
        help="Use asynchronous execution"
    )
    
    # Models command
    models_parser = subparsers.add_parser("models", help="List available models")
    
    # Sandbox command
    sandbox_parser = subparsers.add_parser("sandbox", help="Execute code in a sandbox")
    sandbox_parser.add_argument(
        "file", 
        type=str, 
        help="Python file to execute in the sandbox"
    )
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")
    
    return parser.parse_args(args)


async def async_main(args: argparse.Namespace) -> int:
    """
    Asynchronous main entry point for the CLI.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        if args.command == "run" and args.use_async:
            # Set up environment variables
            os.environ["PROJECT_ROOT"] = args.project_root
            os.environ["MAX_CYCLES"] = str(args.max_cycles)
            os.environ["OLLAMA_BASE_URL"] = args.ollama_base_url
            
            # Validate mission
            valid, error = InputValidator.validate_mission(args.mission)
            if not valid:
                logger.error(f"Invalid mission: {error}")
                return 1
            
            # Create an AsyncAgent instance
            agent = AsyncAgent(
                project_root=args.project_root,
                max_cycles=args.max_cycles,
                verbose=args.verbose,
                ollama_base_url=args.ollama_base_url,
                ollama_model=args.ollama_model
            )
            
            # Run the mission
            await agent.recursive_build_async(args.mission, args.context)
            return 0
            
        elif args.command == "generate" and args.use_async:
            # Set up environment variables
            os.environ["OLLAMA_BASE_URL"] = args.ollama_base_url
            os.environ["OLLAMA_MODEL"] = args.ollama_model
            
            # Validate mission
            valid, error = InputValidator.validate_mission(args.mission)
            if not valid:
                logger.error(f"Invalid mission: {error}")
                return 1
            
            # Create an AsyncAgent instance
            agent = AsyncAgent(
                verbose=args.verbose,
                ollama_base_url=args.ollama_base_url,
                ollama_model=args.ollama_model
            )
            
            # Generate code
            code = await agent.ollama_generate_async(args.mission)
            
            # Write code to file
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(code)
                
            print(f"Generated code written to {args.output}")
            return 0
            
        else:
            # Fall back to synchronous execution
            return main_sync(args)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


def main_sync(args: argparse.Namespace) -> int:
    """
    Synchronous main entry point for the CLI.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        if args.command == "version":
            from apexai_core import __version__
            print(f"ApexAI-Core version {__version__}")
            return 0
            
        elif args.command == "models":
            # Check if Ollama is available
            if not check_ollama_availability(args.ollama_base_url):
                logger.error(f"Ollama not available at {args.ollama_base_url}")
                return 1
                
            # List available models
            try:
                models = list_available_models(args.ollama_base_url)
                print("Available models:")
                for model in models:
                    print(f"  - {model}")
                return 0
            except Exception as e:
                logger.error(f"Failed to list models: {e}")
                return 1
            
        elif args.command == "run" and not args.use_async:
            # Set up environment variables
            os.environ["PROJECT_ROOT"] = args.project_root
            os.environ["MAX_CYCLES"] = str(args.max_cycles)
            os.environ["OLLAMA_BASE_URL"] = args.ollama_base_url
            
            # Validate mission
            valid, error = InputValidator.validate_mission(args.mission)
            if not valid:
                logger.error(f"Invalid mission: {error}")
                return 1
            
            if args.model_type != "auto":
                # Use the specified model type
                if args.model_type == "code":
                    os.environ["OLLAMA_MODEL"] = "codellama:instruct"
                else:
                    os.environ["OLLAMA_MODEL"] = "llama2"
                
                # Create a GODCodeAgentOllama instance
                agent = GODCodeAgentOllama(
                    project_root=args.project_root,
                    max_cycles=args.max_cycles,
                    verbose=args.verbose,
                    ollama_base_url=args.ollama_base_url,
                    ollama_model=os.environ["OLLAMA_MODEL"]
                )
                
                # Run the mission
                agent.recursive_build(args.mission, args.context)
            else:
                # Use the MultiModelAgent for automatic model selection
                agent = MultiModelAgent(
                    project_root=args.project_root,
                    max_cycles=args.max_cycles,
                    verbose=args.verbose,
                    ollama_base_url=args.ollama_base_url
                )
                
                # Run the mission
                agent.run_mission(args.mission, args.context)
                
            return 0
            
        elif args.command == "gui":
            # Set up environment variables
            os.environ["PROJECT_ROOT"] = args.project_root
            os.environ["MAX_CYCLES"] = str(args.max_cycles)
            os.environ["OLLAMA_BASE_URL"] = args.ollama_base_url
            os.environ["OLLAMA_MODEL"] = args.ollama_model
            
            # Create a MultiModelAgent instance
            agent = MultiModelAgent(
                project_root=args.project_root,
                max_cycles=args.max_cycles,
                verbose=args.verbose,
                ollama_base_url=args.ollama_base_url
            )
            
            # Launch the GUI
            agent.launch_gui()
            return 0
            
        elif args.command == "generate" and not args.use_async:
            # Set up environment variables
            os.environ["OLLAMA_BASE_URL"] = args.ollama_base_url
            os.environ["OLLAMA_MODEL"] = args.ollama_model
            
            # Validate mission
            valid, error = InputValidator.validate_mission(args.mission)
            if not valid:
                logger.error(f"Invalid mission: {error}")
                return 1
            
            # Create a GODCodeAgentOllama instance
            agent = GODCodeAgentOllama(
                verbose=args.verbose,
                ollama_base_url=args.ollama_base_url,
                ollama_model=args.ollama_model
            )
            
            # Generate code
            code = agent.ollama_generate(args.mission)
            
            # Write code to file
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(code)
                
            print(f"Generated code written to {args.output}")
            return 0
            
        elif args.command == "sandbox":
            # Read the code from the file
            try:
                with open(args.file, "r", encoding="utf-8") as f:
                    code = f.read()
            except IOError as e:
                logger.error(f"Failed to read file {args.file}: {e}")
                return 1
                
            # Create a CodeSandbox instance
            sandbox = CodeSandbox()
            
            # Validate the code
            violations = sandbox.validate_code(code)
            if violations:
                logger.error(f"Security violations detected:")
                for violation in violations:
                    logger.error(f"  - {violation}")
                return 1
                
            # Execute the code
            success, output = sandbox.execute_code(code)
            if success:
                print(output)
                return 0
            else:
                logger.error(f"Execution failed: {output}")
                return 1
            
        else:
            # No command specified, show help
            parse_args(["--help"])
            return 1
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parsed_args = parse_args(args)
    
    # Check if we need to use async
    if (parsed_args.command == "run" or parsed_args.command == "generate") and getattr(parsed_args, "use_async", False):
        return asyncio.run(async_main(parsed_args))
    else:
        return main_sync(parsed_args)


if __name__ == "__main__":
    sys.exit(main())


"""
Command-line interface for ApexAI-Core.

This module provides a command-line interface for the ApexAI-Core package.
"""

import os
import sys
import argparse
import logging
from typing import List, Optional

from apexai_core.agents import GODCodeAgentOllama, MultiModelAgent

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
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parsed_args = parse_args(args)
    
    try:
        if parsed_args.command == "version":
            from apexai_core import __version__
            print(f"ApexAI-Core version {__version__}")
            return 0
            
        elif parsed_args.command == "run":
            # Set up environment variables
            os.environ["PROJECT_ROOT"] = parsed_args.project_root
            os.environ["MAX_CYCLES"] = str(parsed_args.max_cycles)
            os.environ["OLLAMA_BASE_URL"] = parsed_args.ollama_base_url
            
            if parsed_args.model_type != "auto":
                # Use the specified model type
                if parsed_args.model_type == "code":
                    os.environ["OLLAMA_MODEL"] = "codellama:instruct"
                else:
                    os.environ["OLLAMA_MODEL"] = "llama2"
                
                # Create a GODCodeAgentOllama instance
                agent = GODCodeAgentOllama(
                    project_root=parsed_args.project_root,
                    max_cycles=parsed_args.max_cycles,
                    verbose=parsed_args.verbose,
                    ollama_base_url=parsed_args.ollama_base_url,
                    ollama_model=os.environ["OLLAMA_MODEL"]
                )
                
                # Run the mission
                agent.recursive_build(parsed_args.mission, parsed_args.context)
            else:
                # Use the MultiModelAgent for automatic model selection
                agent = MultiModelAgent(
                    project_root=parsed_args.project_root,
                    max_cycles=parsed_args.max_cycles,
                    verbose=parsed_args.verbose,
                    ollama_base_url=parsed_args.ollama_base_url
                )
                
                # Run the mission
                agent.run_mission(parsed_args.mission, parsed_args.context)
                
            return 0
            
        elif parsed_args.command == "gui":
            # Set up environment variables
            os.environ["PROJECT_ROOT"] = parsed_args.project_root
            os.environ["MAX_CYCLES"] = str(parsed_args.max_cycles)
            os.environ["OLLAMA_BASE_URL"] = parsed_args.ollama_base_url
            os.environ["OLLAMA_MODEL"] = parsed_args.ollama_model
            
            # Create a MultiModelAgent instance
            agent = MultiModelAgent(
                project_root=parsed_args.project_root,
                max_cycles=parsed_args.max_cycles,
                verbose=parsed_args.verbose,
                ollama_base_url=parsed_args.ollama_base_url
            )
            
            # Launch the GUI
            agent.launch_gui()
            return 0
            
        elif parsed_args.command == "generate":
            # Set up environment variables
            os.environ["OLLAMA_BASE_URL"] = parsed_args.ollama_base_url
            os.environ["OLLAMA_MODEL"] = parsed_args.ollama_model
            
            # Create a GODCodeAgentOllama instance
            agent = GODCodeAgentOllama(
                verbose=parsed_args.verbose,
                ollama_base_url=parsed_args.ollama_base_url,
                ollama_model=parsed_args.ollama_model
            )
            
            # Generate code
            code = agent.ollama_generate(parsed_args.mission)
            
            # Write code to file
            with open(parsed_args.output, "w", encoding="utf-8") as f:
                f.write(code)
                
            print(f"Generated code written to {parsed_args.output}")
            return 0
            
        else:
            # No command specified, show help
            parse_args(["--help"])
            return 1
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


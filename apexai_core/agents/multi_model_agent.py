"""
MultiModelAgent - A wrapper for GODCodeAgentOllama that supports multiple models and provides a GUI.

This module extends the functionality of GODCodeAgentOllama by adding model selection
based on mission content and a simple GUI interface for user interaction.
"""

import os
import sys
import subprocess
import logging
import traceback
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, List, Tuple, Optional, Any, Union
import threading
import signal

from apexai_core.agents.god_code_agent import GODCodeAgentOllama, OllamaAPIError, CodeGenerationError, CodeExecutionError

# Configure logging if not already configured
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join(os.path.dirname(__file__), 'multi_model_agent.log'))
        ]
    )
logger = logging.getLogger(__name__)


class ModelSelectionError(Exception):
    """Exception raised for errors in model selection."""
    pass


class MultiModelAgent:
    """
    Agent that selects between multiple Ollama models and provides a GUI.
    
    This class wraps the GODCodeAgentOllama to provide model selection based on
    mission content and a simple GUI for interacting with the agent.
    
    Attributes:
        models (Dict[str, str]): Dictionary mapping model types to model names
        agent (GODCodeAgentOllama): The underlying code generation agent
        verbose (bool): Whether to enable verbose logging
    """

    def __init__(
        self, 
        models: Optional[Dict[str, str]] = None, 
        project_root: Optional[str] = None, 
        max_cycles: Optional[int] = None, 
        verbose: bool = True,
        ollama_base_url: Optional[str] = None
    ):
        """
        Initialize the MultiModelAgent.
        
        Args:
            models: Dictionary mapping model types to model names
            project_root: Directory for storing generated modules
            max_cycles: Maximum recursive cycles for code generation
            verbose: Enable verbose output logging
            ollama_base_url: Base URL for the Ollama API
        """
        try:
            self.models = models or {
                "code": "codellama:instruct",
                "general": "llama2",
            }
            self.agent = GODCodeAgentOllama(
                project_root=project_root, 
                max_cycles=max_cycles, 
                verbose=verbose,
                ollama_base_url=ollama_base_url
            )
            self.verbose = verbose
            logger.info("MultiModelAgent initialized successfully")
            
            if self.verbose:
                logger.info(f"Available models: {', '.join(self.models.values())}")
                
        except Exception as e:
            logger.error(f"Failed to initialize MultiModelAgent: {e}")
            logger.debug(traceback.format_exc())
            raise

    def choose_model(self, mission: str) -> str:
        """
        Choose a model based on mission content using keyword detection.
        
        Args:
            mission: The mission text to analyze
            
        Returns:
            The name of the selected model
            
        Raises:
            ModelSelectionError: If model selection fails
        """
        try:
            mission_lower = mission.lower()
            
            # Keywords that suggest code-related tasks
            code_keywords = ("code", "script", "api", "function", "class", 
                            "data", "csv", "json", "algorithm", "program")
                            
            if any(word in mission_lower for word in code_keywords):
                selected_model = self.models.get("code", self.models["general"])
                logger.debug(f"Selected code model: {selected_model} based on mission keywords")
                return selected_model
                
            # Default to general model
            logger.debug(f"Selected general model: {self.models['general']} (no code keywords found)")
            return self.models["general"]
            
        except Exception as e:
            logger.error(f"Error in model selection: {e}")
            logger.debug(traceback.format_exc())
            raise ModelSelectionError(f"Failed to select model: {e}")

    def run_mission(self, mission: str, context: str = "") -> None:
        """
        Run a mission using the automatically chosen model.
        
        Args:
            mission: The task description for code generation
            context: Additional context from previous iterations
            
        Raises:
            ValueError: If mission is empty
            ModelSelectionError: If model selection fails
            OllamaAPIError: If API request fails
            CodeGenerationError: If code generation fails
            CodeExecutionError: If code execution fails
        """
        if not mission:
            logger.warning("Empty mission provided, aborting")
            raise ValueError("Mission cannot be empty")
            
        try:
            logger.info(f"Starting mission: {mission[:50]}{'...' if len(mission) > 50 else ''}")
            
            # Select appropriate model
            model = self.choose_model(mission)
            os.environ["OLLAMA_MODEL"] = model
            logger.info(f"Using model: {model}")
            
            # Run the mission
            self.agent.recursive_build(mission, context)
            logger.info("Mission completed successfully")
            
        except (ModelSelectionError, OllamaAPIError, CodeGenerationError, CodeExecutionError) as e:
            logger.error(f"Mission failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in mission: {e}")
            logger.debug(traceback.format_exc())
            raise

    def self_update(self) -> bool:
        """
        Pull the latest code from the current git repository.
        
        Returns:
            True if update was successful, False otherwise
        """
        logger.info("Attempting self-update from git repository")
        try:
            result = subprocess.run(
                ["git", "pull"],
                check=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if "Already up to date" in result.stdout:
                logger.info("Repository already up to date")
                return True
                
            logger.info(f"Repository updated successfully: {result.stdout.strip()}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git pull failed: {e.stderr}")
            return False
        except subprocess.TimeoutExpired:
            logger.error("Git pull timed out after 30 seconds")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during self-update: {e}")
            logger.debug(traceback.format_exc())
            return False

    def generate_improvement(self, mission: str) -> str:
        """
        Generate code improvements using the active model.
        
        Args:
            mission: Description of the improvement to make
            
        Returns:
            Generated improvement code
            
        Raises:
            OllamaAPIError: If API request fails
            CodeGenerationError: If code generation fails
        """
        try:
            logger.info(f"Generating improvement for: {mission[:50]}{'...' if len(mission) > 50 else ''}")
            improvement = self.agent.ollama_generate(f"Improve the agent code: {mission}")
            return improvement
        except (OllamaAPIError, CodeGenerationError) as e:
            logger.error(f"Failed to generate improvement: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate_improvement: {e}")
            logger.debug(traceback.format_exc())
            raise CodeGenerationError(f"Unexpected error: {e}")

    def launch_gui(self) -> None:
        """
        Launch a Tkinter GUI with controls for mission execution and self-update.
        
        Raises:
            RuntimeError: If GUI initialization fails
        """
        try:
            logger.info("Launching MultiModelAgent GUI")
            root = tk.Tk()
            root.title("Apex MultiModelAgent")
            root.geometry("600x400")
            
            # Set up variables
            mission_var = tk.StringVar()
            status_var = tk.StringVar(value="Ready")
            
            # Create main frame
            main_frame = ttk.Frame(root, padding=10)
            main_frame.pack(fill="both", expand=True)
            
            # Mission input section
            input_frame = ttk.LabelFrame(main_frame, text="Mission", padding=5)
            input_frame.pack(fill="x", pady=5)
            
            ttk.Label(input_frame, text="Enter mission description:").pack(anchor="w")
            mission_entry = ttk.Entry(input_frame, textvariable=mission_var, width=50)
            mission_entry.pack(fill="x", pady=5)
            mission_entry.focus()
            
            # Log output section
            log_frame = ttk.LabelFrame(main_frame, text="Output Log", padding=5)
            log_frame.pack(fill="both", expand=True, pady=5)
            
            log_text = scrolledtext.ScrolledText(log_frame, height=10)
            log_text.pack(fill="both", expand=True)
            
            # Custom log handler to display logs in the GUI
            class TextHandler(logging.Handler):
                def emit(self, record):
                    msg = self.format(record)
                    log_text.configure(state='normal')
                    log_text.insert(tk.END, msg + '\n')
                    log_text.see(tk.END)
                    log_text.configure(state='disabled')
                    
            # Add the custom handler to the logger
            text_handler = TextHandler()
            text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logging.getLogger().addHandler(text_handler)
            
            # Button actions
            def run_action():
                mission = mission_var.get()
                if not mission:
                    messagebox.showerror("Error", "Mission is required")
                    return
                    
                status_var.set("Running mission...")
                try:
                    # Run in a separate thread to avoid freezing the GUI
                    thread = threading.Thread(target=lambda: self._run_mission_thread(mission))
                    thread.daemon = True
                    thread.start()
                    status_var.set("Mission started")
                except Exception as e:
                    status_var.set("Mission failed")
                    logger.error(f"Error running mission: {e}")
                    messagebox.showerror("Error", f"Failed to run mission: {e}")
            
            def update_action():
                status_var.set("Updating...")
                if self.self_update():
                    status_var.set("Update successful")
                    messagebox.showinfo("Success", "Repository updated successfully")
                else:
                    status_var.set("Update failed")
                    messagebox.showerror("Error", "Failed to update repository")
            
            # Button section
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill="x", pady=5)
            
            ttk.Button(button_frame, text="Run Mission", command=run_action).pack(side="left", padx=5)
            ttk.Button(button_frame, text="Self Update", command=update_action).pack(side="left", padx=5)
            ttk.Button(button_frame, text="Exit", command=root.destroy).pack(side="right", padx=5)
            
            # Status bar
            status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
            status_bar.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Handle window close
            def on_closing():
                logger.info("GUI closed by user")
                root.destroy()
                
            root.protocol("WM_DELETE_WINDOW", on_closing)
            
            # Bind Enter key to run mission
            def on_enter(event):
                run_action()
            
            mission_entry.bind("<Return>", on_enter)
            
            # Handle keyboard interrupts gracefully
            def signal_handler(sig, frame):
                logger.info("Received keyboard interrupt, shutting down gracefully")
                root.destroy()
                sys.exit(0)
                
            # Register signal handler for SIGINT (Ctrl+C)
            signal.signal(signal.SIGINT, signal_handler)
            
            # Add periodic check for interrupts
            def check_interrupts():
                root.after(100, check_interrupts)
                
            root.after(100, check_interrupts)
            
            # Start the main loop
            logger.info("GUI initialized and ready")
            
            try:
                root.mainloop()
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received, shutting down")
                root.destroy()
            except Exception as e:
                logger.error(f"Error in GUI mainloop: {e}")
                logger.debug(traceback.format_exc())
                root.destroy()
                raise
            
        except Exception as e:
            logger.error(f"Error in GUI: {e}")
            logger.debug(traceback.format_exc())
            messagebox.showerror("Fatal Error", f"GUI initialization failed: {e}")
            raise RuntimeError(f"GUI initialization failed: {e}")
    
    def _run_mission_thread(self, mission: str) -> None:
        """
        Run a mission in a separate thread for the GUI.
        
        Args:
            mission: The task description for code generation
        """
        try:
            self.run_mission(mission)
        except Exception as e:
            logger.error(f"Mission thread failed: {e}")
            # We can't show a messagebox here because it's in a separate thread
            # The error is already logged


import os
import subprocess
import logging
import tkinter as tk
from tkinter import ttk, messagebox

from god_code_agent_ollama import GODCodeAgentOllama


class MultiModelAgent:
    """Agent that selects between multiple Ollama models and provides a GUI."""

    def __init__(self, models=None, project_root=None, max_cycles=None, verbose=True):
        self.models = models or {
            "code": "codellama:instruct",
            "general": "llama2",
        }
        self.agent = GODCodeAgentOllama(project_root, max_cycles, verbose)
        self.verbose = verbose

    def choose_model(self, mission: str) -> str:
        """Choose a model based on simple keyword detection."""
        mission_lower = mission.lower()
        if any(word in mission_lower for word in ("code", "script", "api", "data", "csv")):
            return self.models.get("code", self.models["general"])
        return self.models["general"]

    def run_mission(self, mission: str, context: str = "") -> None:
        """Run a mission using the chosen model."""
        model = self.choose_model(mission)
        os.environ["OLLAMA_MODEL"] = model
        if self.verbose:
            logging.info(f"Using model: {model}")
        self.agent.recursive_build(mission, context)

    def self_update(self) -> None:
        """Pull the latest code from the current git repository."""
        try:
            subprocess.run(
                ["git", "pull"],
                check=True,
                capture_output=True,
                text=True
            )
            logging.info("Repository updated successfully")
        except subprocess.CalledProcessError as e:
            logging.error(f"Update failed: {e.stderr}")

    def generate_improvement(self, mission: str) -> str:
        """Generate code improvements using the active model."""
        return self.agent.ollama_generate(f"Improve the agent code: {mission}")

    def launch_gui(self) -> None:
        """Launch a simple Tkinter GUI with basic controls."""
        root = tk.Tk()
        root.title("MultiModelAgent")
        root.geometry("400x200")

        mission_var = tk.StringVar()

        frame = ttk.Frame(root, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Mission:").pack(anchor="w")
        ttk.Entry(frame, textvariable=mission_var).pack(fill="x")

        def run():
            mission = mission_var.get()
            if not mission:
                messagebox.showerror("Error", "Mission is required")
                return
            self.run_mission(mission)

        ttk.Button(frame, text="Run Mission", command=run).pack(fill="x", pady=5)
        ttk.Button(frame, text="Self Update", command=self.self_update).pack(fill="x", pady=5)
        ttk.Button(frame, text="Exit", command=root.destroy).pack(fill="x", pady=5)

        root.mainloop()


if __name__ == "__main__":
    agent = MultiModelAgent()
    agent.launch_gui()

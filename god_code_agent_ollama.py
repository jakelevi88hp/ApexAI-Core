import os
import requests
import subprocess
import sys
import re

# === CONFIG ===
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "codellama:instruct"

class GODCodeAgentOllama:
    def __init__(self, project_root="apex_auto_project", max_cycles=7, verbose=True):
        self.project_root = project_root
        self.max_cycles = max_cycles
        self.verbose = verbose
        if not os.path.exists(project_root):
            os.makedirs(project_root)

    def ollama_generate(self, mission, context=""):
        prompt = (
            f"Write a single, fully working Python script for the following task. "
            f"Output only valid, executable code—no markdown, no explanations, no '[PYTHON]' tokens, no ellipses. "
            f"If you cannot solve the task, output: print('Hello world from GODCodeAgent').\n"
            f"Task: {mission}\n"
            f"Context/output: {context}\n"
        )
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
        )
        raw = response.json()['response']

        # Remove markdown, ellipses, [PYTHON] tokens, etc.
        for bad_token in ["```python", "```", "[PYTHON]", "[/PYTHON]", "..."]:
            raw = raw.replace(bad_token, "")
        raw = raw.strip()

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
        lines = raw.splitlines()
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
            code = "print('Hello world from GODCodeAgent')"
        return code

    def operator_review(self, code, filename):
        return any(word in code for word in ["def ", "class ", "print(", "FastAPI"])

    def destroyer_prune(self, file_path):
        try:
            os.remove(file_path)
            if self.verbose:
                print(f"Destroyed broken file: {file_path}")
        except Exception as e:
            if self.verbose:
                print(f"Failed to destroy file: {file_path}. Reason: {e}")

    def auto_install_module(self, error_output):
        matches = re.findall(r"No module named '([\w_]+)'", error_output)
        for module in matches:
            if self.verbose:
                print(f"Auto-installing missing module: {module}")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", module], check=True)
            except Exception as e:
                if self.verbose:
                    print(f"Failed to auto-install module: {module}. Reason: {e}")

    def should_run_with_uvicorn(self, code, file_path):
        return ("FastAPI" in code or "uvicorn" in code) and ("app = FastAPI()" in code)

    def write_and_execute(self, code, file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            if self.should_run_with_uvicorn(code, file_path):
                module_name = os.path.splitext(os.path.basename(file_path))[0]
                if self.verbose:
                    print(f"Detected FastAPI app, running with uvicorn: {module_name}:app")
                try:
                    completed = subprocess.run(
                        ["uvicorn", f"{module_name}:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
                        check=True,
                        capture_output=True,
                        text=True,
                        timeout=20
                    )
                    # If the server exits by itself, that's abnormal (usually a crash)
                    return True, completed.stdout
                except subprocess.TimeoutExpired:
                    if self.verbose:
                        print(f"Uvicorn server launched and is running at http://localhost:8000 (timed out waiting for manual shutdown)")
                    return True, "Uvicorn server running—manual test at http://localhost:8000"
                except Exception as e:
                    if self.verbose:
                        print(f"Uvicorn run failed: {e}")
                    return False, str(e)
            else:
                completed = subprocess.run(
                    ["python", file_path],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                return True, completed.stdout
        except subprocess.CalledProcessError as e:
            if self.verbose:
                print(f"Execution error in {file_path}: {e.stderr}")
            if "ModuleNotFoundError" in e.stderr:
                self.auto_install_module(e.stderr)
                try:
                    if self.should_run_with_uvicorn(code, file_path):
                        module_name = os.path.splitext(os.path.basename(file_path))[0]
                        completed = subprocess.run(
                            ["uvicorn", f"{module_name}:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
                            check=True,
                            capture_output=True,
                            text=True,
                            timeout=20
                        )
                        return True, completed.stdout
                    else:
                        completed = subprocess.run(
                            ["python", file_path],
                            check=True,
                            capture_output=True,
                            text=True,
                            timeout=60
                        )
                        return True, completed.stdout
                except subprocess.TimeoutExpired:
                    if self.verbose:
                        print(f"Uvicorn server launched and is running at http://localhost:8000 (timed out waiting for manual shutdown)")
                    return True, "Uvicorn server running—manual test at http://localhost:8000"
                except Exception as e2:
                    if self.verbose:
                        print(f"Second execution failed: {e2}")
                    return False, str(e2)
            return False, e.stderr
        except Exception as e:
            if self.verbose:
                print(f"General execution error in {file_path}: {e}")
            return False, str(e)

    def recursive_build(self, mission, context="", cycle=1):
        if cycle > self.max_cycles:
            print("Max recursion reached. Stopping.")
            return

        filename = f"module_{cycle}.py"
        file_path = os.path.join(self.project_root, filename)

        if self.verbose:
            print(f"\n=== CYCLE {cycle}: GENERATOR ===")
        code = self.ollama_generate(mission, context)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        if self.verbose:
            print(f"Code generated for {filename}:\n{code[:300]}...\n")

        if self.verbose:
            print(f"=== CYCLE {cycle}: OPERATOR ===")
        success, output = self.write_and_execute(code, file_path)
        if self.operator_review(code, filename) and success:
            if self.verbose:
                print(f"Execution output: {output[:300]}...\n")
            if cycle < self.max_cycles:
                next_mission = f"Expand, optimize, or add new required modules to complete: {mission}"
                self.recursive_build(next_mission, output, cycle + 1)
        else:
            if self.verbose:
                print(f"=== CYCLE {cycle}: DESTROYER (Failed Review or Execution) ===")
                print(f"\nFAILED CODE:\n{code}\n")
                print(f"\nERROR OUTPUT:\n{output}\n")
            self.destroyer_prune(file_path)

# --- USAGE EXAMPLE ---
if __name__ == "__main__":
    mission = "Build a FastAPI server with a '/status' endpoint and a '/execute' endpoint that takes code and returns execution result."
    agent = GODCodeAgentOllama(max_cycles=4, verbose=True)
    agent.recursive_build(mission)
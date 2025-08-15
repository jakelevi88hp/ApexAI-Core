"""
Wrapper script for backward compatibility with the old GODCodeAgentOllama class.

This script provides a wrapper for the new GODCodeAgentOllama class to maintain
backward compatibility with existing code.
"""

import os
import sys
import logging
from apexai_core.agents import GODCodeAgentOllama

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Print deprecation warning
logger.warning(
    "The god_code_agent_ollama.py script is deprecated and will be removed in a future version. "
    "Please use the new apexai_core package instead."
)

# Re-export the GODCodeAgentOllama class
if __name__ == "__main__":
    # Run the same mission as the original script
    mission = "Build a FastAPI server with a '/status' endpoint and a '/execute' endpoint that takes code and returns execution result."
    agent = GODCodeAgentOllama(max_cycles=4, verbose=True)
    agent.recursive_build(mission)


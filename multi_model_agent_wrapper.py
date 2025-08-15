"""
Wrapper script for backward compatibility with the old MultiModelAgent class.

This script provides a wrapper for the new MultiModelAgent class to maintain
backward compatibility with existing code.
"""

import os
import sys
import logging
from apexai_core.agents import MultiModelAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Print deprecation warning
logger.warning(
    "The multi_model_agent.py script is deprecated and will be removed in a future version. "
    "Please use the new apexai_core package instead."
)

# Re-export the MultiModelAgent class
if __name__ == "__main__":
    try:
        logger.info("Starting MultiModelAgent application")
        agent = MultiModelAgent()
        agent.launch_gui()
    except Exception as e:
        logger.critical(f"Application failed to start: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)


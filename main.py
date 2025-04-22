#!/usr/bin/env python3
"""
AGI Dashboard Generator - Main Application

This is the main entry point for the AGI Dashboard Generator application.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AGI-Dashboard-Generator')

# Add the current directory to the path to fix import issues
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import after path adjustment
from dashboard_ui import DashboardApp

def main():
    """Main entry point for the application."""
    logger.info("Starting AGI Dashboard Generator")
    
    # Create and run the application
    app = DashboardApp()
    app.mainloop()
    
    logger.info("AGI Dashboard Generator closed")

if __name__ == "__main__":
    main()

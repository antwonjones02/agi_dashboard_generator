#!/usr/bin/env python3
"""
AGI Dashboard Generator - Main Application

This is the main entry point for the AGI Dashboard Generator application.
"""

import os
import sys
import logging

# Add parent directory to path to import other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.dashboard_ui import DashboardApp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AGI-Dashboard-Generator')

def main():
    """Main entry point for the application."""
    logger.info("Starting AGI Dashboard Generator")
    
    # Create and run the application
    app = DashboardApp()
    app.mainloop()
    
    logger.info("AGI Dashboard Generator closed")

if __name__ == "__main__":
    main()

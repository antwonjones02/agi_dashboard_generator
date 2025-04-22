#!/usr/bin/env python3
"""
AGI Dashboard Generator - File Monitoring System

This module provides functionality to monitor a folder for new or updated report files
(Excel, CSV, PDF) and trigger processing when changes are detected.
"""

import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AGI-Dashboard-Generator')

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    'excel': ['.xlsx', '.xls'],
    'csv': ['.csv'],
    'pdf': ['.pdf']
}

class ReportFileHandler(FileSystemEventHandler):
    """
    Handler for file system events related to report files.
    """
    
    def __init__(self, callback=None):
        """
        Initialize the handler with an optional callback function.
        
        Args:
            callback: Function to call when a report file is created or modified
        """
        self.callback = callback
        self.processing_queue = set()
        logger.info("Report file handler initialized")
    
    def is_valid_report(self, file_path):
        """
        Check if the file is a supported report type.
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: True if the file is a supported report type, False otherwise
        """
        ext = os.path.splitext(file_path)[1].lower()
        for file_type, extensions in SUPPORTED_EXTENSIONS.items():
            if ext in extensions:
                return True
        return False
    
    def get_file_type(self, file_path):
        """
        Determine the type of report file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: Type of report file ('excel', 'csv', 'pdf') or None if not supported
        """
        ext = os.path.splitext(file_path)[1].lower()
        for file_type, extensions in SUPPORTED_EXTENSIONS.items():
            if ext in extensions:
                return file_type
        return None
    
    def on_created(self, event):
        """
        Handle file creation events.
        
        Args:
            event: File system event
        """
        if not event.is_directory and self.is_valid_report(event.src_path):
            file_path = event.src_path
            file_type = self.get_file_type(file_path)
            logger.info(f"New {file_type} report detected: {file_path}")
            
            # Add to processing queue
            self.processing_queue.add(file_path)
            
            # Call the callback function if provided
            if self.callback:
                self.callback(file_path, file_type, 'created')
    
    def on_modified(self, event):
        """
        Handle file modification events.
        
        Args:
            event: File system event
        """
        if not event.is_directory and self.is_valid_report(event.src_path):
            file_path = event.src_path
            file_type = self.get_file_type(file_path)
            
            # Only process if not already in queue (avoid duplicate processing)
            if file_path not in self.processing_queue:
                logger.info(f"Modified {file_type} report detected: {file_path}")
                self.processing_queue.add(file_path)
                
                # Call the callback function if provided
                if self.callback:
                    self.callback(file_path, file_type, 'modified')
    
    def on_moved(self, event):
        """
        Handle file move events.
        
        Args:
            event: File system event
        """
        if not event.is_directory and self.is_valid_report(event.dest_path):
            file_path = event.dest_path
            file_type = self.get_file_type(file_path)
            logger.info(f"Moved {file_type} report detected: {file_path}")
            
            # Add to processing queue
            self.processing_queue.add(file_path)
            
            # Call the callback function if provided
            if self.callback:
                self.callback(file_path, file_type, 'moved')
    
    def process_complete(self, file_path):
        """
        Mark a file as processed and remove from the queue.
        
        Args:
            file_path: Path to the processed file
        """
        if file_path in self.processing_queue:
            self.processing_queue.remove(file_path)
            logger.info(f"Processing complete for: {file_path}")


class FolderMonitor:
    """
    Monitor a folder for report files and trigger processing when changes are detected.
    """
    
    def __init__(self, folder_path=None, callback=None):
        """
        Initialize the folder monitor.
        
        Args:
            folder_path: Path to the folder to monitor
            callback: Function to call when a report file is created or modified
        """
        self.folder_path = folder_path
        self.callback = callback
        self.observer = None
        self.handler = None
        logger.info(f"Folder monitor initialized for: {folder_path if folder_path else 'Not set'}")
    
    def set_folder(self, folder_path):
        """
        Set the folder to monitor.
        
        Args:
            folder_path: Path to the folder to monitor
        """
        self.folder_path = folder_path
        logger.info(f"Monitoring folder set to: {folder_path}")
    
    def set_callback(self, callback):
        """
        Set the callback function.
        
        Args:
            callback: Function to call when a report file is created or modified
        """
        self.callback = callback
        if self.handler:
            self.handler.callback = callback
    
    def start_monitoring(self):
        """
        Start monitoring the folder for changes.
        
        Returns:
            bool: True if monitoring started successfully, False otherwise
        """
        if not self.folder_path:
            logger.error("No folder path specified")
            return False
        
        if not os.path.exists(self.folder_path):
            logger.error(f"Folder does not exist: {self.folder_path}")
            return False
        
        # Create a new observer and handler
        self.observer = Observer()
        self.handler = ReportFileHandler(self.callback)
        
        # Schedule the handler
        self.observer.schedule(self.handler, self.folder_path, recursive=True)
        
        # Start the observer
        self.observer.start()
        logger.info(f"Started monitoring folder: {self.folder_path}")
        
        # Process existing files in the folder
        self._process_existing_files()
        
        return True
    
    def _process_existing_files(self):
        """
        Process existing report files in the monitored folder.
        """
        if not self.folder_path or not self.callback:
            return
        
        logger.info(f"Scanning for existing report files in: {self.folder_path}")
        
        # Get all files in the folder
        for root, _, files in os.walk(self.folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if self.handler.is_valid_report(file_path):
                    file_type = self.handler.get_file_type(file_path)
                    logger.info(f"Found existing {file_type} report: {file_path}")
                    
                    # Call the callback function
                    self.callback(file_path, file_type, 'existing')
    
    def stop_monitoring(self):
        """
        Stop monitoring the folder.
        """
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info(f"Stopped monitoring folder: {self.folder_path}")
            self.observer = None
            self.handler = None
    
    def is_monitoring(self):
        """
        Check if the folder is being monitored.
        
        Returns:
            bool: True if monitoring, False otherwise
        """
        return self.observer is not None and self.observer.is_alive()


def process_report_file(file_path, file_type, event_type):
    """
    Example callback function for processing report files.
    
    Args:
        file_path: Path to the report file
        file_type: Type of report file ('excel', 'csv', 'pdf')
        event_type: Type of event ('created', 'modified', 'moved', 'existing')
    """
    logger.info(f"Processing {file_type} report: {file_path} (Event: {event_type})")
    # This would be replaced with actual processing logic
    # For example, calling data extraction and analysis functions


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        folder_to_monitor = sys.argv[1]
    else:
        folder_to_monitor = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    
    print(f"Starting folder monitor for: {folder_to_monitor}")
    
    # Create and start the folder monitor
    monitor = FolderMonitor(folder_to_monitor, process_report_file)
    monitor.start_monitoring()
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop monitoring when Ctrl+C is pressed
        monitor.stop_monitoring()
        print("Monitoring stopped")

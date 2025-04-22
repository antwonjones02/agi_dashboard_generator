#!/usr/bin/env python3
"""
AGI Dashboard Generator - User Interface

This module provides a modern, professional user interface for the AGI Dashboard Generator,
allowing users to select folders, configure options, and view generated dashboards.
"""

import os
import sys
import json
import time
import threading
import webbrowser
from pathlib import Path
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import base64
from io import BytesIO

# Add parent directory to path to import other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.file_monitor import FolderMonitor
from src.data_analyzer import DataExtractor, DataAnalyzer, process_report_file
from src.visualization_generator import VisualizationGenerator
from src.openai_analyzer import OpenAIAnalyzer, enhance_analysis_with_openai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AGI-Dashboard-Generator')

# Define color scheme for professional UI
UI_COLORS = {
    'primary': '#0072B2',      # Blue - primary color
    'secondary': '#D55E00',    # Orange - secondary color
    'accent': '#009E73',       # Green - accent color
    'background': '#F8F9FA',   # Light gray - background
    'text': '#212529',         # Dark gray - text
    'light_text': '#6C757D',   # Medium gray - secondary text
    'border': '#DEE2E6',       # Light gray - borders
    'hover': '#E9ECEF',        # Slightly darker gray - hover states
    'success': '#28A745',      # Green - success messages
    'warning': '#FFC107',      # Yellow - warning messages
    'error': '#DC3545'         # Red - error messages
}

class DashboardApp(tk.Tk):
    """
    Main application window for the AGI Dashboard Generator.
    """
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        # Set window properties
        self.title("AGI Dashboard Generator")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        self.configure(bg=UI_COLORS['background'])
        
        # Set application icon
        # self.iconbitmap('path/to/icon.ico')  # Uncomment and set path to icon if available
        
        # Initialize variables
        self.folder_path = tk.StringVar()
        self.monitor_enabled = tk.BooleanVar(value=True)
        self.excel_enabled = tk.BooleanVar(value=True)
        self.csv_enabled = tk.BooleanVar(value=True)
        self.pdf_enabled = tk.BooleanVar(value=True)
        self.analysis_depth = tk.StringVar(value="Standard")
        self.visualization_style = tk.StringVar(value="hbr")
        self.status_text = tk.StringVar(value="Ready")
        self.openai_api_key = tk.StringVar()
        self.openai_enabled = tk.BooleanVar(value=False)
        self.current_dashboard = None
        self.dashboard_list = []
        self.folder_monitor = None
        self.monitor_thread = None
        
        # Create UI elements
        self._create_menu()
        self._create_main_frame()
        
        # Initialize folder monitor
        self._initialize_folder_monitor()
        
        # Set up protocol for window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        logger.info("Dashboard application initialized")
    
    def _create_menu(self):
        """Create the application menu."""
        menubar = tk.Menu(self)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Select Folder", command=self._browse_folder)
        file_menu.add_command(label="Analyze Reports", command=self._analyze_reports)
        file_menu.add_separator()
        file_menu.add_command(label="Export Current Dashboard to CSV", command=self._export_to_csv)
        file_menu.add_command(label="Export Current Dashboard to PDF", command=self._export_to_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Refresh Dashboards", command=self._refresh_dashboards)
        view_menu.add_separator()
        
        # Visualization style submenu
        style_menu = tk.Menu(view_menu, tearoff=0)
        style_menu.add_radiobutton(label="Harvard Business Review", variable=self.visualization_style, value="hbr", command=self._change_visualization_style)
        style_menu.add_radiobutton(label="New York Times", variable=self.visualization_style, value="nyt", command=self._change_visualization_style)
        view_menu.add_cascade(label="Visualization Style", menu=style_menu)
        
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self._show_documentation)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menubar)
    
    def _create_main_frame(self):
        """Create the main application frame."""
        # Create main container with padding
        main_container = ttk.Frame(self, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create top frame for folder selection and options
        top_frame = ttk.Frame(main_container)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Folder selection
        folder_label = ttk.Label(top_frame, text="Reports Folder:")
        folder_label.pack(side=tk.LEFT, padx=(0, 5))
        
        folder_entry = ttk.Entry(top_frame, textvariable=self.folder_path, width=50)
        folder_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        browse_button = ttk.Button(top_frame, text="Browse...", command=self._browse_folder)
        browse_button.pack(side=tk.LEFT, padx=(0, 10))
        
        analyze_button = ttk.Button(top_frame, text="Analyze Reports", command=self._analyze_reports)
        analyze_button.pack(side=tk.LEFT)
        
        # Create options frame
        options_frame = ttk.LabelFrame(main_container, text="Configuration Options")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File types options
        file_types_frame = ttk.Frame(options_frame)
        file_types_frame.pack(fill=tk.X, padx=10, pady=5)
        
        file_types_label = ttk.Label(file_types_frame, text="File Types:")
        file_types_label.pack(side=tk.LEFT, padx=(0, 10))
        
        excel_check = ttk.Checkbutton(file_types_frame, text="Excel", variable=self.excel_enabled)
        excel_check.pack(side=tk.LEFT, padx=(0, 5))
        
        csv_check = ttk.Checkbutton(file_types_frame, text="CSV", variable=self.csv_enabled)
        csv_check.pack(side=tk.LEFT, padx=(0, 5))
        
        pdf_check = ttk.Checkbutton(file_types_frame, text="PDF", variable=self.pdf_enabled)
        pdf_check.pack(side=tk.LEFT, padx=(0, 5))
        
        # Analysis depth options
        analysis_frame = ttk.Frame(options_frame)
        analysis_frame.pack(fill=tk.X, padx=10, pady=5)
        
        analysis_label = ttk.Label(analysis_frame, text="Analysis Depth:")
        analysis_label.pack(side=tk.LEFT, padx=(0, 10))
        
        analysis_combo = ttk.Combobox(analysis_frame, textvariable=self.analysis_depth, 
                                      values=["Basic", "Standard", "Advanced"], state="readonly", width=15)
        analysis_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # Folder monitoring option
        monitor_check = ttk.Checkbutton(analysis_frame, text="Enable Folder Monitoring", variable=self.monitor_enabled)
        monitor_check.pack(side=tk.LEFT)
        
        # OpenAI integration options
        openai_frame = ttk.Frame(options_frame)
        openai_frame.pack(fill=tk.X, padx=10, pady=5)
        
        openai_check = ttk.Checkbutton(openai_frame, text="Enable OpenAI Analysis", variable=self.openai_enabled)
        openai_check.pack(side=tk.LEFT, padx=(0, 10))
        
        openai_label = ttk.Label(openai_frame, text="OpenAI API Key:")
        openai_label.pack(side=tk.LEFT, padx=(0, 5))
        
        openai_entry = ttk.Entry(openai_frame, textvariable=self.openai_api_key, width=40, show="*")
        openai_entry.pack(side=tk.LEFT)
        
        # Create main content frame with notebook for dashboards
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a PanedWindow to divide dashboard list and dashboard content
        paned_window = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for dashboard list
        left_panel = ttk.Frame(paned_window, width=250)
        paned_window.add(left_panel, weight=1)
        
        # Dashboard list
        list_frame = ttk.LabelFrame(left_panel, text="Available Dashboards")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.dashboard_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, activestyle='dotbox',
                                           bg=UI_COLORS['background'], fg=UI_COLORS['text'],
                                           selectbackground=UI_COLORS['primary'], selectforeground='white')
        self.dashboard_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.dashboard_listbox.bind('<<ListboxSelect>>', self._on_dashboard_select)
        
        # Right panel for dashboard content
        right_panel = ttk.Frame(paned_window)
        paned_window.add(right_panel, weight=4)
        
        # Dashboard content
        dashboard_frame = ttk.LabelFrame(right_panel, text="Dashboard Viewer")
        dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a canvas with scrollbar for dashboard content
        self.canvas_frame = ttk.Frame(dashboard_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg=UI_COLORS['background'])
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Status bar
        status_bar = ttk.Frame(self)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        status_label = ttk.Label(status_bar, textvariable=self.status_text, anchor=tk.W)
        status_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Welcome message in dashboard area
        welcome_frame = ttk.Frame(self.scrollable_frame)
        welcome_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        welcome_title = ttk.Label(welcome_frame, text="Welcome to AGI Dashboard Generator", 
                                 font=("Helvetica", 16, "bold"))
        welcome_title.pack(pady=(0, 10))
        
        welcome_text = ttk.Label(welcome_frame, text="To get started, select a folder containing your reports and click 'Analyze Reports'.",
                                wraplength=600, justify=tk.CENTER)
        welcome_text.pack(pady=(0, 20))
        
        # Instructions
        instructions_frame = ttk.LabelFrame(welcome_frame, text="Basic Workflow")
        instructions_frame.pack(fill=tk.X, padx=20, pady=10)
        
        instructions = [
            "1. Select Reports Folder: Click 'Browse...' to select a folder containing your reports",
            "2. Configure Options: Select which file types to process and choose the analysis depth",
            "3. Analyze Reports: Click 'Analyze Reports' to process the data and generate dashboards",
            "4. View Dashboards: Navigate through the generated dashboards in the dashboard viewer"
        ]
        
        for instruction in instructions:
            instr_label = ttk.Label(instructions_frame, text=instruction, wraplength=600, justify=tk.LEFT)
            instr_label.pack(anchor=tk.W, padx=10, pady=5)
    
    def _initialize_folder_monitor(self):
        """Initialize the folder monitor."""
        self.folder_monitor = FolderMonitor(callback=self._process_report_callback)
        logger.info("Folder monitor initialized")
    
    def _browse_folder(self):
        """Open a dialog to browse for a folder."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.status_text.set(f"Selected folder: {folder_selected}")
            logger.info(f"Selected folder: {folder_selected}")
            
            # Update folder monitor
            if self.folder_monitor:
                self.folder_monitor.set_folder(folder_selected)
                
                # Start monitoring if enabled
                if self.monitor_enabled.get():
                    self._start_monitoring()
    
    def _start_monitoring(self):
        """Start monitoring the selected folder."""
        if not self.folder_path.get():
            messagebox.showwarning("Warning", "Please select a folder to monitor.")
            return
        
        if self.folder_monitor and not self.folder_monitor.is_monitoring():
            # Start monitoring in a separate thread
            self.monitor_thread = threading.Thread(target=self._monitor_folder)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            self.status_text.set(f"Monitoring folder: {self.folder_path.get()}")
            logger.info(f"Started monitoring folder: {self.folder_path.get()}")
    
    def _stop_monitoring(self):
        """Stop monitoring the folder."""
        if self.folder_monitor and self.folder_monitor.is_monitoring():
            self.folder_monitor.stop_monitoring()
            self.status_text.set("Folder monitoring stopped")
            logger.info("Folder monitoring stopped")
    
    def _monitor_folder(self):
        """Monitor the folder for changes."""
        if self.folder_monitor:
            self.folder_monitor.start_monitoring()
    
    def _process_report_callback(self, file_path, file_type, event_type):
        """
        Callback function for processing report files.
        
        Args:
            file_path: Path to the report file
            file_type: Type of report file ('excel', 'csv', 'pdf')
            event_type: Type of event ('created', 'modified', 'moved', 'existing')
        """
        # Check if file type is enabled
        if (file_type == 'excel' and not self.excel_enabled.get()) or \
           (file_type == 'csv' and not self.csv_enabled.get()) or \
           (file_type == 'pdf' and not self.pdf_enabled.get()):
            logger.info(f"Skipping {file_type} file: {file_path} (file type disabled)")
            return
        
        # Update status
        self.status_text.set(f"Processing {file_type} file: {os.path.basename(file_path)}")
        
        # Process the file
        try:
            # Process the report file
            analysis_results = process_report_file(file_path, file_type, event_type)
            
            if analysis_result
(Content truncated due to size limit. Use line ranges to read in chunks)
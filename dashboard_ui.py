#!/usr/bin/env python3
"""
AGI Dashboard Generator - Dashboard UI Module

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
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import after path adjustment
from file_monitor import FolderMonitor
from data_analyzer import DataExtractor, DataAnalyzer, process_report_file
from visualization_generator import VisualizationGenerator
from openai_analyzer import OpenAIAnalyzer, enhance_analysis_with_openai

# AGI Dashboard Generator - Installation Guide

This guide provides detailed instructions for installing and running the AGI Dashboard Generator application.

## System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+ recommended)
- **Python**: Version 3.8 or higher
- **RAM**: Minimum 4GB, 8GB recommended for larger datasets
- **Disk Space**: At least 500MB for the application and dependencies
- **Display**: 1280x720 or higher resolution

## Installation Methods

### Method 1: Using pip (Recommended)

1. Open a terminal or command prompt
2. Install the package directly from the source:
   ```
   pip install git+https://github.com/yourusername/agi_dashboard_generator.git
   ```
3. Launch the application:
   ```
   agi-dashboard-generator
   ```

### Method 2: Manual Installation

1. Download the source code:
   ```
   git clone https://github.com/yourusername/agi_dashboard_generator.git
   cd agi_dashboard_generator
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the package in development mode:
   ```
   pip install -e .
   ```

4. Run the application:
   ```
   python src/main.py
   ```

## Troubleshooting

### Missing tkinter

If you encounter an error about missing tkinter, install it using your package manager:

- **Ubuntu/Debian**:
  ```
  sudo apt-get install python3-tk
  ```

- **Fedora**:
  ```
  sudo dnf install python3-tkinter
  ```

- **macOS** (using Homebrew):
  ```
  brew install python-tk
  ```

- **Windows**:
  Tkinter is included with the standard Python installer. If missing, reinstall Python and ensure you check "tcl/tk and IDLE" during installation.

### OpenAI API Issues

If you're having trouble with the OpenAI integration:

1. Verify your API key is correct and has sufficient credits
2. Check your internet connection
3. Ensure you're not hitting rate limits with the OpenAI API

### Display Issues

If the application window appears too small or elements are cut off:

1. Resize the window manually
2. Adjust your display scaling settings in your operating system
3. Try running the application on a monitor with higher resolution

## Uninstallation

To remove the application:

```
pip uninstall agi-dashboard-generator
```

## Getting Help

If you encounter any issues not covered in this guide, please:

1. Check the README.md file for additional information
2. Submit an issue on the GitHub repository
3. Contact the development team at support@example.com

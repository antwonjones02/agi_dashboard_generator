# AGI Dashboard Generator

A powerful desktop application that automatically generates interactive dashboards from your report files.

## Features

- **Multi-format Support**: Process Excel (.xlsx, .xls), CSV, and PDF files
- **Intelligent Analysis**: Automatically identify data types, patterns, and relationships
- **Dynamic Visualization**: Generate appropriate charts and graphs based on data characteristics
- **Interactive Dashboards**: View and interact with generated dashboards
- **Folder Monitoring**: Automatically process new or updated reports
- **Configurable Analysis**: Choose different analysis depths based on your needs
- **OpenAI Integration**: Leverage AI for deeper data analysis and insights
- **Export Functionality**: Export dashboards to CSV or PDF formats

## Installation

### Prerequisites

- Python 3.8 or higher
- Tkinter (usually comes with Python, but may need to be installed separately)

### Install from Source

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/agi_dashboard_generator.git
   cd agi_dashboard_generator
   ```

2. Install the package:
   ```
   pip install -e .
   ```

3. Run the application:
   ```
   python src/main.py
   ```

## Usage

### Basic Workflow

1. **Select Reports Folder**: Click "Browse..." to select a folder containing your reports
2. **Configure Options**: 
   - Select which file types to process
   - Choose the analysis depth
   - Enable/disable folder monitoring
   - Enable OpenAI integration (optional)
3. **Analyze Reports**: Click "Analyze Reports" to process the data and generate dashboards
4. **View Dashboards**: Navigate through the generated dashboards in the dashboard viewer

### Analysis Depth Options

- **Basic**: Quick analysis with fundamental statistics and simple visualizations
- **Standard**: Comprehensive analysis with correlations and more detailed visualizations
- **Advanced**: In-depth analysis with advanced statistical methods and detailed insights

### OpenAI Integration

For deeper analysis, you can enable OpenAI integration:

1. Check the "Enable OpenAI Analysis" option
2. Enter your OpenAI API key in the provided field
3. Select the desired analysis depth

This will enhance your dashboards with AI-generated insights, executive summaries, and strategic recommendations.

### Dashboard Types

The application generates several types of visualizations based on the data:

- **Data Overview**: Summary of the dataset structure and characteristics
- **Missing Values**: Analysis of missing data points
- **Numeric Distribution**: Distribution and statistics for numeric columns
- **Categorical Distribution**: Distribution of categorical values
- **Correlations**: Heatmap showing relationships between numeric columns
- **Time Series**: Trends over time for date-based data

### Export Options

- **CSV Export**: Export dashboard data to CSV format
- **PDF Export**: Export dashboard visualizations to PDF format

## Project Structure

```
agi_dashboard_generator/
├── src/
│   ├── file_monitor.py       # File monitoring system
│   ├── data_analyzer.py      # Data extraction and analysis
│   ├── visualization_generator.py  # Visualization creation
│   ├── openai_analyzer.py    # OpenAI integration
│   ├── dashboard_ui.py       # User interface
│   └── main.py               # Main entry point
├── data/                     # Data directory
│   ├── analysis_results/     # Analysis results
│   └── visualizations/       # Generated visualizations
├── tests/                    # Test files
├── setup.py                  # Package setup script
└── README.md                 # This file
```

## Dependencies

- pandas, numpy: Data processing
- matplotlib, seaborn, plotly: Visualization
- dash: Interactive dashboards
- watchdog: File monitoring
- PyPDF2, openpyxl: File format handling
- reportlab: PDF export
- requests: API communication
- tkinter: User interface

## License

MIT License

#!/usr/bin/env python3
"""
AGI Dashboard Generator - Visualization Generator

This module provides functionality to create professional visualizations based on
analyzed data, with styles inspired by Harvard Business Review and New York Times.
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AGI-Dashboard-Generator')

# Define visualization styles
VISUALIZATION_STYLES = {
    'hbr': {
        'colors': ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#F0E442', '#56B4E9', '#E69F00', '#000000'],
        'background_color': '#FFFFFF',
        'font_family': 'Arial',
        'title_font_size': 16,
        'axis_font_size': 12,
        'label_font_size': 10,
        'grid_alpha': 0.3,
        'figure_size': (10, 6),
        'dpi': 100,
        'style': 'whitegrid'
    },
    'nyt': {
        'colors': ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD', '#8C564B', '#E377C2', '#7F7F7F'],
        'background_color': '#F0F0F0',
        'font_family': 'DejaVu Sans',
        'title_font_size': 18,
        'axis_font_size': 14,
        'label_font_size': 12,
        'grid_alpha': 0.2,
        'figure_size': (12, 7),
        'dpi': 100,
        'style': 'ticks'
    }
}

class VisualizationGenerator:
    """
    Generate professional visualizations based on analyzed data.
    """
    
    def __init__(self, style='hbr'):
        """
        Initialize the visualization generator.
        
        Args:
            style: Visualization style ('hbr' or 'nyt')
        """
        self.style = style
        self.style_config = VISUALIZATION_STYLES.get(style, VISUALIZATION_STYLES['hbr'])
        
        # Use system fonts instead of specific fonts that might not be available
        self.style_config['font_family'] = 'sans-serif'
        
        logger.info(f"Visualization generator initialized with {style} style")
    
    def set_style(self, style):
        """
        Set the visualization style.
        
        Args:
            style: Visualization style ('hbr' or 'nyt')
        """
        if style in VISUALIZATION_STYLES:
            self.style = style
            self.style_config = VISUALIZATION_STYLES[style]
            logger.info(f"Visualization style set to {style}")
        else:
            logger.warning(f"Unknown style: {style}, using default style")
    
    def generate_visualizations(self, analysis_results, output_dir=None):
        """
        Generate visualizations based on analysis results.
        
        Args:
            analysis_results: Analysis results from DataAnalyzer
            output_dir: Directory to save visualizations
            
        Returns:
            dict: Generated visualizations
        """
        if not analysis_results:
            logger.error("No analysis results to visualize")
            return None
        
        logger.info(f"Generating visualizations for {analysis_results['file_name']}")
        
        # Create output directory if not provided
        if not output_dir:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(base_dir, "data", "visualizations")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a directory for this file
        file_name_without_ext = os.path.splitext(analysis_results['file_name'])[0]
        file_output_dir = os.path.join(output_dir, file_name_without_ext)
        os.makedirs(file_output_dir, exist_ok=True)
        
        # Generate visualizations
        visualizations = {
            'file_name': analysis_results['file_name'],
            'file_type': analysis_results['file_type'],
            'charts': []
        }
        
        # Apply the selected style
        self._apply_style()
        
        # Process each dataframe/sheet
        if analysis_results['file_type'] in ['excel', 'csv']:
            for sheet_name, summary in analysis_results['summary'].items():
                # Skip if no KPI metrics for this sheet
                if sheet_name not in analysis_results.get('kpi_metrics', {}):
                    continue
                
                # Get KPI metrics for this sheet
                kpi_metrics = analysis_results['kpi_metrics'][sheet_name]
                
                # Generate KPI visualizations
                kpi_charts = self._generate_kpi_visualizations(sheet_name, kpi_metrics, file_output_dir)
                if kpi_charts:
                    visualizations['charts'].extend(kpi_charts)
                
                # Generate correlation visualizations if available
                if 'correlations' in analysis_results and sheet_name in analysis_results['correlations']:
                    correlations = analysis_results['correlations'][sheet_name]
                    corr_charts = self._generate_correlation_visualizations(sheet_name, correlations, file_output_dir)
                    if corr_charts:
                        visualizations['charts'].extend(corr_charts)
                
                # Generate trend visualizations if available
                if 'trends' in analysis_results and any(trend_key.startswith(sheet_name) for trend_key in analysis_results['trends']):
                    sheet_trends = {k: v for k, v in analysis_results['trends'].items() if k.startswith(sheet_name)}
                    trend_charts = self._generate_trend_visualizations(sheet_name, sheet_trends, file_output_dir)
                    if trend_charts:
                        visualizations['charts'].extend(trend_charts)
        
        # Generate insight visualizations
        if 'insights' in analysis_results and analysis_results['insights']:
            insight_charts = self._generate_insight_visualizations(analysis_results['insights'], file_output_dir)
            if insight_charts:
                visualizations['charts'].extend(insight_charts)
        
        # Save visualization metadata
        metadata_file = os.path.join(file_output_dir, "visualization_metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump(visualizations, f, indent=2)
        
        logger.info(f"Generated {len(visualizations['charts'])} visualizations in {file_output_dir}")
        
        return visualizations
    
    def _apply_style(self):
        """Apply the selected visualization style."""
        # Set seaborn style
        sns.set_style(self.style_config['style'])
        
        # Set matplotlib parameters
        plt.rcParams['figure.figsize'] = self.style_config['figure_size']
        plt.rcParams['figure.dpi'] = self.style_config['dpi']
        plt.rcParams['font.family'] = self.style_config['font_family']
        plt.rcParams['axes.titlesize'] = self.style_config['title_font_size']
        plt.rcParams['axes.labelsize'] = self.style_config['axis_font_size']
        plt.rcParams['xtick.labelsize'] = self.style_config['label_font_size']
        plt.rcParams['ytick.labelsize'] = self.style_config['label_font_size']
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = self.style_config['grid_alpha']
        plt.rcParams['axes.facecolor'] = self.style_config['background_color']
        plt.rcParams['figure.facecolor'] = self.style_config['background_color']
    
    def _generate_kpi_visualizations(self, sheet_name, kpi_metrics, output_dir):
        """
        Generate visualizations for KPI metrics.
        
        Args:
            sheet_name: Name of the sheet or table
            kpi_metrics: KPI metrics
            output_dir: Directory to save visualizations
            
        Returns:
            list: Generated chart metadata
        """
        charts = []
        
        # Group KPIs by category
        kpi_by_category = {}
        for col, metrics in kpi_metrics.items():
            category = metrics.get('category')
            if category not in kpi_by_category:
                kpi_by_category[category] = []
            
            kpi_by_category[category].append({
                'column': col,
                'metrics': metrics
            })
        
        # Generate visualizations for each category
        for category, kpis in kpi_by_category.items():
            # Skip if no numeric metrics
            if not any('mean' in kpi['metrics'] for kpi in kpis):
                continue
            
            # Create a bar chart for this category
            fig, ax = plt.subplots()
            
            # Prepare data
            columns = []
            values = []
            
            for kpi in kpis:
                if 'mean' in kpi['metrics']:
                    columns.append(kpi['column'])
                    values.append(kpi['metrics']['mean'])
            
            # Skip if no data
            if not columns:
                continue
            
            # Create bar chart
            bars = ax.bar(columns, values, color=self.style_config['colors'])
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{height:.2f}', ha='center', va='bottom')
            
            # Set title and labels
            category_title = category.replace('_', ' ').title()
            ax.set_title(f"{category_title} Metrics")
            ax.set_xlabel("Metrics")
            ax.set_ylabel("Value")
            
            # Rotate x-axis labels if needed
            if max(len(col) for col in columns) > 10:
                plt.xticks(rotation=45, ha='right')
            
            # Adjust layout
            plt.tight_layout()
            
            # Save the figure
            chart_file = f"{sheet_name}_{category}_bar_chart.png"
            chart_path = os.path.join(output_dir, chart_file)
            plt.savefig(chart_path)
            plt.close()
            
            # Add chart metadata
            charts.append({
                'title': f"{category_title} Metrics",
                'type': 'bar',
                'category': category,
                'source': sheet_name,
                'file': chart_file,
                'path': chart_path
            })
            
            # Create a radar chart for this category if there are multiple metrics
            if len(columns) >= 3:
                # Create a figure
                fig = plt.figure(figsize=self.style_config['figure_size'])
                
                # Create a radar chart
                ax = fig.add_subplot(111, polar=True)
                
                # Compute angle for each metric
                angles = np.linspace(0, 2*np.pi, len(columns), endpoint=False).tolist()
                
                # Close the polygon
                values.append(values[0])
                angles.append(angles[0])
                
                # Plot data
                ax.plot(angles, values, 'o-', linewidth=2, color=self.style_config['colors'][0])
                ax.fill(angles, values, alpha=0.25, color=self.style_config['colors'][0])
                
                # Set category labels
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(columns)
                
                # Set title
                ax.set_title(f"{category_title} Metrics Radar")
                
                # Adjust layout
                plt.tight_layout()
                
                # Save the figure
                chart_file = f"{sheet_name}_{category}_radar_chart.png"
                chart_path = os.path.join(output_dir, chart_file)
                plt.savefig(chart_path)
                plt.close()
                
                # Add chart metadata
                charts.append({
                    'title': f"{category_title} Metrics Radar",
                    'type': 'radar',
                    'category': category,
                    'source': sheet_name,
                    'file': chart_file,
                    'path': chart_path
                })
            
            # Create an interactive plotly bar chart
            fig = go.Figure(data=[
                go.Bar(
                    x=columns,
                    y=values,
                    marker_color=self.style_config['colors'][0]
                )
            ])
            
            # Update layout
            fig.update_layout(
                title=f"{category_title} Metrics",
                xaxis_title="Metrics",
                yaxis_title="Value",
                template="plotly_white",
                font=dict(
                    family=self.style_config['font_family'],
                    size=self.style_config['label_font_size']
                )
            )
            
            # Save as HTML
            chart_file = f"{sheet_name}_{category}_interactive_bar.html"
            chart_path = os.path.join(output_dir, chart_file)
            fig.write_html(chart_path)
            
            # Add chart metadata
            charts.append({
                'title': f"{category_title} Metrics (Interactive)",
                'type': 'interactive_bar',
                'category': category,
                'source': sheet_name,
                'file': chart_file,
                'path': chart_path
            })
        
        return charts
    
    def _generate_correlation_visualizations(self, sheet_name, correlations, output_dir):
        """
        Generate visualizations for correlations.
        
        Args:
            sheet_name: Name of the sheet or table
            correlations: Correlation matrix
            output_dir: Directory to save visualizations
            
        Returns:
            list: Generated chart metadata
        """
        charts = []
        
        # Skip if no correlations
        if not correlations:
            return charts
        
        # Create a correlation matrix
        columns = list(correlations.keys())
        
        # Skip if too few columns
        if len(columns) < 2:
            return charts
        
        # Create a correlation matrix
        corr_matrix = pd.DataFrame(index=columns, columns=columns)
        
        for col1 in columns:
            for col2 in columns:
                if col1 == col2:
                    corr_matrix.loc[col1, col2] = 1.0
                else:
                    corr_matrix.loc[col1, col2] = correlations[col1].get(col2, 0)
        
        # Convert to float type to avoid dtype object error
        corr_matrix = corr_matrix.astype(float)
        
        # Create a heatmap
        plt.figure(figsize=self.style_config['figure_size'])
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0,
                   linewidths=0.5, cbar_kws={"shrink": 0.8})
        
        # Set title
        plt.title(f"Correlation Matrix - {sheet_name}")
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the figure
        chart_file = f"{sheet_name}_correlation_heatmap.png"
        chart_path = os.path.join(output_dir, chart_file)
        plt.savefig(chart_path)
        plt.close()
        
        # Add chart metadata
        charts.append({
            'title': f"Correlation Matrix - {sheet_name}",
            'type': 'heatmap',
            'category': 'correlation',
            'source': sheet_name,
            'file': chart_file,
            'path': chart_path
        })
        
        # Create an interactive plotly heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            
(Content truncated due to size limit. Use line ranges to read in chunks)
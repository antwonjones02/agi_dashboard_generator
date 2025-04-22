#!/usr/bin/env python3
"""
AGI Dashboard Generator - Data Extraction and Analysis

This module provides functionality to extract data from various report formats
(Excel, CSV, PDF) and analyze it to identify patterns and insights, with a focus
on operational KPIs and learning/development metrics.
"""

import os
import pandas as pd
import numpy as np
import logging
import PyPDF2
from pathlib import Path
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AGI-Dashboard-Generator')

class DataExtractor:
    """
    Extract data from various report formats.
    """
    
    def __init__(self):
        """Initialize the data extractor."""
        logger.info("Data extractor initialized")
    
    def extract_data(self, file_path, file_type):
        """
        Extract data from a report file.
        
        Args:
            file_path: Path to the report file
            file_type: Type of report file ('excel', 'csv', 'pdf')
            
        Returns:
            dict: Extracted data and metadata
        """
        logger.info(f"Extracting data from {file_type} file: {file_path}")
        
        if file_type == 'excel':
            return self._extract_from_excel(file_path)
        elif file_type == 'csv':
            return self._extract_from_csv(file_path)
        elif file_type == 'pdf':
            return self._extract_from_pdf(file_path)
        else:
            logger.error(f"Unsupported file type: {file_type}")
            return None
    
    def _extract_from_excel(self, file_path):
        """
        Extract data from an Excel file.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            dict: Extracted data and metadata
        """
        try:
            # Get the Excel file name without extension
            file_name = os.path.basename(file_path)
            file_name_without_ext = os.path.splitext(file_name)[0]
            
            # Read all sheets from the Excel file
            excel_data = pd.read_excel(file_path, sheet_name=None)
            
            # Process each sheet
            processed_data = {}
            for sheet_name, df in excel_data.items():
                # Clean the dataframe
                df = self._clean_dataframe(df)
                
                # Store the processed dataframe
                processed_data[sheet_name] = df
            
            # Create metadata
            metadata = {
                'file_name': file_name,
                'file_type': 'excel',
                'sheet_count': len(excel_data),
                'sheet_names': list(excel_data.keys()),
                'row_counts': {sheet: df.shape[0] for sheet, df in processed_data.items()},
                'column_counts': {sheet: df.shape[1] for sheet, df in processed_data.items()},
                'column_names': {sheet: list(df.columns) for sheet, df in processed_data.items()}
            }
            
            return {
                'data': processed_data,
                'metadata': metadata
            }
        
        except Exception as e:
            logger.error(f"Error extracting data from Excel file: {e}")
            return None
    
    def _extract_from_csv(self, file_path):
        """
        Extract data from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            dict: Extracted data and metadata
        """
        try:
            # Get the CSV file name without extension
            file_name = os.path.basename(file_path)
            file_name_without_ext = os.path.splitext(file_name)[0]
            
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Clean the dataframe
            df = self._clean_dataframe(df)
            
            # Create metadata
            metadata = {
                'file_name': file_name,
                'file_type': 'csv',
                'row_count': df.shape[0],
                'column_count': df.shape[1],
                'column_names': list(df.columns)
            }
            
            return {
                'data': {file_name_without_ext: df},
                'metadata': metadata
            }
        
        except Exception as e:
            logger.error(f"Error extracting data from CSV file: {e}")
            return None
    
    def _extract_from_pdf(self, file_path):
        """
        Extract data from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            dict: Extracted data and metadata
        """
        try:
            # Get the PDF file name without extension
            file_name = os.path.basename(file_path)
            file_name_without_ext = os.path.splitext(file_name)[0]
            
            # Open the PDF file
            with open(file_path, 'rb') as file:
                # Create a PDF reader object
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Get the number of pages
                num_pages = len(pdf_reader.pages)
                
                # Extract text from each page
                text_content = []
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text_content.append(page.extract_text())
                
                # Join all text content
                full_text = '\n'.join(text_content)
                
                # Try to extract tables from the text
                tables = self._extract_tables_from_text(full_text)
                
                # Create metadata
                metadata = {
                    'file_name': file_name,
                    'file_type': 'pdf',
                    'page_count': num_pages,
                    'table_count': len(tables)
                }
                
                return {
                    'data': {
                        'text': full_text,
                        'tables': tables
                    },
                    'metadata': metadata
                }
        
        except Exception as e:
            logger.error(f"Error extracting data from PDF file: {e}")
            return None
    
    def _extract_tables_from_text(self, text):
        """
        Attempt to extract tables from text.
        
        Args:
            text: Text content
            
        Returns:
            list: List of extracted tables as dataframes
        """
        # This is a simplified implementation
        # In a real-world scenario, you would use more sophisticated methods
        # such as tabula-py or other PDF table extraction libraries
        
        tables = []
        
        # Split the text into lines
        lines = text.split('\n')
        
        # Look for potential table markers
        table_start_indices = []
        table_end_indices = []
        
        for i, line in enumerate(lines):
            # Check for lines that might indicate the start of a table
            # (e.g., lines with multiple commas or tabs)
            if line.count(',') >= 3 or line.count('\t') >= 3:
                if not table_start_indices or table_start_indices[-1] < table_end_indices[-1]:
                    table_start_indices.append(i)
            
            # Check for lines that might indicate the end of a table
            # (e.g., empty lines after a potential table)
            if line.strip() == '' and table_start_indices and (not table_end_indices or table_start_indices[-1] > table_end_indices[-1]):
                table_end_indices.append(i)
        
        # Ensure we have matching start and end indices
        if len(table_start_indices) > len(table_end_indices):
            table_end_indices.append(len(lines))
        
        # Extract tables
        for start, end in zip(table_start_indices, table_end_indices):
            table_lines = lines[start:end]
            
            # Skip if too few lines
            if len(table_lines) < 2:
                continue
            
            # Try to determine the delimiter
            first_line = table_lines[0]
            if ',' in first_line:
                delimiter = ','
            elif '\t' in first_line:
                delimiter = '\t'
            else:
                # Try to split by whitespace
                delimiter = None
            
            # Create a dataframe from the table lines
            try:
                if delimiter:
                    # Create a CSV-like string
                    csv_string = '\n'.join(table_lines)
                    df = pd.read_csv(pd.StringIO(csv_string), delimiter=delimiter)
                else:
                    # Try to split by whitespace
                    data = []
                    for line in table_lines:
                        data.append(line.split())
                    
                    # Use the first row as header
                    header = data[0]
                    rows = data[1:]
                    
                    # Create a dataframe
                    df = pd.DataFrame(rows, columns=header)
                
                # Clean the dataframe
                df = self._clean_dataframe(df)
                
                tables.append(df)
            
            except Exception as e:
                logger.warning(f"Failed to extract table: {e}")
        
        return tables
    
    def _clean_dataframe(self, df):
        """
        Clean a dataframe by handling missing values, removing duplicates, etc.
        
        Args:
            df: Pandas dataframe
            
        Returns:
            df: Cleaned dataframe
        """
        # Make a copy to avoid modifying the original
        df = df.copy()
        
        # Remove completely empty rows and columns
        df.dropna(how='all', inplace=True)
        df.dropna(axis=1, how='all', inplace=True)
        
        # Remove duplicate rows
        df.drop_duplicates(inplace=True)
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        return df


class DataAnalyzer:
    """
    Analyze data to identify patterns and insights, with a focus on
    operational KPIs and learning/development metrics.
    """
    
    def __init__(self):
        """Initialize the data analyzer."""
        logger.info("Data analyzer initialized")
        
        # Define KPI categories and related keywords
        self.kpi_categories = {
            'learning_completion': [
                'completion', 'progress', 'finished', 'graduated', 'certified',
                'pass rate', 'completion rate', 'graduation rate', 'certification rate'
            ],
            'learning_engagement': [
                'engagement', 'participation', 'active', 'attendance', 'session',
                'login', 'access', 'view', 'download', 'time spent', 'duration'
            ],
            'learning_performance': [
                'score', 'grade', 'performance', 'assessment', 'test', 'exam',
                'quiz', 'evaluation', 'rating', 'ranking', 'percentile'
            ],
            'operational_efficiency': [
                'efficiency', 'productivity', 'output', 'throughput', 'turnaround',
                'cycle time', 'processing time', 'response time', 'lead time'
            ],
            'training_cost': [
                'cost', 'expense', 'budget', 'spending', 'investment',
                'roi', 'return', 'value', 'benefit', 'saving'
            ]
        }
    
    def analyze_data(self, extracted_data):
        """
        Analyze extracted data to identify patterns and insights.
        
        Args:
            extracted_data: Dict containing extracted data and metadata
            
        Returns:
            dict: Analysis results
        """
        if not extracted_data:
            logger.error("No data to analyze")
            return None
        
        logger.info(f"Analyzing data from {extracted_data['metadata']['file_name']}")
        
        file_type = extracted_data['metadata']['file_type']
        
        if file_type in ['excel', 'csv']:
            return self._analyze_tabular_data(extracted_data)
        elif file_type == 'pdf':
            return self._analyze_pdf_data(extracted_data)
        else:
            logger.error(f"Unsupported file type for analysis: {file_type}")
            return None
    
    def _analyze_tabular_data(self, extracted_data):
        """
        Analyze tabular data (Excel, CSV).
        
        Args:
            extracted_data: Dict containing extracted data and metadata
            
        Returns:
            dict: Analysis results
        """
        analysis_results = {
            'file_name': extracted_data['metadata']['file_name'],
            'file_type': extracted_data['metadata']['file_type'],
            'summary': {},
            'kpi_metrics': {},
            'correlations': {},
            'trends': {},
            'insights': []
        }
        
        # Process each dataframe
        for sheet_name, df in extracted_data['data'].items():
            # Skip if dataframe is empty
            if df.empty:
                continue
            
            # Create a summary for this sheet/dataframe
            summary = self._create_data_summary(df)
            analysis_results['summary'][sheet_name] = summary
            
            # Identify KPI metrics
            kpi_metrics = self._identify_kpi_metrics(df)
            if kpi_metrics:
                analysis_results['kpi_metrics'][sheet_name] = kpi_metrics
            
            # Calculate correlations between numeric columns
            correlations = self._calculate_correlations(df)
            if correlations is not None:
                analysis_results['correlations'][sheet_name] = correlations
            
            # Identify trends in time series data
            trends = self._identify_trends(df)
            if trends:
                analysis_results['trends'][sheet_name] = trends
            
            # Generate insights
            insights = self._generate_insights(df, sheet_name, kpi_metrics, correlations, trends)
            if insights:
                analysis_results['insights'].extend(insights)
        
        return analysis_results
    
    def _analyze_pdf_data(self, extracted_data):
        """
        Analyze PDF data.
        
        Args:
            extracted_data: Dict containing extracted data and metadata
            
        Returns:
            dict: Analysis results
        """
        analysis_results = {
            'file_name': extracted_data['metadata']['file_name'],
            'file_type': extracted_data['metadata']['file_type'],
            'summary': {},
            'kpi_metrics': {},
            'key_terms': {},
            'insights': []
        }
        
        # Analyze text content
        text = extracted_data['data']['text']
        
        # Extract key terms related to KPIs
        key_terms = self._extract_key_terms(text)
        analysis_results['key_terms'] = key_terms
        
        # Analyze tables if available
        tables = extracted_data['data']['tables']
        
        for i, df in enumerate(tables):
            table_name = f"Table_{i+1}"
            
            # Create a summary for this table
            summary = self._create_data_summary(df)
            analysis_results['summary'][table_name] = summary
            
            # Identify KPI metrics
            kpi_metrics = self._identify_kpi_metrics(df)
            if kpi_metrics:
                analysis_results['kpi_metrics'][table_name] = kpi_metrics
            
            # Generate insights
            insights = self._generate_insights(df, table_name, kpi_metrics, None, None)
           
(Content truncated due to size limit. Use line ranges to read in chunks)
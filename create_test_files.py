#!/usr/bin/env python3
"""
AGI Dashboard Generator - Test File Monitor

This script creates test files in the data directory to verify the file monitoring system.
"""

import os
import time
import pandas as pd
import numpy as np
from pathlib import Path

def create_test_files():
    """Create test files in the data directory."""
    # Get the data directory path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    
    # Create the data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    print(f"Creating test files in {data_dir}")
    
    # Create a test CSV file
    csv_path = os.path.join(data_dir, "test_sales_data.csv")
    df_sales = pd.DataFrame({
        'Date': pd.date_range(start='2024-01-01', periods=100),
        'Product': np.random.choice(['Product A', 'Product B', 'Product C', 'Product D'], 100),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], 100),
        'Sales': np.random.randint(100, 1000, 100),
        'Units': np.random.randint(1, 50, 100)
    })
    df_sales.to_csv(csv_path, index=False)
    print(f"Created CSV file: {csv_path}")
    
    # Create a test Excel file
    excel_path = os.path.join(data_dir, "test_financial_data.xlsx")
    df_financial = pd.DataFrame({
        'Quarter': ['Q1', 'Q2', 'Q3', 'Q4'] * 5,
        'Year': sorted([2020, 2021, 2022, 2023, 2024] * 4),
        'Revenue': np.random.randint(10000, 100000, 20),
        'Expenses': np.random.randint(5000, 50000, 20),
        'Profit': np.random.randint(1000, 50000, 20)
    })
    df_financial.to_excel(excel_path, index=False)
    print(f"Created Excel file: {excel_path}")
    
    # Create another test Excel file with multiple sheets
    multi_sheet_path = os.path.join(data_dir, "test_multi_sheet_data.xlsx")
    with pd.ExcelWriter(multi_sheet_path) as writer:
        # Sales by region sheet
        df_region = pd.DataFrame({
            'Region': ['North', 'South', 'East', 'West'],
            'Q1_Sales': np.random.randint(1000, 5000, 4),
            'Q2_Sales': np.random.randint(1000, 5000, 4),
            'Q3_Sales': np.random.randint(1000, 5000, 4),
            'Q4_Sales': np.random.randint(1000, 5000, 4)
        })
        df_region.to_excel(writer, sheet_name='Regional_Sales', index=False)
        
        # Product performance sheet
        df_product = pd.DataFrame({
            'Product': ['Product A', 'Product B', 'Product C', 'Product D'],
            'Units_Sold': np.random.randint(100, 1000, 4),
            'Revenue': np.random.randint(10000, 50000, 4),
            'Customer_Rating': np.random.uniform(3.0, 5.0, 4).round(1)
        })
        df_product.to_excel(writer, sheet_name='Product_Performance', index=False)
        
        # Customer demographics sheet
        df_customer = pd.DataFrame({
            'Age_Group': ['18-24', '25-34', '35-44', '45-54', '55+'],
            'Count': np.random.randint(100, 500, 5),
            'Avg_Purchase': np.random.randint(50, 200, 5)
        })
        df_customer.to_excel(writer, sheet_name='Customer_Demographics', index=False)
    
    print(f"Created multi-sheet Excel file: {multi_sheet_path}")
    
    return data_dir

if __name__ == "__main__":
    data_dir = create_test_files()
    print(f"Test files created successfully in {data_dir}")

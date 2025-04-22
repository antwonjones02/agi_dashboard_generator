#!/usr/bin/env python3
"""
AGI Dashboard Generator - Setup Script

This script is used to package the AGI Dashboard Generator application.
"""

from setuptools import setup, find_packages

setup(
    name="agi_dashboard_generator",
    version="1.0.0",
    description="Automatically generate interactive dashboards from report files",
    author="AGI Dashboard Generator Team",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "plotly",
        "dash",
        "watchdog",
        "PyPDF2",
        "openpyxl",
        "reportlab",
        "pillow",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "agi-dashboard-generator=src.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Business/Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)

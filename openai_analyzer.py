#!/usr/bin/env python3
"""
AGI Dashboard Generator - OpenAI Integration

This module provides functionality to leverage OpenAI's API for deeper data analysis
of reports and generation of insights.
"""

import os
import json
import logging
import pandas as pd
import numpy as np
import requests
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AGI-Dashboard-Generator')

class OpenAIAnalyzer:
    """
    Leverage OpenAI's API for deeper data analysis and insights generation.
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the OpenAI analyzer.
        
        Args:
            api_key: OpenAI API key (optional, can be set later)
        """
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4"  # Default to GPT-4 for best analysis
        logger.info("OpenAI analyzer initialized")
    
    def set_api_key(self, api_key):
        """
        Set the OpenAI API key.
        
        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key
        logger.info("OpenAI API key set")
    
    def set_model(self, model):
        """
        Set the OpenAI model to use.
        
        Args:
            model: OpenAI model name (e.g., "gpt-4", "gpt-3.5-turbo")
        """
        self.model = model
        logger.info(f"OpenAI model set to {model}")
    
    def analyze_data(self, analysis_results, depth="standard"):
        """
        Analyze data using OpenAI API to generate deeper insights.
        
        Args:
            analysis_results: Analysis results from DataAnalyzer
            depth: Analysis depth ("basic", "standard", "advanced")
            
        Returns:
            dict: Enhanced analysis results with AI-generated insights
        """
        if not self.api_key:
            logger.error("OpenAI API key not set")
            return analysis_results
        
        logger.info(f"Performing {depth} OpenAI analysis on {analysis_results['file_name']}")
        
        # Create a copy of the analysis results
        enhanced_results = analysis_results.copy()
        
        # Add AI insights section if it doesn't exist
        if 'ai_insights' not in enhanced_results:
            enhanced_results['ai_insights'] = {}
        
        # Process based on file type
        file_type = analysis_results['file_type']
        
        if file_type in ['excel', 'csv']:
            # Analyze tabular data
            ai_insights = self._analyze_tabular_data(analysis_results, depth)
            if ai_insights:
                enhanced_results['ai_insights']['tabular_analysis'] = ai_insights
        
        elif file_type == 'pdf':
            # Analyze PDF data
            ai_insights = self._analyze_pdf_data(analysis_results, depth)
            if ai_insights:
                enhanced_results['ai_insights']['pdf_analysis'] = ai_insights
        
        # Generate executive summary
        summary = self._generate_executive_summary(enhanced_results, depth)
        if summary:
            enhanced_results['ai_insights']['executive_summary'] = summary
        
        # Generate recommendations
        recommendations = self._generate_recommendations(enhanced_results, depth)
        if recommendations:
            enhanced_results['ai_insights']['recommendations'] = recommendations
        
        logger.info(f"OpenAI analysis completed for {analysis_results['file_name']}")
        return enhanced_results
    
    def _analyze_tabular_data(self, analysis_results, depth):
        """
        Analyze tabular data (Excel, CSV) using OpenAI API.
        
        Args:
            analysis_results: Analysis results from DataAnalyzer
            depth: Analysis depth
            
        Returns:
            dict: AI-generated insights for tabular data
        """
        # Extract relevant information for analysis
        summary = analysis_results.get('summary', {})
        kpi_metrics = analysis_results.get('kpi_metrics', {})
        correlations = analysis_results.get('correlations', {})
        trends = analysis_results.get('trends', {})
        insights = analysis_results.get('insights', [])
        
        # Prepare data for OpenAI
        data_description = self._prepare_data_description(summary, kpi_metrics, correlations, trends, insights)
        
        # Define prompt based on analysis depth
        if depth == "basic":
            prompt = f"""
            Analyze the following data summary and provide basic insights:
            
            {data_description}
            
            Focus on:
            1. Key patterns in the data
            2. Basic interpretation of the metrics
            3. Simple recommendations
            
            Format your response as JSON with the following structure:
            {{
                "key_findings": [list of 3-5 key findings],
                "patterns": [list of identified patterns],
                "interpretation": [interpretation of key metrics],
                "business_implications": [list of business implications]
            }}
            """
        
        elif depth == "advanced":
            prompt = f"""
            Perform an advanced analysis of the following data and provide detailed insights:
            
            {data_description}
            
            Focus on:
            1. Complex patterns and relationships in the data
            2. Detailed interpretation of all metrics and correlations
            3. Advanced statistical insights
            4. Comprehensive business implications
            5. Detailed strategic recommendations
            6. Potential future trends based on the data
            
            Format your response as JSON with the following structure:
            {{
                "key_findings": [list of 5-8 detailed key findings],
                "patterns": [list of complex patterns identified],
                "correlations_analysis": [detailed analysis of correlations],
                "statistical_insights": [advanced statistical observations],
                "business_implications": [comprehensive business implications],
                "strategic_recommendations": [detailed strategic recommendations],
                "future_trends": [predicted future trends based on data]
            }}
            """
        
        else:  # standard
            prompt = f"""
            Analyze the following data and provide comprehensive insights:
            
            {data_description}
            
            Focus on:
            1. Key patterns and trends in the data
            2. Interpretation of metrics and correlations
            3. Business implications
            4. Strategic recommendations
            
            Format your response as JSON with the following structure:
            {{
                "key_findings": [list of 4-6 key findings],
                "patterns": [list of patterns identified],
                "correlations_analysis": [analysis of important correlations],
                "business_implications": [list of business implications],
                "strategic_recommendations": [list of strategic recommendations]
            }}
            """
        
        # Call OpenAI API
        response = self._call_openai_api(prompt)
        
        if response:
            try:
                # Extract JSON from response
                json_str = response.strip()
                if json_str.startswith("```json"):
                    json_str = json_str.split("```json")[1]
                if json_str.endswith("```"):
                    json_str = json_str.split("```")[0]
                
                # Parse JSON
                ai_insights = json.loads(json_str)
                return ai_insights
            
            except Exception as e:
                logger.error(f"Error parsing OpenAI response: {str(e)}")
                return {"error": "Failed to parse OpenAI response", "raw_response": response}
        
        return None
    
    def _analyze_pdf_data(self, analysis_results, depth):
        """
        Analyze PDF data using OpenAI API.
        
        Args:
            analysis_results: Analysis results from DataAnalyzer
            depth: Analysis depth
            
        Returns:
            dict: AI-generated insights for PDF data
        """
        # Extract text content and key terms
        text = analysis_results.get('data', {}).get('text', '')
        key_terms = analysis_results.get('key_terms', {})
        
        # Truncate text if too long (OpenAI has token limits)
        if len(text) > 10000:
            text = text[:10000] + "... [text truncated]"
        
        # Prepare key terms description
        key_terms_description = ""
        for category, terms in key_terms.items():
            key_terms_description += f"\nCategory: {category}\nTerms: {', '.join(terms)}\n"
        
        # Define prompt based on analysis depth
        if depth == "basic":
            prompt = f"""
            Analyze the following document text and key terms and provide basic insights:
            
            TEXT EXCERPT:
            {text}
            
            KEY TERMS:
            {key_terms_description}
            
            Focus on:
            1. Main topics and themes
            2. Basic summary of content
            3. Simple implications
            
            Format your response as JSON with the following structure:
            {{
                "main_topics": [list of main topics],
                "summary": "brief summary of the document",
                "key_points": [list of key points],
                "basic_implications": [list of basic implications]
            }}
            """
        
        elif depth == "advanced":
            prompt = f"""
            Perform an advanced analysis of the following document text and key terms:
            
            TEXT EXCERPT:
            {text}
            
            KEY TERMS:
            {key_terms_description}
            
            Focus on:
            1. Detailed analysis of main topics and themes
            2. Comprehensive content analysis
            3. Identification of subtle patterns and implications
            4. Critical evaluation of the document
            5. Detailed recommendations based on the content
            
            Format your response as JSON with the following structure:
            {{
                "main_topics": [list of main topics with detailed descriptions],
                "content_analysis": "comprehensive analysis of the document content",
                "patterns": [list of identified patterns and relationships],
                "critical_evaluation": "critical evaluation of the document",
                "detailed_implications": [list of detailed implications],
                "recommendations": [list of specific recommendations]
            }}
            """
        
        else:  # standard
            prompt = f"""
            Analyze the following document text and key terms and provide comprehensive insights:
            
            TEXT EXCERPT:
            {text}
            
            KEY TERMS:
            {key_terms_description}
            
            Focus on:
            1. Main topics and themes
            2. Content summary and analysis
            3. Key implications
            4. Recommendations based on the content
            
            Format your response as JSON with the following structure:
            {{
                "main_topics": [list of main topics],
                "content_analysis": "analysis of the document content",
                "key_points": [list of key points],
                "implications": [list of implications],
                "recommendations": [list of recommendations]
            }}
            """
        
        # Call OpenAI API
        response = self._call_openai_api(prompt)
        
        if response:
            try:
                # Extract JSON from response
                json_str = response.strip()
                if json_str.startswith("```json"):
                    json_str = json_str.split("```json")[1]
                if json_str.endswith("```"):
                    json_str = json_str.split("```")[0]
                
                # Parse JSON
                ai_insights = json.loads(json_str)
                return ai_insights
            
            except Exception as e:
                logger.error(f"Error parsing OpenAI response: {str(e)}")
                return {"error": "Failed to parse OpenAI response", "raw_response": response}
        
        return None
    
    def _generate_executive_summary(self, analysis_results, depth):
        """
        Generate an executive summary using OpenAI API.
        
        Args:
            analysis_results: Enhanced analysis results
            depth: Analysis depth
            
        Returns:
            str: Executive summary
        """
        # Extract AI insights
        ai_insights = analysis_results.get('ai_insights', {})
        
        # Extract original insights
        insights = analysis_results.get('insights', [])
        
        # Prepare insights description
        insights_description = ""
        for insight in insights:
            insights_description += f"\n- {insight.get('description', '')}"
        
        # Define prompt based on analysis depth
        if depth == "basic":
            prompt = f"""
            Generate a brief executive summary based on the following insights:
            
            ORIGINAL INSIGHTS:
            {insights_description}
            
            AI INSIGHTS:
            {json.dumps(ai_insights, indent=2)}
            
            Create a concise executive summary (3-4 sentences) that highlights the most important findings.
            """
        
        elif depth == "advanced":
            prompt = f"""
            Generate a comprehensive executive summary based on the following insights:
            
            ORIGINAL INSIGHTS:
            {insights_description}
            
            AI INSIGHTS:
            {json.dumps(ai_insights, indent=2)}
            
            Create a detailed executive summary (1-2 paragraphs) that:
            1. Highlights the most important findings
            2. Explains the business implications
            3. Provides strategic context
            4. Suggests high-level next steps
            
            The summary should be suitable for C-level executives and provide actionable intelligence.
            """
        
        else:  # standard
            prompt = f"""
            Generate an executive summary based on the following insights:
            
            ORIGINAL INSIGHTS:
            {insights_description}
            
            AI INSIGHTS:
            {json.dumps(ai_insights, indent=2)}
            
            Create a clear executive summary (5-7 sentences) that highlights the key findings and their implications.
            """
        
        # Call OpenAI API
        response = self._call_openai_api(prompt)
        
        return response.strip() if response else None
    
    def _generate_recommendations(self, analysis_results, depth):
        """
        Generate recommendations using OpenAI API.
        
        Args:
            analysis_results: Enhanced analysis results
            depth: Analysis depth
            
        Returns:
            list: Recommendations
        """
        # Extract AI insights
        ai_insights = analysis_results.get('ai_insights', {})
        
        # Extract original insights
        insights = analysis_results.get('insights', [])
        
        # Prepare insights description
        insights_descr
(Content truncated due to size limit. Use line ranges to read in chunks)
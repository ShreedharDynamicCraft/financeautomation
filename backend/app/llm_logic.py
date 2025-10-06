import google.generativeai as genai
import json
import PyPDF2
import pdfplumber
import pandas as pd
import logging
import io
from typing import Dict, Any, Optional
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)

# Configure Google Gemini API
if settings.google_api_key:
    genai.configure(api_key=settings.google_api_key)
else:
    logger.warning("Google API key not configured")

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF using multiple methods for best results
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text as string
    """
    try:
        text_parts = []
        
        # Method 1: Try PyPDF2 first (simple extraction)
        try:
            logger.info("Extracting text using PyPDF2...")
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
            
            if text_parts:
                logger.info(f"PyPDF2 extracted text from {len(text_parts)} pages")
                return "\n\n".join(text_parts)
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {e}")
        
        # Method 2: Fallback to pdfplumber (better for tables)
        try:
            logger.info("Extracting text using pdfplumber...")
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
                    
                    # Also extract tables
                    tables = page.extract_tables()
                    for table_num, table in enumerate(tables):
                        if table:
                            table_text = "\n".join(["\t".join(row) if row else "" for row in table])
                            text_parts.append(f"--- Page {page_num + 1} Table {table_num + 1} ---\n{table_text}")
            
            if text_parts:
                logger.info(f"pdfplumber extracted text from {len(text_parts)} sections")
                return "\n\n".join(text_parts)
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")
        
        # If both methods fail
        if not text_parts:
            raise ValueError("Could not extract any text from PDF")
        
        return "\n\n".join(text_parts)
        
    except Exception as e:
        logger.error(f"PDF text extraction failed: {e}")
        raise

def get_data_from_llm(pdf_text: str, template_type: str) -> dict:
    """
    Calls the Gemini API with the correct, high-fidelity master prompt.
    
    Args:
        pdf_text: Extracted text from PDF
        template_type: Template type ("Extraction Template 1" or "Extraction Template 2")
        
    Returns:
        Extracted data as dictionary
    """
    if not settings.google_api_key:
        raise ValueError("Google API key not configured")
    
    try:
        # Use the recommended model
        model = genai.GenerativeModel(settings.gemini_model)

        # Configure generation parameters with JSON output enforcement
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.1,  # Low temperature for consistent results
            max_output_tokens=8192,
        )

        # Build the prompt dynamically based on user selection
        prompt = build_master_prompt(pdf_text, template_type)
        
        logger.info(f"Sending request to Gemini with {len(prompt)} characters")
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        if not response.text:
            raise ValueError("Empty response from Gemini API")
        
        logger.info(f"Received response from Gemini: {len(response.text)} characters")
        
        # Parse JSON response
        extracted_data = json.loads(response.text)
        
        # Validate the response structure
        if not isinstance(extracted_data, dict):
            raise ValueError("Invalid response format: expected JSON object")
        
        logger.info(f"Successfully parsed JSON with {len(extracted_data)} keys")
        return extracted_data
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        logger.error(f"Raw response: {response.text[:500]}...")
        raise ValueError(f"Failed to parse JSON response: {e}")
    except Exception as e:
        logger.error(f"LLM processing failed: {e}")
        raise

def build_master_prompt(pdf_text: str, template_type: str) -> str:
    """
    Dynamically selects and returns the master prompt based on the template type.
    
    Args:
        pdf_text: Extracted text from PDF
        template_type: Template type
        
    Returns:
        Complete prompt string
    """
    if template_type == "Extraction Template 1":
        return build_prompt_for_template_1(pdf_text)
    elif template_type == "Extraction Template 2":
        return build_prompt_for_template_2(pdf_text)
    else:
        raise ValueError("Invalid template type specified.")

def build_prompt_for_template_1(pdf_text: str) -> str:
    """
    Hyper-specific prompt for Extraction Template 1 with exhaustive examples.
    """
    return f"""
**Role:** You are a meticulous financial data analyst. Your task is to perform a deep and exhaustive extraction of data from a financial report and structure it into a JSON format that EXACTLY matches the schema for 'Extraction Template 1'.

**Core Instructions:**
1. Analyze the entire text provided.
2. You MUST populate every field for every sheet in the JSON schema. If a value is not found, you MUST use `null`.
3. For all sheets structured as key-value pairs (e.g., 'Fund Data', 'Fund Financial Position'), the row object MUST have a "Data Point" key and a "Value - Current Period" key.
4. All monetary values must be converted to base units (e.g., '$12.5 million' becomes `12500000`).
5. Your output must be a single, valid JSON object and nothing else. Follow the schema with absolute precision.

**JSON Output Schema for Template 1:**
{{
  "Doc Summary": [{{"#": 1, "Tab": "Fund Data", "Description": "..."}}],
  "Fund Data": [{{"Data Point": "Fund Name", "Value - Current Period": "..."}}, {{"Data Point": "Fund Currency", "Value - Current Period": "..."}}],
  "Fund Manager": [{{"Data Point": "Management Company", "Value - Current Period": "..."}}],
  "Fund Financial Position": [{{"Data Point": "Total Commitment", "Value - Current Period": 0}}, {{"Data Point": "Paid In Capital", "Value - Current Period": 0}}],
  "LP cashflows": [{{"Transaction Date": "YYYY-MM-DD", "Transaction comment": "...", "Contributions": 0, "Distributions": 0}}],
  "Fund Companies": [{{"Company": "...", "Company Type": "Private", "GICS Industry": "...", "Description": "..."}}],
  "Initial Investments": [{{"Company": "...", "Investment Date": "YYYY-MM-DD", "Instrument Type": "...", "Initial Investment": 0}}],
  "Company Investment Positions": [{{"Company": "...", "Investment Status": "Unrealized", "Instrument Type": "...", "Invested Capital [B]": 0, "Unrealized Value [D]": 0}}],
  "Company Valuation": [{{"Company": "...", "Last Valuation Date": "YYYY-MM-DD", "Enterprise Value [C]": 0, "Net Debt [D]": 0}}],
  "Company Financials": [{{"Company": "...", "Operating Data Date": "YYYY-MM-DD", "LTM Revenue": 0, "LTM EBITDA": 0}}]
}}

**--- START OF EXHAUSTIVE EXAMPLE ---**

*Example Input Snippet:* "...Page 1: Real Estate Opportunity Fund 7... June 2025... Manager is Aurora Property Funds Management... Page 4: REOF7 closed its first round in March 2025 at $265 million... Page 5: Cumulative Paid-In -(Called) capital 106,000,000... Page 7: Springfield QLD, 123 Fictional Avenue... Total Inv. Cost $9,000,000... Unrealised Fair Value $9,300,000..."

*Expected JSON Output for Snippet:*
{{
  "Doc Summary": [],
  "Fund Data": [
    {{"Data Point": "Fund Name", "Value - Current Period": "Real Estate Opportunity Fund 7"}},
    {{"Data Point": "Fund Currency", "Value - Current Period": "AUD"}},
    {{"Data Point": "Fund Size", "Value - Current Period": 265000000}}
  ],
  "Fund Manager": [
    {{"Data Point": "Management Company", "Value - Current Period": "Aurora Property Funds Management Pty Limited"}}
  ],
  "Fund Financial Position": [
    {{"Data Point": "Paid In Capital", "Value - Current Period": 106000000}}
  ],
  "LP cashflows": [],
  "Fund Companies": [
    {{"Company": "Springfield QLD, 123 Fictional Avenue", "Company Type": "Private", "GICS Industry": "Real Estate", "Description": "Development of a 15,000 sqm site..."}}
  ],
  "Initial Investments": [],
  "Company Investment Positions": [
    {{"Company": "Springfield QLD, 123 Fictional Avenue", "Investment Status": "Unrealized", "Instrument Type": "Senior Loan", "Invested Capital [B]": 9000000, "Unrealized Value [D]": 9300000}}
  ],
  "Company Valuation": [],
  "Company Financials": []
}}

**--- END OF EXAMPLE ---**

**Input Text from New PDF:**
{pdf_text}
"""

def build_prompt_for_template_2(pdf_text: str) -> str:
    """
    Hyper-specific prompt for Extraction Template 2 with source citation rules.
    """
    return f"""
**Role:** You are a world-class financial analyst. Your task is to extract data from a financial document and structure it into a JSON format that EXACTLY matches the schema and content style of 'Extraction Template 2'.

**Core Instructions:**
1. Analyze the entire text provided.
2. You MUST populate every field for every sheet in the JSON schema. If a value is not found, you MUST use `null`.
3. **CRITICAL SOURCE CITATION RULE**: For the 'Portfolio Summary' sheet, the `Value` field MUST be a single string formatted as: `"data|Page X, 'direct quote from text'"`
4. All monetary values must be converted to base units (e.g., '$265 million' becomes `265000000`).
5. Your output must be a single, valid JSON object. Follow the schema with absolute precision.

**JSON Output Schema for Template 2:**
{{
  "Doc Summary": [{{"#": 1, "Tab": "Portfolio Summary", "Description": "..."}}],
  "Portfolio Summary": [{{"Field": "General Partner", "Value": "data|Page X, '...'"}}, {{"Field": "Assets Under Management", "Value": "data|Page X, '...'"}}],
  "Schedule of Investments": [{{"#": 1, "Company": "...", "Fund": "...", "Reported Date": "YYYY-MM-DD", "Total Invested (A)": 0, "Reported Value (C)": 0}}],
  "Statement of Operations": [{{"Period": "...", "Total income": 0, "Total expenses": 0}}],
  "Statement of Cashflows": [{{"Description": "Current Period", "Net cash provided by/(used in) operating activities": 0}}],
  "PCAP Statement": [{{"Description": "Total Fund - QTD", "Beginning NAV - Net of Incentive Allocation": 0}}],
  "Portfolio Company profile": [{{"#": 1, "Company Name": "...", "Initial Investment Date": "YYYY-MM-DD", "Industry": "...", "Invested Capital": 0}}],
  "Portfolio Company Financials": [{{"Company": "...", "Operating Data Date": "YYYY-MM-DD", "LTM Revenue (CP)": 0, "LTM EBITDA (CP)": 0}}],
  "Footnotes": [{{"Note #": 1, "Note Header": "...", "Description": "..."}}]
}}

**--- START OF EXHAUSTIVE EXAMPLE ---**

*Example Input Snippet:* "...Page 3: Manager is Aurora Property Funds Management... Page 4: REOF7 closed at $265 million... 15 loans... Page 5: Cumulative Paid-In capital 106,000,000... Page 7: Springfield QLD, 123 Fictional Avenue... Total Inv. Cost $9,000,000... Unrealised Fair Value $9,300,000... Page 11: Development of a 15,000 sqm site..."

*Expected JSON Output for Snippet:*
{{
  "Doc Summary": [],
  "Portfolio Summary": [
    {{"Field": "General Partner", "Value": "Aurora Property Funds Management Pty Limited|Page 3, 'Manager is Aurora Property Funds Management'"}},
    {{"Field": "Assets Under Management", "Value": "265000000|Page 4, 'REOF7 closed its first round in March 2025 at $265 million'"}},
    {{"Field": "Active Portfolio Companies", "Value": "15|Page 4, 'portfolio to 15 loans'"}}
  ],
  "Schedule of Investments": [
    {{"#": 1, "Company": "Springfield QLD, 123 Fictional Avenue", "Fund": "Real Estate Opportunity Fund 7", "Reported Date": "2025-06-30", "Total Invested (A)": 9000000, "Reported Value (C)": 9300000}}
  ],
  "Statement of Operations": [],
  "Statement of Cashflows": [],
  "PCAP Statement": [],
  "Portfolio Company profile": [
    {{"#": 1, "Company Name": "Springfield QLD, 123 Fictional Avenue", "Initial Investment Date": "2025-03-01", "Industry": "Real Estate", "Invested Capital": 9000000}}
  ],
  "Portfolio Company Financials": [],
  "Footnotes": []
}}

**--- END OF EXAMPLE ---**

**Input Text from New PDF:**
{pdf_text}
"""

def create_excel_from_data(extracted_data: dict, template_type: str) -> io.BytesIO:
    """
    Create Excel file from extracted data and return as BytesIO buffer
    
    Args:
        extracted_data: Dictionary containing extracted data
        template_type: Template type used
        
    Returns:
        BytesIO buffer containing Excel file
    """
    try:
        # Import here to avoid circular imports
        from app.excel_formatter import create_formatted_excel_buffer
        
        return create_formatted_excel_buffer(extracted_data, template_type)
    except Exception as e:
        logger.error(f"Excel creation failed: {e}")
        raise ValueError(f"Failed to create Excel file: {e}")
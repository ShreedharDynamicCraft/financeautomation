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
                            table_text = "\n".join(["\t".join([str(cell) if cell else "" for cell in row]) for row in table])
                            text_parts.append(f"--- Table {table_num + 1} on Page {page_num + 1} ---\n{table_text}")
            
            if text_parts:
                logger.info(f"pdfplumber extracted text from {len(text_parts)} sections")
                return "\n\n".join(text_parts)
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")
        
        if not text_parts:
            raise ValueError("Could not extract any text from the PDF file")
            
    except Exception as e:
        logger.error(f"PDF text extraction failed: {e}")
        raise

def get_data_from_llm(pdf_text: str, template_type: str) -> Dict[str, Any]:
    """
    Calls the Gemini API with the correct master prompt to extract data.
    
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
        logger.error(f"Raw response: {response.text if 'response' in locals() else 'No response'}")
        raise ValueError(f"Invalid JSON response from LLM: {e}")
    except Exception as e:
        logger.error(f"LLM processing error: {e}")
        raise ValueError(f"LLM processing failed: {e}")

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
        return f"""
**Role:** You are a meticulous financial data analyst. Your task is to perform a deep extraction of data from a private equity fund report and structure it into a highly detailed JSON format corresponding to 'Extraction Template 1'.

**Core Instructions:**
1. Analyze the complete text provided from the financial report.
2. Populate the JSON schema below. Each main key in the JSON corresponds to a specific tab in the Excel template.
3. For sheets like 'Fund Data', the JSON object for each row should have a "Data Point" key and a "Value - Current Period" key.
4. Convert all monetary values to base units (e.g., '$12.5 million' should become `12500000`). If a value is not found, use `null`.
5. Extract ALL companies mentioned in investment positions, even if some data is incomplete.
6. For dates, use ISO format (YYYY-MM-DD) where possible.
7. Your final output MUST be a single, valid JSON object and nothing else.

**JSON Output Schema for Template 1:**
{{
  "Fund Data": [
    {{"Data Point": "Fund Name", "Value - Current Period": "..."}},
    {{"Data Point": "Fund Currency", "Value - Current Period": "..."}},
    {{"Data Point": "Fund Vintage Year", "Value - Current Period": "..."}},
    {{"Data Point": "Fund Size", "Value - Current Period": 0}},
    {{"Data Point": "Management Fee", "Value - Current Period": "..."}},
    {{"Data Point": "Carried Interest", "Value - Current Period": "..."}},
    {{"Data Point": "Fund Status", "Value - Current Period": "..."}},
    {{"Data Point": "Investment Period End", "Value - Current Period": "..."}},
    {{"Data Point": "Fund Term", "Value - Current Period": "..."}},
    {{"Data Point": "NAV Date", "Value - Current Period": "..."}}
  ],
  "Fund Manager": [
    {{"Data Point": "Management Company", "Value - Current Period": "..."}},
    {{"Data Point": "General Partner", "Value - Current Period": "..."}},
    {{"Data Point": "Contact Person", "Value - Current Period": "..."}},
    {{"Data Point": "Address", "Value - Current Period": "..."}},
    {{"Data Point": "Phone", "Value - Current Period": "..."}},
    {{"Data Point": "Email", "Value - Current Period": "..."}},
    {{"Data Point": "Investment Strategy", "Value - Current Period": "..."}}
  ],
  "Company Investment Positions": [
    {{
      "Company": "...",
      "Industry": "...",
      "Country": "...",
      "Investment Date": "...",
      "Instrument Type": "...",
      "Ownership Percentage": 0,
      "Number of Shares": 0,
      "Invested Capital [B]": 0,
      "Additional Investments [C]": 0,
      "Total Invested [D=B+C]": 0,
      "Unrealized Value [E]": 0,
      "Realized Value [F]": 0,
      "Total Value [G=E+F]": 0,
      "Multiple [H=G/D]": 0,
      "IRR": 0,
      "Status": "..."
    }}
  ],
  "Financial Summary": [
    {{"Data Point": "Total Committed Capital", "Value - Current Period": 0}},
    {{"Data Point": "Total Called Capital", "Value - Current Period": 0}},
    {{"Data Point": "Total Invested Capital", "Value - Current Period": 0}},
    {{"Data Point": "Total Unrealized Value", "Value - Current Period": 0}},
    {{"Data Point": "Total Realized Value", "Value - Current Period": 0}},
    {{"Data Point": "Total Portfolio Value", "Value - Current Period": 0}},
    {{"Data Point": "Cash and Cash Equivalents", "Value - Current Period": 0}},
    {{"Data Point": "Net Asset Value", "Value - Current Period": 0}},
    {{"Data Point": "Gross IRR", "Value - Current Period": 0}},
    {{"Data Point": "Net IRR", "Value - Current Period": 0}},
    {{"Data Point": "Gross Multiple", "Value - Current Period": 0}},
    {{"Data Point": "Net Multiple", "Value - Current Period": 0}}
  ]
}}

**Input Text from PDF:**
{pdf_text}
"""

    elif template_type == "Extraction Template 2":
        return f"""
**Role:** You are an expert financial analyst. Your task is to extract key summary information from a fund's report and structure it into a specific JSON format corresponding to 'Extraction Template 2'.

**Core Instructions:**
1. Analyze the complete text provided from the financial report.
2. Extract the data required to populate the JSON schema below.
3. For the 'Portfolio Summary' sheet, the JSON object for each row should have a "Data Points" key and a "Value - Current Period" key.
4. For tabular sheets like 'Schedule of Investments', the value for each key should be an array of objects, where each object represents a row.
5. Convert all monetary values to base units (e.g., '$265 million' should become `265000000`). If a value is not found, use `null`.
6. Extract ALL investments mentioned, even if some data is incomplete.
7. For dates, use ISO format (YYYY-MM-DD) where possible.
8. Your final output MUST be a single, valid JSON object and nothing else.

**JSON Output Schema for Template 2:**
{{
  "Portfolio Summary": [
    {{"Data Points": "Fund Name", "Value - Current Period": "..."}},
    {{"Data Points": "General Partner", "Value - Current Period": "..."}},
    {{"Data Points": "Assets Under Management", "Value - Current Period": 0}},
    {{"Data Points": "Portfolio Companies", "Value - Current Period": 0}},
    {{"Data Points": "Investment Period", "Value - Current Period": "..."}},
    {{"Data Points": "Vintage Year", "Value - Current Period": "..."}},
    {{"Data Points": "Fund Size", "Value - Current Period": 0}},
    {{"Data Points": "Called Capital", "Value - Current Period": 0}},
    {{"Data Points": "Remaining Commitments", "Value - Current Period": 0}},
    {{"Data Points": "Net Asset Value", "Value - Current Period": 0}},
    {{"Data Points": "Gross IRR", "Value - Current Period": 0}},
    {{"Data Points": "Net IRR", "Value - Current Period": 0}},
    {{"Data Points": "Total Value Multiple", "Value - Current Period": 0}},
    {{"Data Points": "Reporting Date", "Value - Current Period": "..."}}
  ],
  "Schedule of Investments": [
    {{
      "Company": "...",
      "Fund": "...",
      "Industry": "...",
      "Location": "...",
      "Investment Date": "...",
      "Reported Date": "...",
      "Investment Type": "...",
      "Total Invested (A)": 0,
      "Realized Value (B)": 0,
      "Reported Value (C)": 0,
      "Total Value (D = B + C)": 0,
      "Multiple (E = D / A)": 0,
      "Ownership %": 0,
      "Status": "..."
    }}
  ],
  "Performance Metrics": [
    {{"Data Points": "Since Inception IRR", "Value - Current Period": 0}},
    {{"Data Points": "3-Year IRR", "Value - Current Period": 0}},
    {{"Data Points": "1-Year IRR", "Value - Current Period": 0}},
    {{"Data Points": "Total Value Multiple", "Value - Current Period": 0}},
    {{"Data Points": "Realized Multiple", "Value - Current Period": 0}},
    {{"Data Points": "Unrealized Multiple", "Value - Current Period": 0}},
    {{"Data Points": "Cash Flow Multiple", "Value - Current Period": 0}},
    {{"Data Points": "Portfolio Beta", "Value - Current Period": 0}},
    {{"Data Points": "Sharpe Ratio", "Value - Current Period": 0}},
    {{"Data Points": "Maximum Drawdown", "Value - Current Period": 0}}
  ]
}}

**Input Text from PDF:**
{pdf_text}
"""
    else:
        raise ValueError("Invalid template type specified.")

def create_excel_from_data(data: Dict[str, Any], template_type: str) -> io.BytesIO:
    """
    Create Excel file from extracted data
    
    Args:
        data: Dictionary containing extracted data
        template_type: Template type used
        
    Returns:
        BytesIO buffer containing Excel file
    """
    try:
        logger.info(f"Creating Excel file for {template_type}")
        
        # Create Excel writer
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Create sheets based on data keys
            for sheet_name, sheet_data in data.items():
                if not sheet_data:
                    logger.warning(f"No data for sheet: {sheet_name}")
                    continue
                
                try:
                    # Convert to DataFrame
                    if isinstance(sheet_data, list) and len(sheet_data) > 0:
                        df = pd.DataFrame(sheet_data)
                        
                        # Clean sheet name (Excel has limitations)
                        clean_sheet_name = sheet_name.replace("/", "_").replace("\\", "_")[:31]
                        
                        # Write to Excel
                        df.to_excel(writer, sheet_name=clean_sheet_name, index=False)
                        
                        # Get workbook and worksheet for formatting
                        workbook = writer.book
                        worksheet = writer.sheets[clean_sheet_name]
                        
                        # Auto-adjust column widths
                        for column in worksheet.columns:
                            max_length = 0
                            column_letter = column[0].column_letter
                            
                            for cell in column:
                                try:
                                    if len(str(cell.value)) > max_length:
                                        max_length = len(str(cell.value))
                                except:
                                    pass
                            
                            adjusted_width = min(max_length + 2, 50)
                            worksheet.column_dimensions[column_letter].width = adjusted_width
                        
                        # Style headers
                        from openpyxl.styles import Font, PatternFill, Alignment
                        
                        header_font = Font(bold=True, color="FFFFFF")
                        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                        center_alignment = Alignment(horizontal="center", vertical="center")
                        
                        for cell in worksheet[1]:
                            cell.font = header_font
                            cell.fill = header_fill
                            cell.alignment = center_alignment
                        
                        logger.info(f"Created sheet '{clean_sheet_name}' with {len(df)} rows")
                        
                    else:
                        logger.warning(f"Invalid data format for sheet: {sheet_name}")
                        
                except Exception as e:
                    logger.error(f"Error creating sheet {sheet_name}: {e}")
                    continue
            
            # Add a summary sheet
            try:
                summary_data = {
                    "Metric": ["Template Used", "Total Sheets", "Processing Date", "File Version"],
                    "Value": [template_type, len(data), pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"), "1.0"]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name="Summary", index=False)
                
                # Format summary sheet
                summary_sheet = writer.sheets["Summary"]
                for column in summary_sheet.columns:
                    max_length = max(len(str(cell.value)) for cell in column)
                    column_letter = column[0].column_letter
                    summary_sheet.column_dimensions[column_letter].width = max_length + 2
                
                logger.info("Created summary sheet")
                
            except Exception as e:
                logger.warning(f"Could not create summary sheet: {e}")
        
        buffer.seek(0)
        logger.info(f"Excel file created successfully, size: {len(buffer.getvalue())} bytes")
        return buffer
        
    except Exception as e:
        logger.error(f"Excel creation failed: {e}")
        raise ValueError(f"Failed to create Excel file: {e}")
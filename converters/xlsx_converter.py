import pandas as pd
import logging
import os
import re

logger = logging.getLogger(__name__)

def convert_xlsx_to_markdown(file_path, use_llm=False):
    """
    Convert Excel file to Markdown
    
    Args:
        file_path (str): Path to the Excel file
        use_llm (bool): Whether to use LLM enhancement (not implemented)
        
    Returns:
        str: Markdown content
    """
    logger.debug(f"Converting Excel file: {file_path}")
    
    try:
        # Get the filename without extension for use as title
        file_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        
        # Read the Excel file 
        xls = pd.ExcelFile(file_path)
        
        # Process all sheets and combine into one markdown string
        markdown_text = f"# {file_name_without_ext}\n\n"
        
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Add sheet name as heading
            markdown_text += f"## Sheet: {sheet_name}\n\n"
            
            # Check if dataframe is empty
            if df.empty:
                markdown_text += "*No data in this sheet*\n\n"
                continue
            
            # Convert dataframe to markdown table
            markdown_table = df.to_markdown(index=False)
            if markdown_table:
                markdown_text += markdown_table + "\n\n"
            else:
                markdown_text += "*Unable to convert sheet data to markdown*\n\n"
        
        # Clean up multiple newlines
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        
        if use_llm:
            logger.info("LLM enhancement requested but not implemented for Excel")
        
        return markdown_text
    
    except Exception as e:
        logger.error(f"Error converting Excel to Markdown: {str(e)}")
        raise Exception(f"Excel conversion error: {str(e)}")
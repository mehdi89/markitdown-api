import pandas as pd
import logging
import os
import re

logger = logging.getLogger(__name__)

def convert_csv_to_markdown(file_path, use_llm=False):
    """
    Convert CSV file to Markdown
    
    Args:
        file_path (str): Path to the CSV file
        use_llm (bool): Whether to use LLM enhancement (not implemented)
        
    Returns:
        str: Markdown content
    """
    logger.debug(f"Converting CSV file: {file_path}")
    
    try:
        # Get the filename without extension for use as title
        file_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        
        # Read the CSV file
        try:
            df = pd.read_csv(file_path)
        except Exception as csv_error:
            # Try different encodings if default fails
            try:
                df = pd.read_csv(file_path, encoding='latin1')
            except Exception:
                try:
                    df = pd.read_csv(file_path, encoding='cp1252')
                except Exception:
                    # If all else fails, try with engine='python' which can handle more formats
                    df = pd.read_csv(file_path, engine='python')
        
        # Start with a title
        markdown_text = f"# {file_name_without_ext}\n\n"
        
        # Check if dataframe is empty
        if df.empty:
            markdown_text += "*No data in this CSV file*\n\n"
        else:
            # Get basic statistics
            markdown_text += f"## Overview\n\n"
            markdown_text += f"- **Rows**: {len(df)}\n"
            markdown_text += f"- **Columns**: {len(df.columns)}\n\n"
            
            # If there are too many rows, show a limited preview
            if len(df) > 100:
                markdown_text += f"*Showing first 100 rows of {len(df)} total rows*\n\n"
                markdown_text += df.head(100).to_markdown(index=False) + "\n\n"
            else:
                markdown_text += df.to_markdown(index=False) + "\n\n"
        
        # Clean up multiple newlines
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        
        if use_llm:
            logger.info("LLM enhancement requested but not implemented for CSV")
        
        return markdown_text
    
    except Exception as e:
        logger.error(f"Error converting CSV to Markdown: {str(e)}")
        raise Exception(f"CSV conversion error: {str(e)}")
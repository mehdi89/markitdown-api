import logging
import os
import re
from docx import Document

logger = logging.getLogger(__name__)

def convert_docx_to_markdown(file_path, use_llm=False):
    """
    Convert DOCX file to Markdown
    
    Args:
        file_path (str): Path to the DOCX file
        use_llm (bool): Whether to use LLM enhancement (not implemented)
        
    Returns:
        str: Markdown content
    """
    logger.debug(f"Converting DOCX file: {file_path}")
    
    try:
        # Get the filename without extension for use as title
        file_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        
        # Open the document
        doc = Document(file_path)
        
        # Start with a title
        markdown_text = f"# {file_name_without_ext}\n\n"
        
        # Process paragraphs - check for headings based on style
        for para in doc.paragraphs:
            if not para.text.strip():
                continue
            
            # Check if paragraph is a heading
            if para.style.name.startswith('Heading'):
                # Extract heading level from style name
                try:
                    level = int(para.style.name.replace('Heading', ''))
                except ValueError:
                    level = 2  # Default to heading level 2 if we can't parse level
                
                # Add appropriate heading markers
                markdown_text += f"{'#' * (level + 1)} {para.text.strip()}\n\n"
            else:
                # Regular paragraph
                markdown_text += f"{para.text.strip()}\n\n"
        
        # Process tables
        for table in doc.tables:
            # Count cells in the first row to determine columns
            if not table.rows:
                continue
                
            # Get all cells from first row for headers
            headers = []
            for cell in table.rows[0].cells:
                headers.append(cell.text.strip())
            
            # Add table headers
            markdown_text += "| " + " | ".join(headers) + " |\n"
            markdown_text += "| " + " | ".join(["---"] * len(headers)) + " |\n"
            
            # Add data rows (skip the header row)
            for row in table.rows[1:]:
                cells = []
                for cell in row.cells:
                    cells.append(cell.text.strip())
                markdown_text += "| " + " | ".join(cells) + " |\n"
            
            markdown_text += "\n"
        
        # Clean up multiple newlines
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        
        if use_llm:
            logger.info("LLM enhancement requested but not implemented for DOCX")
        
        return markdown_text
    
    except Exception as e:
        logger.error(f"Error converting DOCX to Markdown: {str(e)}")
        raise Exception(f"DOCX conversion error: {str(e)}")
import logging
import os
import re
import PyPDF2

logger = logging.getLogger(__name__)

def convert_pdf_to_markdown(file_path, use_llm=False):
    """
    Convert PDF file to Markdown
    
    Args:
        file_path (str): Path to the PDF file
        use_llm (bool): Whether to use LLM enhancement (not implemented)
        
    Returns:
        str: Markdown content
    """
    logger.debug(f"Converting PDF file: {file_path}")
    
    try:
        # Get the filename without extension for use as title
        file_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        
        # Start with a title
        markdown_text = f"# {file_name_without_ext}\n\n"
        
        # Open the PDF file
        with open(file_path, 'rb') as pdf_file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Get the number of pages
            num_pages = len(pdf_reader.pages)
            
            # Add a summary of the PDF
            markdown_text += f"## PDF Overview\n\n"
            markdown_text += f"- **Pages**: {num_pages}\n\n"
            
            # Extract text from each page
            markdown_text += f"## Content\n\n"
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                if text.strip():
                    markdown_text += f"### Page {page_num + 1}\n\n"
                    
                    # Process the extracted text
                    # Split into paragraphs
                    paragraphs = text.split('\n\n')
                    
                    for paragraph in paragraphs:
                        # Skip empty paragraphs
                        if not paragraph.strip():
                            continue
                            
                        # Check if this might be a heading (short, all caps or ends with colon)
                        lines = paragraph.split('\n')
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                                
                            # Potential heading detection
                            if (len(line) < 50 and (line.isupper() or line.rstrip().endswith(':'))):
                                markdown_text += f"#### {line}\n\n"
                            else:
                                # Regular paragraph
                                markdown_text += f"{line}\n\n"
                    
                    markdown_text += "\n"
                else:
                    markdown_text += f"### Page {page_num + 1}\n\n"
                    markdown_text += "*No extractable text found on this page (might be an image or scanned content)*\n\n"
        
        # Clean up multiple newlines
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        
        if use_llm:
            logger.info("LLM enhancement requested but not implemented for PDF")
        
        return markdown_text
    
    except Exception as e:
        logger.error(f"Error converting PDF to Markdown: {str(e)}")
        raise Exception(f"PDF conversion error: {str(e)}")
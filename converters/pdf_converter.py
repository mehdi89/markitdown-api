import PyPDF2
import re
import logging

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
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            markdown_text = ""
            
            # Extract text from each page
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                
                if text:
                    # Add page number as heading
                    markdown_text += f"## Page {page_num + 1}\n\n"
                    
                    # Process the extracted text into paragraphs
                    paragraphs = re.split(r'\n\s*\n', text)
                    for paragraph in paragraphs:
                        # Skip empty paragraphs
                        if not paragraph.strip():
                            continue
                        
                        # Check if this might be a heading (all caps, short line)
                        if len(paragraph) < 100 and paragraph.isupper():
                            markdown_text += f"### {paragraph.strip()}\n\n"
                        # Check if this might be a list item
                        elif re.match(r'^\s*[•\-\*]\s', paragraph):
                            # Convert bullet points
                            lines = paragraph.split('\n')
                            for line in lines:
                                if re.match(r'^\s*[•\-\*]\s', line):
                                    markdown_text += f"* {line.strip()[1:].strip()}\n"
                                else:
                                    markdown_text += f"{line.strip()}\n"
                            markdown_text += "\n"
                        # Check if this might be a numbered list
                        elif re.match(r'^\s*\d+[\.\)]\s', paragraph):
                            # Convert numbered lists
                            lines = paragraph.split('\n')
                            for line in lines:
                                if re.match(r'^\s*\d+[\.\)]\s', line):
                                    number_match = re.match(r'^\s*(\d+)[\.\)]\s', line)
                                    if number_match:
                                        number = number_match.group(1)
                                        markdown_text += f"{number}. {line.strip()[len(number)+1:].strip()}\n"
                                else:
                                    markdown_text += f"{line.strip()}\n"
                            markdown_text += "\n"
                        else:
                            # Regular paragraph
                            markdown_text += f"{paragraph.strip()}\n\n"
            
            # Clean up multiple newlines and spaces
            markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
            markdown_text = re.sub(r' {2,}', ' ', markdown_text)
            
            if use_llm:
                logger.info("LLM enhancement requested but not implemented for PDF")
            
            return markdown_text
    
    except Exception as e:
        logger.error(f"Error converting PDF to Markdown: {str(e)}")
        raise Exception(f"PDF conversion error: {str(e)}")

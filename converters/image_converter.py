import pytesseract
from PIL import Image
import os
import logging
import re

logger = logging.getLogger(__name__)

def convert_image_to_markdown(file_path, use_llm=False):
    """
    Convert Image file to Markdown using OCR
    
    Args:
        file_path (str): Path to the Image file
        use_llm (bool): Whether to use LLM enhancement (not implemented)
        
    Returns:
        str: Markdown content
    """
    logger.debug(f"Converting Image file: {file_path}")
    
    try:
        # Get the filename without extension for use as title
        file_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        
        # Start with a title
        markdown_text = f"# {file_name_without_ext}\n\n"
        
        # Add image reference
        markdown_text += f"![Image: {file_name}]({file_path})\n\n"
        
        # Perform OCR to extract text
        markdown_text += "## Extracted Text\n\n"
        
        try:
            # Open the image
            img = Image.open(file_path)
            
            # Use PyTesseract to extract text
            extracted_text = pytesseract.image_to_string(img)
            
            if extracted_text.strip():
                # Process the extracted text to identify potential structure
                lines = extracted_text.split('\n')
                current_paragraph = ""
                
                for line in lines:
                    # Skip empty lines
                    if not line.strip():
                        if current_paragraph:
                            markdown_text += current_paragraph + "\n\n"
                            current_paragraph = ""
                        continue
                    
                    # Check if this might be a heading (all caps, short line)
                    if len(line) < 50 and line.isupper():
                        if current_paragraph:
                            markdown_text += current_paragraph + "\n\n"
                            current_paragraph = ""
                        markdown_text += f"### {line.strip()}\n\n"
                    
                    # Check if this might be a bullet point
                    elif line.strip().startswith(('•', '-', '*')):
                        if current_paragraph:
                            markdown_text += current_paragraph + "\n\n"
                            current_paragraph = ""
                        markdown_text += f"{line.strip()}\n"
                    
                    # Append to current paragraph
                    else:
                        if current_paragraph:
                            current_paragraph += " " + line.strip()
                        else:
                            current_paragraph = line.strip()
                
                # Add the last paragraph if any
                if current_paragraph:
                    markdown_text += current_paragraph + "\n\n"
            else:
                markdown_text += "*No text could be extracted from this image*\n\n"
        
        except Exception as ocr_error:
            logger.error(f"OCR processing error: {str(ocr_error)}")
            markdown_text += "*Error extracting text from image*\n\n"
        
        # Clean up multiple newlines
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        
        if use_llm:
            logger.info("LLM enhancement requested but not implemented for Image")
        
        return markdown_text
    
    except Exception as e:
        logger.error(f"Error converting Image to Markdown: {str(e)}")
        raise Exception(f"Image conversion error: {str(e)}")
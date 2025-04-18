import logging
import os
import re

logger = logging.getLogger(__name__)

def convert_txt_to_markdown(file_path, use_llm=False):
    """
    Convert plain text file to Markdown
    
    Args:
        file_path (str): Path to the text file
        use_llm (bool): Whether to use LLM enhancement (not implemented)
        
    Returns:
        str: Markdown content
    """
    logger.debug(f"Converting text file: {file_path}")
    
    try:
        # Get the filename without extension for use as title
        file_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        
        # Read the text file
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            text_content = file.read()
        
        # Start with a title
        markdown_text = f"# {file_name_without_ext}\n\n"
        
        # Process content - try to identify structure
        lines = text_content.split('\n')
        
        # Process each line
        current_paragraph = ""
        in_code_block = False
        in_list = False
        
        for line in lines:
            line = line.rstrip()
            
            # Skip empty lines but respect paragraph breaks
            if not line.strip():
                if current_paragraph:
                    markdown_text += current_paragraph + "\n\n"
                    current_paragraph = ""
                elif in_list:
                    in_list = False
                    markdown_text += "\n"
                continue
            
            # Check for potential code blocks (indented by 4+ spaces or tabs)
            if line.startswith('    ') or line.startswith('\t'):
                if not in_code_block and current_paragraph:
                    markdown_text += current_paragraph + "\n\n"
                    current_paragraph = ""
                
                if not in_code_block:
                    in_code_block = True
                    markdown_text += "```\n"
                
                markdown_text += line.lstrip() + "\n"
                continue
            
            # End code block if needed
            if in_code_block and not (line.startswith('    ') or line.startswith('\t')):
                in_code_block = False
                markdown_text += "```\n\n"
            
            # Check if this might be a heading (all caps, short line)
            if len(line) < 50 and line.isupper():
                if current_paragraph:
                    markdown_text += current_paragraph + "\n\n"
                    current_paragraph = ""
                markdown_text += f"## {line}\n\n"
                continue
            
            # Check if this might be a bullet point
            if line.strip().startswith(('•', '-', '*', '+')):
                if current_paragraph and not in_list:
                    markdown_text += current_paragraph + "\n\n"
                    current_paragraph = ""
                
                in_list = True
                markdown_text += line + "\n"
                continue
            
            # If we were in a list but this line doesn't start with a bullet
            if in_list and not line.strip().startswith(('•', '-', '*', '+')):
                in_list = False
                markdown_text += "\n"
            
            # Regular paragraph content
            if current_paragraph:
                # Check if this is a continuation of the paragraph
                if not line.endswith(('.', '!', '?', ':', ';')):
                    current_paragraph += " " + line
                else:
                    # End of sentence
                    current_paragraph += " " + line
                    markdown_text += current_paragraph + "\n\n"
                    current_paragraph = ""
            else:
                current_paragraph = line
        
        # Add any remaining paragraph
        if current_paragraph:
            markdown_text += current_paragraph + "\n\n"
        
        # End any open code block
        if in_code_block:
            markdown_text += "```\n\n"
        
        # Clean up multiple newlines
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        
        if use_llm:
            logger.info("LLM enhancement requested but not implemented for text files")
        
        return markdown_text
    
    except Exception as e:
        logger.error(f"Error converting text to Markdown: {str(e)}")
        raise Exception(f"Text conversion error: {str(e)}")
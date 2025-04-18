import re
import logging

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
    logger.debug(f"Converting TXT file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Simple heuristics to identify structure in plain text
        markdown_text = ""
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                markdown_text += "\n"
                i += 1
                continue
            
            # Check for headings (all caps, short line)
            if len(line) < 100 and line.isupper() and len(line) > 3:
                markdown_text += f"## {line}\n\n"
            
            # Check for numbered lists
            elif re.match(r'^\s*\d+[\.\)]\s', line):
                # This looks like a numbered list item
                markdown_text += line + "\n"
            
            # Check for bullet lists
            elif re.match(r'^\s*[\*\-\•]\s', line):
                # This looks like a bullet list item
                markdown_text += line + "\n"
            
            # Check for potential section titles (shorter lines followed by longer paragraphs)
            elif (i+1 < len(lines) and 
                  len(line) < 80 and 
                  len(lines[i+1].strip()) > 100):
                markdown_text += f"### {line}\n\n"
            
            # Regular paragraph
            else:
                # Check if this is part of a continuing paragraph
                if (i > 0 and 
                    lines[i-1].strip() and 
                    not re.match(r'^\s*[\*\-\•\d]', lines[i-1]) and
                    not re.match(r'^\s*[\*\-\•\d]', line)):
                    # Continue paragraph without extra newline
                    markdown_text += line + "\n"
                else:
                    # New paragraph
                    markdown_text += line + "\n\n"
            
            i += 1
        
        # Clean up multiple newlines
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        
        if use_llm:
            logger.info("LLM enhancement requested but not implemented for TXT")
        
        return markdown_text
    
    except Exception as e:
        logger.error(f"Error converting TXT to Markdown: {str(e)}")
        raise Exception(f"TXT conversion error: {str(e)}")

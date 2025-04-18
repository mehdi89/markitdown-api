import logging
import os
import re
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def convert_html_to_markdown(file_path, use_llm=False):
    """
    Convert HTML file to Markdown
    
    Args:
        file_path (str): Path to the HTML file
        use_llm (bool): Whether to use LLM enhancement (not implemented)
        
    Returns:
        str: Markdown content
    """
    logger.debug(f"Converting HTML file: {file_path}")
    
    try:
        # Get the filename without extension for use as title
        file_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        
        # Read the HTML file
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            html_content = file.read()
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Start with a title
        markdown_text = f"# {file_name_without_ext}\n\n"
        
        # Try to extract the HTML title if available
        title_tag = soup.find('title')
        if title_tag and title_tag.string and title_tag.string.strip():
            markdown_text = f"# {title_tag.string.strip()}\n\n"
        
        # Extract main content - typically from body, article, or main tags
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        if not main_content:
            main_content = soup
        
        # Process headings
        for heading_level in range(1, 7):
            for heading in main_content.find_all(f'h{heading_level}'):
                if heading.get_text().strip():
                    # Create the equivalent markdown heading with proper nesting
                    markdown_level = min(heading_level + 1, 6)  # adjust level to work under the main title
                    markdown_text += f"{'#' * markdown_level} {heading.get_text().strip()}\n\n"
        
        # Process paragraphs
        for paragraph in main_content.find_all('p'):
            if paragraph.get_text().strip():
                markdown_text += f"{paragraph.get_text().strip()}\n\n"
        
        # Process lists
        for ul in main_content.find_all('ul'):
            for li in ul.find_all('li'):
                if li.get_text().strip():
                    markdown_text += f"* {li.get_text().strip()}\n"
            markdown_text += "\n"
        
        for ol in main_content.find_all('ol'):
            for i, li in enumerate(ol.find_all('li'), 1):
                if li.get_text().strip():
                    markdown_text += f"{i}. {li.get_text().strip()}\n"
            markdown_text += "\n"
        
        # Process links
        for link in main_content.find_all('a', href=True):
            link_text = link.get_text().strip()
            href = link['href']
            if link_text and href:
                old_text = link.get_text()
                markdown_link = f"[{link_text}]({href})"
                html_content = html_content.replace(str(link), markdown_link)
        
        # Process images
        for img in main_content.find_all('img', src=True):
            alt_text = img.get('alt', 'Image')
            src = img['src']
            if src:
                markdown_text += f"![{alt_text}]({src})\n\n"
        
        # Process tables
        for table in main_content.find_all('table'):
            # Extract headers
            headers = []
            header_row = table.find('thead')
            if header_row:
                for th in header_row.find_all('th'):
                    headers.append(th.get_text().strip())
            
            if not headers and table.find('th'):
                for th in table.find_all('th'):
                    headers.append(th.get_text().strip())
            
            # Start table
            if headers:
                markdown_text += "| " + " | ".join(headers) + " |\n"
                markdown_text += "| " + " | ".join(["---"] * len(headers)) + " |\n"
            else:
                # If no headers were found, create dummy headers based on column count
                first_row = table.find('tr')
                if first_row:
                    col_count = len(first_row.find_all(['td', 'th']))
                    if col_count > 0:
                        markdown_text += "| " + " | ".join(["Column " + str(i+1) for i in range(col_count)]) + " |\n"
                        markdown_text += "| " + " | ".join(["---"] * col_count) + " |\n"
            
            # Add data rows
            rows = table.find_all('tr')
            for row in rows:
                # Skip if this row is part of the header
                if row.find_parent('thead'):
                    continue
                
                # Get cells
                cells = row.find_all(['td'])
                if cells:
                    cell_texts = [cell.get_text().strip() for cell in cells]
                    markdown_text += "| " + " | ".join(cell_texts) + " |\n"
            
            markdown_text += "\n"
        
        # Process code blocks
        for code in main_content.find_all('code'):
            if code.get_text().strip():
                is_inline = code.parent.name != 'pre'
                if is_inline:
                    markdown_text += f"`{code.get_text().strip()}`"
                else:
                    language = ""
                    if 'class' in code.attrs:
                        # Try to extract language from class like 'language-python'
                        for cls in code['class']:
                            if cls.startswith('language-'):
                                language = cls[9:]
                                break
                    
                    markdown_text += f"```{language}\n{code.get_text()}\n```\n\n"
        
        # Process blockquotes
        for blockquote in main_content.find_all('blockquote'):
            if blockquote.get_text().strip():
                # Split by lines and add '>' to each line
                quote_text = blockquote.get_text().strip()
                quote_lines = quote_text.split('\n')
                for line in quote_lines:
                    markdown_text += f"> {line}\n"
                markdown_text += "\n"
        
        # Clean up multiple newlines
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        
        if use_llm:
            logger.info("LLM enhancement requested but not implemented for HTML")
        
        return markdown_text
    
    except Exception as e:
        logger.error(f"Error converting HTML to Markdown: {str(e)}")
        raise Exception(f"HTML conversion error: {str(e)}")
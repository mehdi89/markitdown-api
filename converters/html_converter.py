from bs4 import BeautifulSoup
import markdown
import re
import logging

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
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements that we don't want to convert
        for script in soup(["script", "style"]):
            script.extract()
        
        # Process HTML elements to Markdown
        markdown_text = ""
        
        # Process headings
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                markdown_text += f"{'#' * i} {heading.get_text().strip()}\n\n"
        
        # Process paragraphs
        for p in soup.find_all('p'):
            markdown_text += f"{p.get_text().strip()}\n\n"
        
        # Process lists
        for ul in soup.find_all('ul'):
            for li in ul.find_all('li'):
                markdown_text += f"* {li.get_text().strip()}\n"
            markdown_text += "\n"
        
        for ol in soup.find_all('ol'):
            for i, li in enumerate(ol.find_all('li')):
                markdown_text += f"{i+1}. {li.get_text().strip()}\n"
            markdown_text += "\n"
        
        # Process links
        for a in soup.find_all('a'):
            href = a.get('href', '')
            text = a.get_text().strip()
            markdown_text += f"[{text}]({href})\n\n"
        
        # Process images
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            markdown_text += f"![{alt}]({src})\n\n"
        
        # Process code blocks
        for pre in soup.find_all('pre'):
            code = pre.get_text().strip()
            markdown_text += f"```\n{code}\n```\n\n"
        
        # Process inline code
        for code in soup.find_all('code'):
            if code.parent.name != 'pre':  # Skip if already in a pre block
                markdown_text += f"`{code.get_text().strip()}`\n\n"
        
        # Process blockquotes
        for blockquote in soup.find_all('blockquote'):
            lines = blockquote.get_text().strip().split('\n')
            for line in lines:
                markdown_text += f"> {line.strip()}\n"
            markdown_text += "\n"
        
        # Process tables (basic support)
        for table in soup.find_all('table'):
            # Headers
            headers = []
            for th in table.find_all('th'):
                headers.append(th.get_text().strip())
            
            if headers:
                markdown_text += "| " + " | ".join(headers) + " |\n"
                markdown_text += "| " + " | ".join(["---"] * len(headers)) + " |\n"
            
            # Rows
            for tr in table.find_all('tr'):
                row = []
                for td in tr.find_all('td'):
                    row.append(td.get_text().strip())
                if row:
                    markdown_text += "| " + " | ".join(row) + " |\n"
            
            markdown_text += "\n"
        
        # Clean up multiple newlines
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        
        if use_llm:
            logger.info("LLM enhancement requested but not implemented for HTML")
        
        return markdown_text
    
    except Exception as e:
        logger.error(f"Error converting HTML to Markdown: {str(e)}")
        raise Exception(f"HTML conversion error: {str(e)}")

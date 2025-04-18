import os
import logging
from flask import Flask, request, jsonify, render_template, flash
from werkzeug.utils import secure_filename
import uuid
import tempfile
import json

# Import converters
from converters.txt_converter import convert_txt_to_markdown
from converters.html_converter import convert_html_to_markdown

# Define placeholder converters until dependencies are resolved
def convert_pdf_to_markdown(file_path, use_llm=False):
    """Convert PDF to Markdown using basic text extraction"""
    try:
        import subprocess
        import re
        
        # Get the filename without extension for use as title
        file_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        
        # Start with a title
        markdown_text = f"# {file_name_without_ext}\n\n"
        
        try:
            # Try using Linux's pdftotext utility if available
            text = subprocess.check_output(["pdftotext", file_path, "-"], stderr=subprocess.DEVNULL).decode("utf-8", errors="replace")
            
            if text.strip():
                # Basic structure detection for the extracted text
                lines = text.split('\n')
                current_paragraph = ""
                in_list = False
                
                for line in lines:
                    line = line.strip()
                    
                    # Skip empty lines
                    if not line:
                        if current_paragraph:
                            markdown_text += current_paragraph + "\n\n"
                            current_paragraph = ""
                        elif in_list:
                            in_list = False
                            markdown_text += "\n"
                        continue
                    
                    # Check if this might be a heading (short, all caps or ends with colon)
                    if len(line) < 50 and (line.isupper() or line.rstrip().endswith(':')):
                        if current_paragraph:
                            markdown_text += current_paragraph + "\n\n"
                            current_paragraph = ""
                        markdown_text += f"## {line}\n\n"
                        continue
                    
                    # Check if this might be a bullet point
                    if line.startswith(('•', '-', '*')) and ' ' in line[1:3]:
                        if current_paragraph:
                            markdown_text += current_paragraph + "\n\n"
                            current_paragraph = ""
                        
                        in_list = True
                        markdown_text += f"{line}\n"
                        continue
                    
                    # If we were in a list but this line doesn't start with a bullet
                    if in_list and not line.startswith(('•', '-', '*')):
                        in_list = False
                        markdown_text += "\n"
                    
                    # Regular paragraph content
                    if current_paragraph:
                        current_paragraph += " " + line
                    else:
                        current_paragraph = line
                
                # Add the last paragraph if any
                if current_paragraph:
                    markdown_text += current_paragraph + "\n\n"
            else:
                markdown_text += "No text could be extracted from this PDF. It may contain only images or be protected.\n\n"
        except (subprocess.SubprocessError, FileNotFoundError):
            # If pdftotext isn't available, return a basic message
            markdown_text += f"## PDF Content\n\nThis PDF file requires additional tools for text extraction.\n\n"
            
            # Try to get basic info about the PDF
            try:
                # Use file command to get basic info
                info = subprocess.check_output(["file", file_path]).decode("utf-8")
                markdown_text += f"**File Info**: {info}\n\n"
            except:
                pass
        
        # Clean up multiple newlines
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        
        return markdown_text
        
    except Exception as e:
        logger.error(f"Error converting PDF to Markdown: {str(e)}")
        return f"# {os.path.basename(file_path)}\n\nError processing PDF file: {str(e)}"

def convert_docx_to_markdown(file_path, use_llm=False):
    """Convert DOCX to Markdown using basic extraction"""
    try:
        import zipfile
        import xml.etree.ElementTree as ET
        import re
        
        # Get the filename without extension for use as title
        file_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        
        # Start with a title
        markdown_text = f"# {file_name_without_ext}\n\n"
        
        # DOCX files are actually ZIP files containing XML
        try:
            with zipfile.ZipFile(file_path) as docx_zip:
                # Extract content XML
                if 'word/document.xml' in docx_zip.namelist():
                    content_xml = docx_zip.read('word/document.xml').decode('utf-8', errors='replace')
                    
                    # Parse XML
                    # Remove namespaces for easier parsing
                    content_xml = re.sub('xmlns="[^"]+"', '', content_xml)
                    root = ET.fromstring(content_xml)
                    
                    # Extract paragraphs
                    paragraphs = []
                    for p in root.findall('.//p'):
                        text = ""
                        for t in p.findall('.//t'):
                            if t.text:
                                text += t.text
                        if text.strip():
                            paragraphs.append(text.strip())
                    
                    # Process paragraphs to detect structure
                    for i, para in enumerate(paragraphs):
                        # Simple heuristic for headings
                        if len(para) < 100 and (para.isupper() or para.endswith(':')) and i < 20:
                            markdown_text += f"## {para}\n\n"
                        # Attempt to detect bullet points
                        elif para.startswith(('•', '-', '*', '○', '·')) and ' ' in para[1:3]:
                            markdown_text += f"{para}\n"
                        # Regular paragraph
                        else:
                            markdown_text += f"{para}\n\n"
                    
                    # Try to extract document properties for metadata
                    if 'docProps/core.xml' in docx_zip.namelist():
                        core_xml = docx_zip.read('docProps/core.xml').decode('utf-8', errors='replace')
                        core_xml = re.sub('xmlns="[^"]+"', '', core_xml)
                        core_root = ET.fromstring(core_xml)
                        
                        markdown_text += "## Document Information\n\n"
                        
                        # Extract creation date
                        created = core_root.find('.//created')
                        if created is not None and created.text:
                            markdown_text += f"**Created**: {created.text}\n\n"
                        
                        # Extract last modified date
                        modified = core_root.find('.//modified')
                        if modified is not None and modified.text:
                            markdown_text += f"**Last Modified**: {modified.text}\n\n"
                        
                        # Extract author
                        creator = core_root.find('.//creator')
                        if creator is not None and creator.text:
                            markdown_text += f"**Author**: {creator.text}\n\n"
                else:
                    markdown_text += "Could not locate document content in the DOCX file.\n\n"
        except zipfile.BadZipFile:
            markdown_text += "The DOCX file appears to be corrupt or invalid.\n\n"
        
        return markdown_text
    
    except Exception as e:
        logger.error(f"Error converting DOCX to Markdown: {str(e)}")
        return f"# {os.path.basename(file_path)}\n\nError processing DOCX file: {str(e)}"

def convert_xlsx_to_markdown(file_path, use_llm=False):
    """Convert XLSX to Markdown without external dependencies"""
    try:
        import zipfile
        import xml.etree.ElementTree as ET
        import re
        
        # Get the filename without extension for use as title
        file_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        
        # Start with a title
        markdown_text = f"# {file_name_without_ext}\n\n"
        
        # XLSX files are ZIP files with XML content
        try:
            with zipfile.ZipFile(file_path) as xlsx_zip:
                # First get the sheet names from workbook.xml
                sheets = []
                if 'xl/workbook.xml' in xlsx_zip.namelist():
                    workbook_xml = xlsx_zip.read('xl/workbook.xml').decode('utf-8', errors='replace')
                    workbook_xml = re.sub('xmlns="[^"]+"', '', workbook_xml)
                    wb_root = ET.fromstring(workbook_xml)
                    
                    for sheet in wb_root.findall('.//sheet'):
                        sheet_name = sheet.get('name', f"Sheet{len(sheets)+1}")
                        sheet_id = sheet.get('sheetId', str(len(sheets)+1))
                        sheets.append((sheet_name, sheet_id))
                else:
                    markdown_text += "Could not locate workbook structure in the Excel file.\n\n"
                    return markdown_text
                
                # Process each sheet
                for sheet_name, sheet_id in sheets:
                    markdown_text += f"## {sheet_name}\n\n"
                    
                    # Look for the corresponding sheet XML
                    sheet_path = f'xl/worksheets/sheet{sheet_id}.xml'
                    if sheet_path not in xlsx_zip.namelist():
                        # Try alternate path pattern
                        for path in xlsx_zip.namelist():
                            if path.startswith('xl/worksheets/sheet') and path.endswith('.xml'):
                                sheet_path = path
                                break
                    
                    if sheet_path in xlsx_zip.namelist():
                        sheet_xml = xlsx_zip.read(sheet_path).decode('utf-8', errors='replace')
                        sheet_xml = re.sub('xmlns="[^"]+"', '', sheet_xml)
                        sheet_root = ET.fromstring(sheet_xml)
                        
                        # Extract shared strings if available
                        shared_strings = {}
                        if 'xl/sharedStrings.xml' in xlsx_zip.namelist():
                            ss_xml = xlsx_zip.read('xl/sharedStrings.xml').decode('utf-8', errors='replace')
                            ss_xml = re.sub('xmlns="[^"]+"', '', ss_xml)
                            ss_root = ET.fromstring(ss_xml)
                            
                            for i, si in enumerate(ss_root.findall('.//si')):
                                text_parts = []
                                for t in si.findall('.//t'):
                                    if t.text:
                                        text_parts.append(t.text)
                                shared_strings[str(i)] = ''.join(text_parts)
                        
                        # Extract data from sheet
                        data = []
                        for row in sheet_root.findall('.//row'):
                            row_data = []
                            for cell in row.findall('.//c'):
                                cell_value = ""
                                # Get the value
                                v = cell.find('v')
                                if v is not None and v.text:
                                    # Check if this is a shared string
                                    if cell.get('t') == 's' and v.text in shared_strings:
                                        cell_value = shared_strings[v.text]
                                    else:
                                        cell_value = v.text
                                row_data.append(cell_value)
                            if row_data:
                                data.append(row_data)
                        
                        # Convert data to markdown table
                        if data:
                            # Determine max width of each column for padding
                            max_row_len = max(len(row) for row in data)
                            
                            # Use first row as headers or generate column labels
                            headers = data[0] if len(data) > 0 else [f"Column {i+1}" for i in range(max_row_len)]
                            
                            # Create table header
                            markdown_text += "| " + " | ".join(headers) + " |\n"
                            markdown_text += "| " + " | ".join(["---"] * len(headers)) + " |\n"
                            
                            # Add data rows (skip the header row)
                            for row in data[1:]:
                                # Ensure row has enough columns
                                if len(row) < len(headers):
                                    row = row + [""] * (len(headers) - len(row))
                                # Truncate if too many columns
                                row = row[:len(headers)]
                                # Escape pipe characters in cell content
                                row = [cell.replace("|", "\\|") for cell in row]
                                markdown_text += "| " + " | ".join(row) + " |\n"
                                
                            markdown_text += f"\n*Sheet contains {len(data)} rows*\n\n"
                        else:
                            markdown_text += "*No data in this sheet*\n\n"
                    else:
                        markdown_text += f"*Could not locate data for sheet {sheet_name}*\n\n"
            
        except zipfile.BadZipFile:
            markdown_text += "The Excel file appears to be corrupt or invalid.\n\n"
        
        return markdown_text
    
    except Exception as e:
        logger.error(f"Error converting XLSX to Markdown: {str(e)}")
        return f"# {os.path.basename(file_path)}\n\nError processing Excel file: {str(e)}"

def convert_pptx_to_markdown(file_path, use_llm=False):
    """Convert PowerPoint to Markdown without external dependencies"""
    try:
        import zipfile
        import xml.etree.ElementTree as ET
        import re
        
        # Get the filename without extension for use as title
        file_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        
        # Start with a title
        markdown_text = f"# {file_name_without_ext}\n\n"
        
        # PowerPoint files are ZIP files with XML content
        try:
            with zipfile.ZipFile(file_path) as pptx_zip:
                # Extract slide list from presentation.xml
                if 'ppt/presentation.xml' in pptx_zip.namelist():
                    presentation_xml = pptx_zip.read('ppt/presentation.xml').decode('utf-8', errors='replace')
                    presentation_xml = re.sub('xmlns="[^"]+"', '', presentation_xml)
                    pres_root = ET.fromstring(presentation_xml)
                    
                    # Find all slide references
                    slides = []
                    for slide_id_element in pres_root.findall('.//sldId'):
                        slide_id = slide_id_element.get('id', '0')
                        slide_rid = slide_id_element.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                        if slide_rid:
                            slides.append((slide_id, slide_rid))
                    
                    # Find relationship between rid and actual file
                    slide_paths = {}
                    if 'ppt/_rels/presentation.xml.rels' in pptx_zip.namelist():
                        rels_xml = pptx_zip.read('ppt/_rels/presentation.xml.rels').decode('utf-8', errors='replace')
                        rels_xml = re.sub('xmlns="[^"]+"', '', rels_xml)
                        rels_root = ET.fromstring(rels_xml)
                        
                        for rel in rels_root.findall('.//Relationship'):
                            rid = rel.get('Id')
                            target = rel.get('Target')
                            if rid and target and target.startswith('slides/slide'):
                                slide_paths[rid] = 'ppt/' + target
                    
                    # Process each slide
                    for slide_num, (slide_id, slide_rid) in enumerate(slides, 1):
                        markdown_text += f"## Slide {slide_num}\n\n"
                        
                        if slide_rid in slide_paths:
                            slide_path = slide_paths[slide_rid]
                            if slide_path in pptx_zip.namelist():
                                slide_xml = pptx_zip.read(slide_path).decode('utf-8', errors='replace')
                                slide_xml = re.sub('xmlns="[^"]+"', '', slide_xml)
                                slide_root = ET.fromstring(slide_xml)
                                
                                # Extract title if available
                                title_found = False
                                title_text = ""
                                for title in slide_root.findall('.//title'):
                                    text_parts = []
                                    for t in title.findall('.//t'):
                                        if t.text:
                                            text_parts.append(t.text)
                                    
                                    title_text = ' '.join(text_parts).strip()
                                    if title_text:
                                        markdown_text += f"### {title_text}\n\n"
                                        title_found = True
                                        break
                                
                                # Extract all text from shapes
                                text_list = []
                                for shape in slide_root.findall('.//sp'):
                                    shape_text = []
                                    for t in shape.findall('.//t'):
                                        if t.text:
                                            shape_text.append(t.text)
                                    
                                    # Skip if this was already processed as the title
                                    if title_found and len(shape_text) == 1 and shape_text[0] == title_text:
                                        continue
                                    
                                    # Process text content
                                    for text in shape_text:
                                        # Skip empty text
                                        if not text.strip():
                                            continue
                                            
                                        # Check if this looks like a bullet point
                                        if text.startswith(('•', '-', '*', '○', '·')) and ' ' in text[1:3]:
                                            text_list.append(f"{text}")
                                        # Might be a heading
                                        elif len(text) < 50 and text.endswith(':'):
                                            text_list.append(f"#### {text}")
                                        # Regular text
                                        else:
                                            text_list.append(text)
                                
                                # Add all the extracted text
                                for text in text_list:
                                    markdown_text += f"{text}\n\n"
                            else:
                                markdown_text += "*Slide data not found*\n\n"
                        else:
                            markdown_text += "*Slide reference not found in relationships*\n\n"
                    
                    # If no slides were found, add a note
                    if not slides:
                        markdown_text += "*No slides found in the presentation*\n\n"
                else:
                    markdown_text += "*Could not locate presentation structure*\n\n"
            
        except zipfile.BadZipFile:
            markdown_text += "The PowerPoint file appears to be corrupt or invalid.\n\n"
        
        return markdown_text
    
    except Exception as e:
        logger.error(f"Error converting PPTX to Markdown: {str(e)}")
        return f"# {os.path.basename(file_path)}\n\nError processing PowerPoint file: {str(e)}"

def convert_image_to_markdown(file_path, use_llm=False):
    """Convert Image to Markdown with basic information extraction"""
    try:
        import subprocess
        import os
        import base64
        import mimetypes
        
        # Get the filename without extension for use as title
        file_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        
        # Start with a title
        markdown_text = f"# {file_name_without_ext}\n\n"
        
        # Try using file command to get information about the image
        try:
            file_info = subprocess.check_output(['file', file_path]).decode('utf-8').strip()
            markdown_text += f"## Image Information\n\n{file_info}\n\n"
        except subprocess.SubprocessError:
            pass
        
        # Try using identify command if available (from ImageMagick)
        try:
            identify_info = subprocess.check_output(['identify', file_path]).decode('utf-8').strip()
            info_parts = identify_info.split()
            
            if len(info_parts) >= 2:
                dimensions = info_parts[2] if len(info_parts) > 2 else "Unknown dimensions"
                format_info = info_parts[1] if len(info_parts) > 1 else "Unknown format"
                
                markdown_text += f"**Format:** {format_info}\n\n"
                markdown_text += f"**Dimensions:** {dimensions}\n\n"
        except (subprocess.SubprocessError, FileNotFoundError):
            # If identify isn't available, we'll skip this part
            pass
        
        # Try using tesseract OCR if installed
        try:
            # Check if tesseract is installed
            if subprocess.call(["which", "tesseract"], stdout=subprocess.DEVNULL) == 0:
                # Run OCR on the image
                ocr_text = subprocess.check_output(
                    ["tesseract", file_path, "stdout"], 
                    stderr=subprocess.DEVNULL
                ).decode('utf-8')
                
                if ocr_text.strip():
                    markdown_text += "## Extracted Text\n\n"
                    
                    # Process the extracted text
                    lines = ocr_text.split('\n')
                    current_paragraph = ""
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            if current_paragraph:
                                markdown_text += current_paragraph + "\n\n"
                                current_paragraph = ""
                            continue
                        
                        if current_paragraph:
                            current_paragraph += " " + line
                        else:
                            current_paragraph = line
                    
                    if current_paragraph:
                        markdown_text += current_paragraph + "\n\n"
        except (subprocess.SubprocessError, FileNotFoundError):
            # If OCR isn't available or fails, indicate that
            markdown_text += "## Text Extraction\n\nText extraction from images requires OCR software like Tesseract to be installed.\n\n"
        
        # Include a reference to the image itself
        markdown_text += "## Original Image\n\n"
        
        # Get the mime type
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "image/jpeg"  # default fallback
        
        markdown_text += f"![{file_name_without_ext}]({file_name})\n\n"
        markdown_text += "*Note: The image reference above will only work if the image is in the same directory as the Markdown file.*\n\n"
        
        return markdown_text
    
    except Exception as e:
        logger.error(f"Error converting Image to Markdown: {str(e)}")
        return f"# {os.path.basename(file_path)}\n\nError processing image file: {str(e)}"

def convert_csv_to_markdown(file_path, use_llm=False):
    """Convert CSV to Markdown table without using pandas"""
    try:
        import csv
        
        # Get the filename without extension for use as title
        file_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        
        # Start with a title
        markdown_text = f"# {file_name_without_ext}\n\n"
        
        with open(file_path, 'r', encoding='utf-8', errors='replace') as csv_file:
            # Try to detect the delimiter
            sample = csv_file.read(1024)
            csv_file.seek(0)
            
            # Simple heuristic for delimiter detection
            delimiter = ','  # default
            if sample.count(';') > sample.count(','):
                delimiter = ';'
            elif sample.count('\t') > sample.count(','):
                delimiter = '\t'
            
            # Read CSV data
            csv_reader = csv.reader(csv_file, delimiter=delimiter)
            rows = list(csv_reader)
            
            if not rows:
                return markdown_text + "Empty CSV file.\n\n"
            
            # Use first row as headers
            headers = rows[0]
            
            # Create Markdown table header
            markdown_text += "| " + " | ".join(headers) + " |\n"
            markdown_text += "| " + " | ".join(["---"] * len(headers)) + " |\n"
            
            # Add data rows
            for row in rows[1:]:
                # Ensure row has enough columns
                if len(row) < len(headers):
                    row = row + [""] * (len(headers) - len(row))
                # Truncate if too many columns
                row = row[:len(headers)]
                # Escape pipe characters in cell content
                row = [cell.replace("|", "\\|") for cell in row]
                markdown_text += "| " + " | ".join(row) + " |\n"
            
            # Add summary
            markdown_text += f"\n*CSV file with {len(rows)} rows and {len(headers)} columns.*\n\n"
        
        return markdown_text
        
    except Exception as e:
        logger.error(f"Error converting CSV to Markdown: {str(e)}")
        return f"# {os.path.basename(file_path)}\n\nError processing CSV file: {str(e)}"

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "markitdown-secret-key")

# File upload settings
ALLOWED_EXTENSIONS = {
    'html', 'htm', 'pdf', 'docx', 'doc', 'txt', 'md', 'markdown',
    'xlsx', 'xls', 'pptx', 'ppt', 'csv', 
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'
}
TEMP_FOLDER = tempfile.gettempdir()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_converter_for_file(file_path):
    """Determine the appropriate converter based on file extension"""
    ext = file_path.rsplit('.', 1)[1].lower()
    
    if ext in ['html', 'htm']:
        return convert_html_to_markdown
    elif ext == 'pdf':
        return convert_pdf_to_markdown
    elif ext in ['docx', 'doc']:
        return convert_docx_to_markdown
    elif ext in ['txt', 'md', 'markdown']:
        return convert_txt_to_markdown
    elif ext in ['xlsx', 'xls']:
        return convert_xlsx_to_markdown
    elif ext in ['pptx', 'ppt']:
        return convert_pptx_to_markdown
    elif ext == 'csv':
        return convert_csv_to_markdown
    elif ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff']:
        return convert_image_to_markdown
    else:
        return None

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/documentation')
def documentation():
    """Render the documentation page"""
    return render_template('documentation.html')

@app.route('/api/convert', methods=['POST'])
def convert_file():
    """API endpoint to convert uploaded files to markdown"""
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Check if the file has a name
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check if the file is allowed
    if not allowed_file(file.filename):
        return jsonify({
            'error': 'Unsupported file format',
            'supported_formats': list(ALLOWED_EXTENSIONS)
        }), 400
    
    # Generate a unique filename to avoid conflicts
    unique_filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    file_path = os.path.join(TEMP_FOLDER, unique_filename)
    
    try:
        # Save the file temporarily
        file.save(file_path)
        logger.debug(f"Saved file to {file_path}")
        
        # Get the appropriate converter
        converter = get_converter_for_file(file_path)
        
        if not converter:
            os.remove(file_path)
            return jsonify({
                'error': 'No suitable converter found for this file type',
                'supported_formats': list(ALLOWED_EXTENSIONS)
            }), 400
        
        # Process LLM option
        use_llm = request.form.get('use_llm', 'false').lower() == 'true'
        
        # Convert the file to markdown
        markdown_content = converter(file_path, use_llm=use_llm)
        
        # Clean up
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'markdown': markdown_content,
            'original_filename': file.filename
        })
    
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        # Clean up in case of error
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({
            'error': 'Error processing file',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

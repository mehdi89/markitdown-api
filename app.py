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
    """Placeholder for PDF converter until dependency is resolved"""
    return f"# PDF conversion\n\nPDF conversion requires additional dependencies. File: {file_path}"

def convert_docx_to_markdown(file_path, use_llm=False):
    """Placeholder for DOCX converter until dependency is resolved"""
    return f"# DOCX conversion\n\nDOCX conversion requires additional dependencies. File: {file_path}"

def convert_xlsx_to_markdown(file_path, use_llm=False):
    """Placeholder for XLSX converter until dependency is resolved"""
    return f"# XLSX conversion\n\nXLSX conversion requires additional dependencies. File: {file_path}"

def convert_pptx_to_markdown(file_path, use_llm=False):
    """Placeholder for PPTX converter until dependency is resolved"""
    return f"# PPTX conversion\n\nPPTX conversion requires additional dependencies. File: {file_path}"

def convert_image_to_markdown(file_path, use_llm=False):
    """Placeholder for Image converter until dependency is resolved"""
    return f"# Image conversion\n\nImage conversion requires additional dependencies. File: {file_path}"

def convert_csv_to_markdown(file_path, use_llm=False):
    """Placeholder for CSV converter until dependency is resolved"""
    return f"# CSV conversion\n\nCSV conversion requires additional dependencies. File: {file_path}"

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

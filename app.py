import os
import tempfile
import io
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from markitdown import MarkItDown
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = tempfile.gettempdir()
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# Get Azure Document Intelligence endpoint if configured
docintel_endpoint = os.environ.get("DOCUMENT_INTELLIGENCE_ENDPOINT", None)

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "features": {
            "document_intelligence": docintel_endpoint is not None
        }
    })

@app.route("/convert", methods=["POST"])
def convert_to_markdown():
    """
    Convert uploaded file to Markdown.
    Supports multiple file formats (PDF, DOCX, PPTX, XLSX, etc.)
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    # Get file extension
    filename = secure_filename(file.filename)
    
    # Get conversion options from request
    use_document_intelligence = request.form.get('use_document_intelligence', 'false').lower() == 'true'
    enable_plugins = request.form.get('enable_plugins', 'false').lower() == 'true'
    
    # Configure MarkItDown
    md_config = {
        "enable_plugins": enable_plugins
    }
    
    # Add Document Intelligence if requested and available
    if use_document_intelligence and docintel_endpoint:
        md_config["docintel_endpoint"] = docintel_endpoint
    
    # Initialize MarkItDown
    md = MarkItDown(**md_config)
    
    try:
        # Save the file temporarily
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        
        # Convert the file to markdown
        result = md.convert(filepath)
        
        # Return the markdown as JSON
        return jsonify({
            "markdown": result.text_content,
            "original_filename": filename,
            "conversion_info": {
                "used_document_intelligence": use_document_intelligence and docintel_endpoint is not None,
                "used_plugins": enable_plugins
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        # Clean up the temporary file
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route("/download", methods=["POST"])
def download_markdown():
    """
    Convert file and return markdown as a downloadable file.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    # Get file extension and base name
    filename = secure_filename(file.filename)
    basename = os.path.splitext(filename)[0]
    
    # Configure MarkItDown the same as the convert endpoint
    use_document_intelligence = request.form.get('use_document_intelligence', 'false').lower() == 'true'
    enable_plugins = request.form.get('enable_plugins', 'false').lower() == 'true'
    
    md_config = {"enable_plugins": enable_plugins}
    if use_document_intelligence and docintel_endpoint:
        md_config["docintel_endpoint"] = docintel_endpoint
    
    md = MarkItDown(**md_config)
    
    try:
        # Save the file temporarily
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        
        # Convert the file to markdown
        result = md.convert(filepath)
        
        # Create an in-memory file to send
        out_file = io.BytesIO()
        out_file.write(result.text_content.encode('utf-8'))
        out_file.seek(0)
        
        # Return the markdown as a downloadable file
        return send_file(
            out_file,
            as_attachment=True,
            download_name=f"{basename}.md",
            mimetype="text/markdown"
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        # Clean up the temporary file
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route("/supported-formats", methods=["GET"])
def supported_formats():
    """
    Return information about supported file formats.
    """
    return jsonify({
        "supported_formats": [
            {"extension": ".pdf", "description": "PDF Documents"},
            {"extension": ".docx", "description": "Microsoft Word Documents"},
            {"extension": ".pptx", "description": "Microsoft PowerPoint Presentations"},
            {"extension": ".xlsx", "description": "Microsoft Excel Spreadsheets"},
            {"extension": ".html", "description": "HTML Documents"},
            {"extension": ".jpg", "description": "JPEG Images (with OCR)"},
            {"extension": ".png", "description": "PNG Images (with OCR)"},
            {"extension": ".txt", "description": "Text Files"},
            {"extension": ".csv", "description": "CSV Files"},
            {"extension": ".json", "description": "JSON Files"},
            {"extension": ".xml", "description": "XML Files"},
            {"extension": ".epub", "description": "EPub Books"},
            {"extension": ".mp3", "description": "MP3 Audio Files (for transcription)"},
            {"extension": ".wav", "description": "WAV Audio Files (for transcription)"},
            {"extension": ".msg", "description": "Outlook Messages"},
            {"extension": ".zip", "description": "ZIP Archives (iterates over contents)"}
        ]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("DEBUG", "False").lower() == "true") 
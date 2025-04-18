# MarkItDown API

A Flask-based REST API for converting various file formats to Markdown using Microsoft's [MarkItDown](https://github.com/microsoft/markitdown) library.

## Features

- Convert multiple file formats to Markdown, including:
  - PDF
  - Microsoft Office documents (Word, PowerPoint, Excel)
  - Images (with OCR)
  - HTML
  - Text-based formats (CSV, JSON, XML)
  - EPub
  - Audio files (with transcription)
  - And more!
- Support for Azure Document Intelligence for enhanced document conversion
- REST API with JSON responses or direct file downloads
- Docker support for easy deployment

## Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/yourusername/markitdown-api.git
cd markitdown-api

# Build and start the container
docker compose up -d

# The API is now available at http://localhost:5000
```

## API Endpoints

### GET /health

Check the health of the API.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "features": {
    "document_intelligence": false
  }
}
```

### GET /supported-formats

Get a list of supported file formats.

**Response:**
```json
{
  "supported_formats": [
    {"extension": ".pdf", "description": "PDF Documents"},
    {"extension": ".docx", "description": "Microsoft Word Documents"},
    ...
  ]
}
```

### POST /convert

Convert a file to Markdown and return the result as JSON.

**Request:**
- Form data:
  - `file`: The file to convert
  - `use_document_intelligence` (optional): Set to "true" to use Azure Document Intelligence
  - `enable_plugins` (optional): Set to "true" to enable MarkItDown plugins

**Response:**
```json
{
  "markdown": "# Document Title\n\nDocument content...",
  "original_filename": "document.pdf",
  "conversion_info": {
    "used_document_intelligence": false,
    "used_plugins": false
  }
}
```

### POST /download

Convert a file to Markdown and return the result as a downloadable file.

**Request:**
- Form data:
  - `file`: The file to convert
  - `use_document_intelligence` (optional): Set to "true" to use Azure Document Intelligence
  - `enable_plugins` (optional): Set to "true" to enable MarkItDown plugins

**Response:**
- A downloadable Markdown file

## Environment Variables

You can configure the API using the following environment variables:

- `DEBUG`: Set to "True" to enable debug mode (default: "False")
- `PORT`: The port to run the API on (default: 5000)
- `DOCUMENT_INTELLIGENCE_ENDPOINT`: Azure Document Intelligence endpoint URL (optional)

## Examples

### Using cURL

```bash
# Convert a PDF file to Markdown
curl -X POST -F "file=@document.pdf" http://localhost:5000/convert

# Convert a PDF file and download the result
curl -X POST -F "file=@document.pdf" http://localhost:5000/download -o document.md

# Use Azure Document Intelligence
curl -X POST -F "file=@document.pdf" -F "use_document_intelligence=true" http://localhost:5000/convert
```

### Using Python requests

```python
import requests

# Convert a PDF file to Markdown
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/convert',
        files={'file': f}
    )
    
markdown_content = response.json()['markdown']
print(markdown_content)
```

## Development

### Running locally

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Running tests

```bash
# (Future implementation)
```

## License

This project is MIT licensed, as is the original [MarkItDown](https://github.com/microsoft/markitdown) library. 
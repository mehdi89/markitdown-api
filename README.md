# MarkItDown: File-to-Markdown Converter

<div align="center">
  <img src="https://github.com/markitdown/convert/raw/main/logo.png" alt="MarkItDown Logo" width="200"/>
  <br>
  <strong>Convert various file formats to clean, well-formatted Markdown</strong>
  <br><br>
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#api">API</a> •
  <a href="#development">Development</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</div>

## Features

- **Multiple Format Support**: Convert HTML, PDF, DOCX, XLSX, PPTX, CSV, TXT, and image files to Markdown
- **Structure Preservation**: Maintains document structure including headings, lists, tables, and links
- **Clean Output**: Produces well-formatted, readable Markdown
- **API Available**: Integrate with the conversion engine via REST API
- **Drag-and-Drop Interface**: User-friendly web interface with preview, copy, and download options
- **Optional LLM Enhancement**: Experimental AI-powered improvements (when enabled)
- **Docker Compatible**: Easy deployment with containerization
- **Extensible Architecture**: Modular design makes adding new format converters simple

## Installation

MarkItDown can be installed and run in several ways:

### Prerequisites

- Python 3.8+
- Required packages (installed automatically with pip)

### Option 1: From PyPI

```bash
pip install markitdown-converter
```

### Option 2: From Source

```bash
git clone https://github.com/markitdown/convert.git
cd convert
pip install -e .
```

### Option 3: Using Docker

```bash
# Pull the image
docker pull markitdown/convert:latest

# Run the container
docker run -p 5000:5000 markitdown/convert:latest
```

### Option 4: Using Docker Compose

```bash
git clone https://github.com/markitdown/convert.git
cd convert
docker-compose up
```

## Usage

### Command Line Interface

MarkItDown provides a simple command-line interface for file conversion:

```bash
# Basic usage
markitdown convert document.pdf > document.md

# With LLM enhancement
markitdown convert --use-llm document.docx > enhanced_document.md

# Specify output file
markitdown convert document.html -o document.md
```

### Web Interface

When running as a service, MarkItDown provides a web interface at http://localhost:5000 (or your configured domain).

1. Navigate to the web interface
2. Drag and drop your file or use the file selector
3. Toggle LLM enhancement if desired
4. Click "Convert to Markdown"
5. View, copy, or download the resulting Markdown

### Python Library Usage

```python
from markitdown import convert_file

# Basic conversion
markdown = convert_file('document.pdf')
print(markdown)

# With LLM enhancement
markdown = convert_file('document.docx', use_llm=True)

# Save to file
with open('output.md', 'w') as f:
    f.write(markdown)
```

## API

MarkItDown exposes a RESTful API for integration with other services. See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for full details.

### Quick Example

```bash
curl -X POST http://localhost:5000/api/convert \
  -F "file=@document.pdf" \
  -F "use_llm=false"
```

### Response

```json
{
  "success": true,
  "markdown": "# Document Title\n\nContent of the document...",
  "original_filename": "document.pdf"
}
```

## Architecture & Implementation Details

MarkItDown follows a modular architecture that makes it easy to maintain and extend.

### System Architecture

```
┌─────────────┐     ┌────────────────┐     ┌────────────────┐
│  Web UI /   │────▶│  Flask Server  │────▶│   Converter    │
│    API      │     │                │     │   Modules      │
└─────────────┘     └────────────────┘     └────────────────┘
                           │                       │
                           ▼                       ▼
                    ┌────────────────┐     ┌────────────────┐
                    │  File Storage  │     │  LLM Service   │
                    │   (Temp)       │     │  (Optional)    │
                    └────────────────┘     └────────────────┘
```

### Core Components

1. **Flask Application**: Provides web interface and API endpoints
2. **Converter Modules**: Format-specific converters implemented as independent modules
3. **File Handling**: Manages secure file uploads and temporary storage
4. **LLM Integration**: Optional AI enhancement for improved conversion quality

### Converter Implementation

Each converter module follows a standard interface:

```python
def convert_X_to_markdown(file_path, use_llm=False):
    """
    Convert X file to Markdown
    
    Args:
        file_path (str): Path to the file
        use_llm (bool): Whether to use LLM enhancement
        
    Returns:
        str: Markdown content
    """
```

Converters use format-specific libraries for content extraction and apply custom logic to transform content into well-structured Markdown.

### File Format Support Details

| Format | Library | Features | Limitations |
|--------|---------|----------|-------------|
| HTML | BeautifulSoup4 | Full DOM parsing, extracts structure, tables, links | JavaScript-rendered content not supported |
| PDF | PyPDF2 | Text extraction, basic structure | Complex layouts may lose formatting |
| DOCX | python-docx | Document structure, tables, lists | Complex formatting may be simplified |
| XLSX | pandas, openpyxl | Table structure, multiple sheets | Formatting and formulas not preserved |
| PPTX | python-pptx | Slide content, basic structure | Complex layouts and animations lost |
| CSV | pandas | Table structure | Limited to tabular data |
| Images | pytesseract | OCR text extraction | Accuracy depends on image quality |
| TXT | builtin | Basic structure detection | Limited formatting possible |

### Implementation Details by Feature

#### Structure Preservation

- Headings are detected through style analysis, font size, or position
- Lists are identified by markers or indentation
- Tables are preserved through Markdown table syntax
- Links are converted to Markdown format `[text](url)`

#### LLM Enhancement

When enabled, LLM features:
- Improve document structure detection
- Generate better heading hierarchies
- Enhance formatting detection
- Provide additional context in complex sections

#### Security Considerations

- Files are stored in temporary locations and removed after processing
- File extensions and MIME types are validated
- Input sanitization throughout the application
- Rate limiting recommended for production deployments

## Docker Deployment

The included Dockerfile and docker-compose.yml allow for easy containerization:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--reuse-port", "--reload", "main:app"]
```

Build and run:

```bash
docker build -t markitdown:latest .
docker run -p 5000:5000 markitdown:latest
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/markitdown/convert.git
cd convert

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Project Structure

```
markitdown/
├── converters/             # Format-specific converters
│   ├── __init__.py
│   ├── html_converter.py
│   ├── pdf_converter.py
│   ├── docx_converter.py
│   ├── xlsx_converter.py
│   └── ...
├── static/                 # Static web assets
│   ├── css/
│   └── js/
├── templates/              # HTML templates
│   ├── index.html
│   └── documentation.html
├── app.py                  # Flask application
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
└── Dockerfile              # Docker configuration
```

### Running Tests

```bash
pytest
```

### Adding a New Converter

1. Create a new file in the `converters` directory: `converters/new_format_converter.py`
2. Implement the converter function following the standard interface
3. Import and register the converter in `app.py`
4. Update the supported formats list in both the code and documentation

Example converter template:

```python
import logging
import os

logger = logging.getLogger(__name__)

def convert_new_format_to_markdown(file_path, use_llm=False):
    """
    Convert NewFormat file to Markdown
    
    Args:
        file_path (str): Path to the file
        use_llm (bool): Whether to use LLM enhancement
        
    Returns:
        str: Markdown content
    """
    logger.debug(f"Converting NewFormat file: {file_path}")
    
    try:
        # Format-specific conversion logic
        # ...
        
        return markdown_text
    
    except Exception as e:
        logger.error(f"Error converting NewFormat to Markdown: {str(e)}")
        raise Exception(f"NewFormat conversion error: {str(e)}")
```

### Code Style

This project follows PEP 8 style guidelines. To check and fix style issues:

```bash
# Check style
flake8

# Auto-format code
black .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines

- Follow the established code style and patterns
- Add tests for new functionality
- Update documentation to reflect changes
- Ensure all tests pass before submitting PRs

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all [contributors](https://github.com/markitdown/convert/graphs/contributors)
- [Flask](https://flask.palletsprojects.com/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [PyPDF2](https://pythonhosted.org/PyPDF2/)
- [python-docx](https://python-docx.readthedocs.io/)
- [pandas](https://pandas.pydata.org/)
- [python-pptx](https://python-pptx.readthedocs.io/)
- [pytesseract](https://github.com/madmaze/pytesseract)

---

<div align="center">
  <sub>Built with ❤️ by the community</sub>
</div>
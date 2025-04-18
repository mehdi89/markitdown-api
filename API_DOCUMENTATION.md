# MarkItDown API Documentation

## Overview

MarkItDown is an API service that extracts and converts content from various file formats to clean, well-formatted Markdown. This document provides detailed information about the available endpoints, parameters, and examples for integrating with the MarkItDown API.

## Base URL

For local development:
```
http://localhost:5000
```

For deployed instances, use the appropriate domain.

## Authentication

Currently, the API does not require authentication. This might change in future versions.

## API Endpoints

### Convert File to Markdown

Converts an uploaded file to Markdown format.

**Endpoint:** `POST /api/convert`

**Content-Type:** `multipart/form-data`

#### Request Parameters

| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| file      | File   | Yes      | The file to convert (must be in one of the supported formats) |
| use_llm   | Boolean| No       | Whether to use LLM enhancement features (default: false) |

#### Supported File Formats

| Format          | Extensions             | Description |
|-----------------|------------------------|-------------|
| HTML            | .html, .htm            | Converts HTML documents to Markdown, preserving structure and formatting |
| PDF             | .pdf                   | Extracts text content from PDF files, attempts to preserve document structure |
| Microsoft Word  | .docx, .doc            | Converts Word documents to Markdown, preserving headings, lists, and basic formatting |
| Plain Text      | .txt, .md, .markdown   | Processes plain text files, detecting and enhancing structure when possible |
| Excel           | .xlsx, .xls            | Converts Excel spreadsheets to Markdown tables |
| PowerPoint      | .pptx, .ppt            | Extracts content from presentations including text and structure |
| CSV             | .csv                   | Converts CSV data to Markdown tables |
| Images          | .jpg, .jpeg, .png, .gif, .bmp, .tiff | Extracts text from images using OCR |

#### Response

**Success Response (200 OK)**

```json
{
  "success": true,
  "markdown": "# Converted Document\n\nThis is a paragraph...",
  "original_filename": "example.docx"
}
```

**Error Response (400 Bad Request)**

```json
{
  "error": "Unsupported file format",
  "supported_formats": ["html", "htm", "pdf", "docx", "doc", "txt", "md", "markdown", "xlsx", "xls", "pptx", "ppt", "csv", "jpg", "jpeg", "png", "gif", "bmp", "tiff"]
}
```

or

```json
{
  "error": "No file provided"
}
```

**Error Response (500 Internal Server Error)**

```json
{
  "error": "Error processing file",
  "message": "Detailed error message"
}
```

#### Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 OK      | Successful conversion |
| 400 Bad Request | Missing file, empty file, or unsupported format |
| 500 Internal Server Error | Error processing file or server issues |

## Examples

### cURL Examples

#### Basic Usage

```bash
curl -X POST http://localhost:5000/api/convert \
  -F "file=@/path/to/document.pdf"
```

#### With LLM Enhancement

```bash
curl -X POST http://localhost:5000/api/convert \
  -F "file=@/path/to/document.docx" \
  -F "use_llm=true"
```

#### Processing HTML Content

```bash
curl -X POST http://localhost:5000/api/convert \
  -F "file=@/path/to/webpage.html"
```

#### Converting Excel Spreadsheet

```bash
curl -X POST http://localhost:5000/api/convert \
  -F "file=@/path/to/data.xlsx"
```

#### Image OCR Processing

```bash
curl -X POST http://localhost:5000/api/convert \
  -F "file=@/path/to/scan.jpg"
```

### Python Example

```python
import requests

url = 'http://localhost:5000/api/convert'
files = {'file': open('document.docx', 'rb')}
data = {'use_llm': 'false'}

response = requests.post(url, files=files, data=data)
result = response.json()

if response.status_code == 200:
    markdown_content = result['markdown']
    print(markdown_content)
    
    # Save to file
    with open('converted.md', 'w') as f:
        f.write(markdown_content)
else:
    print(f"Error: {result['error']}")
```

### JavaScript/Node.js Example

```javascript
const fs = require('fs');
const axios = require('axios');
const FormData = require('form-data');

async function convertToMarkdown(filePath) {
  const form = new FormData();
  form.append('file', fs.createReadStream(filePath));
  form.append('use_llm', 'false');
  
  try {
    const response = await axios.post('http://localhost:5000/api/convert', form, {
      headers: {
        ...form.getHeaders()
      }
    });
    
    if (response.data.success) {
      return response.data.markdown;
    } else {
      throw new Error(response.data.error);
    }
  } catch (error) {
    console.error('Error:', error.message);
    throw error;
  }
}

// Usage
convertToMarkdown('/path/to/document.pdf')
  .then(markdown => {
    console.log(markdown);
    fs.writeFileSync('converted.md', markdown);
  })
  .catch(error => console.error('Conversion failed:', error));
```

### Browser JavaScript Example

```javascript
const form = new FormData();
form.append('file', fileInput.files[0]);
form.append('use_llm', 'false');

fetch('http://localhost:5000/api/convert', {
  method: 'POST',
  body: form
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log(data.markdown);
    document.getElementById('output').textContent = data.markdown;
  } else {
    console.error(data.error);
  }
})
.catch(error => console.error('Error:', error));
```

## LLM Enhancement Features

The API includes an optional `use_llm` parameter that enables Large Language Model features for enhanced conversion. When enabled, the API uses advanced AI models to:

- Improve structure detection in plain text
- Enhance formatting in PDF content extraction
- Detect and preserve more complex elements like tables
- Generate better heading hierarchies
- Provide summaries for complex documents

To enable LLM features, set the `use_llm` parameter to `true` when making API requests.

Note: LLM features are experimental and may not be available for all file formats. Processing time might increase when LLM enhancement is enabled.

## Rate Limiting

Currently, there are no rate limits implemented. However, we recommend implementing client-side throttling for production use.

## Self-Hosting

For information on self-hosting the MarkItDown service, please refer to the README.md in the project repository.

## Troubleshooting

### Common Issues

1. **File format not supported**
   - Check if your file extension is in the supported list
   - Some file formats may require additional dependencies to be installed

2. **Conversion errors**
   - Make sure the file is not corrupted
   - Complex formatting in source documents may lead to imperfect conversion

3. **Empty response**
   - Some files may contain content that is difficult to extract (e.g., scanned PDFs without OCR)

For additional support, please open an issue on the GitHub repository.
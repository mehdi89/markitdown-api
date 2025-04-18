#!/usr/bin/env python3
"""
Simple test client for the MarkItDown API.
This script demonstrates how to use the API endpoints.
"""

import argparse
import os
import requests
import sys

def main():
    parser = argparse.ArgumentParser(description="Test client for MarkItDown API")
    parser.add_argument("file", help="Path to the file to convert")
    parser.add_argument(
        "--endpoint", 
        default="http://localhost:5000",
        help="API endpoint URL (default: http://localhost:5000)"
    )
    parser.add_argument(
        "--download", 
        action="store_true",
        help="Download the result as a file instead of displaying it"
    )
    parser.add_argument(
        "--use-document-intelligence", 
        action="store_true",
        help="Use Azure Document Intelligence for conversion"
    )
    parser.add_argument(
        "--enable-plugins", 
        action="store_true",
        help="Enable MarkItDown plugins"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} does not exist.")
        sys.exit(1)
        
    # Prepare the form data
    form_data = {
        "use_document_intelligence": "true" if args.use_document_intelligence else "false",
        "enable_plugins": "true" if args.enable_plugins else "false"
    }
    
    # Prepare the files
    with open(args.file, "rb") as f:
        files = {"file": f}
        
        if args.download:
            # Call the download endpoint
            response = requests.post(
                f"{args.endpoint}/download",
                files=files,
                data=form_data
            )
            
            if response.status_code == 200:
                # Save the file
                filename = os.path.splitext(os.path.basename(args.file))[0] + ".md"
                with open(filename, "wb") as output_file:
                    output_file.write(response.content)
                print(f"Markdown saved to {filename}")
            else:
                try:
                    error_msg = response.json()["error"]
                    print(f"Error: {error_msg}")
                except:
                    print(f"Error: HTTP {response.status_code}")
                    print(response.text)
        else:
            # Call the convert endpoint
            response = requests.post(
                f"{args.endpoint}/convert",
                files=files,
                data=form_data
            )
            
            if response.status_code == 200:
                # Display the markdown
                markdown = response.json()["markdown"]
                print(markdown)
            else:
                try:
                    error_msg = response.json()["error"]
                    print(f"Error: {error_msg}")
                except:
                    print(f"Error: HTTP {response.status_code}")
                    print(response.text)

if __name__ == "__main__":
    main() 
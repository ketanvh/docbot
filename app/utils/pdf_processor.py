import io
import fitz  # PyMuPDF
import re
import os
from dotenv import load_dotenv
from werkzeug.datastructures import FileStorage

# Load environment variables and set up debug functionality
load_dotenv()
DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "t", "yes", "y"]

def debug_log(message):
    if DEBUG:
        print(f"DEBUG [PDF Processor]: {message}")

def process_pdf(file_obj):
    """
    Process a PDF file and extract text content in markdown format.
    
    Args:
        file_obj: File object from request.files
        
    Returns:
        str: Extracted text content in markdown format
    """
    debug_log(f"Processing PDF file: {getattr(file_obj, 'filename', 'Unnamed Document')}")
    
    try:
        # Get the file content
        if isinstance(file_obj, FileStorage):
            pdf_bytes = file_obj.read()
            file_obj.close()
            pdf_stream = io.BytesIO(pdf_bytes)
        else:
            # If it's already a bytes object or BytesIO
            pdf_stream = file_obj if isinstance(file_obj, io.BytesIO) else io.BytesIO(file_obj)
        
        # Open the PDF
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        debug_log(f"PDF opened successfully with {len(doc)} pages")
        
        # Initialize document content
        content = f"# Document: {getattr(file_obj, 'filename', 'Unnamed Document')}\n\n"
        
        # Extract text from each page
        for page_num, page in enumerate(doc):
            debug_log(f"Extracting text from page {page_num + 1}/{len(doc)}")
            page_text = page.get_text()
            
            # Clean up text
            page_text = re.sub(r'\s+', ' ', page_text)  # Replace multiple spaces with single space
            page_text = page_text.strip()
            
            if page_text:
                content += f"## Page {page_num + 1}\n\n{page_text}\n\n"
        
        # Close the document
        doc.close()
        
        debug_log(f"PDF processing complete: {len(content)} characters extracted")
        return content.strip()
    except Exception as e:
        debug_log(f"ERROR processing PDF: {str(e)}")
        return f"Error processing PDF: {str(e)}"
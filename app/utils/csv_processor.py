import io
import csv
import os
from dotenv import load_dotenv
from werkzeug.datastructures import FileStorage

# Load environment variables and set up debug functionality
load_dotenv()
DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "t", "yes", "y"]

def debug_log(message):
    if DEBUG:
        print(f"DEBUG [CSV Processor]: {message}")

def process_csv(file_obj):
    """
    Process a CSV file and convert its content to a markdown table for better LLM understanding.
    
    Args:
        file_obj: File object from request.files
        
    Returns:
        str: CSV content converted to markdown table format
    """
    debug_log(f"Processing CSV file: {getattr(file_obj, 'filename', 'Unnamed CSV')}")
    
    try:
        # Get the file content
        if isinstance(file_obj, FileStorage):
            csv_bytes = file_obj.read()
            file_obj.close()
            csv_stream = io.StringIO(csv_bytes.decode('utf-8'))
        else:
            # If it's already a bytes object or StringIO
            if isinstance(file_obj, io.BytesIO):
                csv_stream = io.StringIO(file_obj.getvalue().decode('utf-8'))
            elif isinstance(file_obj, io.StringIO):
                csv_stream = file_obj
            else:
                csv_stream = io.StringIO(file_obj.decode('utf-8'))
        
        # Parse CSV
        csv_stream.seek(0)
        reader = csv.reader(csv_stream)
        
        # Get header and rows
        rows = list(reader)
        
        if not rows:
            debug_log("CSV file is empty")
            return "CSV file is empty"
        
        header = rows[0]
        data_rows = rows[1:]
        
        # Initialize markdown content
        content = f"# CSV Data: {getattr(file_obj, 'filename', 'Unnamed CSV')}\n\n"
        
        # Build markdown table header
        table_header = "| " + " | ".join(header) + " |"
        separator = "| " + " | ".join(["---" for _ in header]) + " |"
        
        # Build table rows
        table_rows = []
        for row in data_rows:
            # Pad short rows to match header length
            padded_row = row + [''] * (len(header) - len(row))
            table_rows.append("| " + " | ".join(padded_row) + " |")
        
        # Combine all parts of the markdown table
        markdown_table = "\n".join([table_header, separator] + table_rows)
        
        # Add table to content
        content += markdown_table + "\n\n"
        
        # Add a summary
        content += f"\nTable summary: {len(data_rows)} rows and {len(header)} columns of data.\n"
        
        debug_log(f"CSV processing complete: converted to markdown table with {len(data_rows)} rows")
        return content.strip()
    except Exception as e:
        debug_log(f"ERROR processing CSV: {str(e)}")
        return f"Error processing CSV: {str(e)}"
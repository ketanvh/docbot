"""
Service provider module that determines which document processing library to use.
Based on the DOC_INTELLIGENT flag, this module selects the appropriate processing function
for each document type.
"""

import importlib
import os
from dotenv import load_dotenv

load_dotenv()
DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "t", "yes", "y"]

def debug_log(message):
    if DEBUG:
        print(f"DEBUG [Document Processor]: {message}")


class DocumentServiceProvider:
    """
    Service provider that determines which document processing library to use
    based on the configured settings.
    """
    
    def __init__(self, use_intelligent_processing=False):
        """
        Initialize the service provider with the configured processing mode.
        
        Args:
            use_intelligent_processing (bool): Whether to use intelligent document processing
        """
        debug_log(f"Use Document Intelligent : {use_intelligent_processing}")
        self.use_intelligent_processing = use_intelligent_processing
    
    def get_pdf_processor(self):
        """
        Returns the appropriate PDF processor based on the configuration.
        
        Returns:
            function: PDF processing function
        """
        if self.use_intelligent_processing:
            # Import the intelligent PDF processing module
            from app.utils.doc_processing import process_document
            return process_document
        else:
            # Import the standard PDF processing module
            from app.utils.pdf_processor import process_pdf
            return process_pdf
    
    def get_csv_processor(self):
        """
        Returns the appropriate CSV processor.
        Currently, there's only one implementation.
        
        Returns:
            function: CSV processing function
        """
        from app.utils.csv_processor import process_csv
        return process_csv
    
    def get_word_processor(self):
        """
        Returns the appropriate Word document processor based on the configuration.
        
        Returns:
            function: Word document processing function
        """
        if self.use_intelligent_processing:
            # Import the intelligent Word processing module
            from app.utils.doc_processing import process_document
            return process_document
        else:
            # Import the standard Word processing module
            from app.utils.word_processor import process_word
            return process_word
    
    def get_powerpoint_processor(self):
        """
        Returns the appropriate PowerPoint processor based on the configuration.
        
        Returns:
            function: PowerPoint processing function
        """
        if self.use_intelligent_processing:
            # Import the intelligent PowerPoint processing module
            from app.utils.doc_processing import process_document
            return process_document
        else:
            # Import the standard PowerPoint processing module
            from app.utils.powerpoint_processor import process_powerpoint
            return process_powerpoint
    
    def get_website_processor(self):
        """
        Returns the appropriate website processor.
        Currently, there's only one implementation.
        
        Returns:
            function: Website processing function
        """
        from app.utils.website_processor import process_website
        return process_website
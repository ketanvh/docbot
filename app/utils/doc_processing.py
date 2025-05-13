import io
import os
from dotenv import load_dotenv
from werkzeug.datastructures import FileStorage

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, DocumentContentFormat, AnalyzeResult


load_dotenv()
DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "t", "yes", "y"]

def debug_log(message):
    if DEBUG:
        print(f"DEBUG [Document Processor]: {message}")

def process_document(file_obj):
        endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        credential = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_API_KEY")
        file_name = "Undefined"

        try:
            # Get the file content
            if isinstance(file_obj, FileStorage):
                pdf_bytes = file_obj.read()
                file_obj.close()
                pdf_stream = io.BytesIO(pdf_bytes)
            else:
                # If it's already a bytes object or BytesIO
                pdf_stream = file_obj if isinstance(file_obj, io.BytesIO) else io.BytesIO(file_obj)

            file_name = getattr(file_obj, 'filename', 'Unnamed Document')
            debug_log(f"Processing document: {file_name}")

            # Check if the file is empty
            # Create a Document Intelligence client
            client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(credential))
            poller = client.begin_analyze_document("prebuilt-layout", body=pdf_stream,output_content_format=DocumentContentFormat.MARKDOWN)
            doc_result = poller.result()

            debug_log(f"Document {file_name} opened successfully with {len(doc_result.pages)} pages")
            debug_log(f"File processing complete: {len(doc_result.content)} characters extracted")
        
            # Initialize document content
            content = f"# Document: {getattr(file_obj, 'filename', 'Unnamed Document')}\n\n"
        
            
            content += f"## Contents \n\n{doc_result.content}\n\n"
            return content.strip()
            
        except Exception as e:
            debug_log(f"ERROR processing {file_name}: {str(e)}")
            #print(e.with_traceback())
            return f"Error processing {file_name}: {str(e)}"
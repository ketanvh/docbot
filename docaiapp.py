import os
import json
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from dotenv import load_dotenv
import uuid
from docaiapp.utils.service_provider import DocumentServiceProvider
from docaiapp.utils.openai_service import get_completion

# Load environment variables
load_dotenv()

# Initialize debug status from environment
DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "t", "yes", "y"]

# Debug logging function
def debug_log(message):
    if DEBUG:
        print(f"DEBUG: {message}")

# Initialize Flask app with correct template and static folders
app = Flask(__name__, 
            template_folder="docaiapp/templates",
            static_folder="docaiapp/static")

# Configure server-side session
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.secret_key = os.urandom(24)
Session(app)
DOC_INTELLIGENT = os.getenv("DOC_INTELLIGENT", True)

# Define the route for the main page with file upload and URL input form
@app.route("/", methods=["GET"])
def index():
    # Initialize or reset session variables
    session["documents"] = session.get("documents", [])
    session["websites"] = session.get("websites", [])
    session["messages"] = session.get("messages", [])
    
    # Get environment variables for customization
    app_title = os.getenv("APP_TITLE", "RAG Chatbot")
    app_welcome_message = os.getenv("APP_WELCOME_MESSAGE", "Welcome to the RAG Chatbot")
    app_logo_path = os.getenv("APP_LOGO_PATH", "images/Logo.png")
    app_primary_color = os.getenv("APP_PRIMARY_COLOR", "#007bff")
    
    # Generate a unique session ID if it doesn't exist
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    
    return render_template("index.html", 
                           title=app_title, 
                           welcome_message=app_welcome_message,
                           logo_path=app_logo_path,
                           primary_color=app_primary_color,
                           documents=session.get("documents", []),
                           websites=session.get("websites", []),
                           messages=session.get("messages", []))

# Route for handling file uploads and URL submissions
@app.route("/upload", methods=["POST"])
def upload():
    # Get existing documents and websites or initialize if they don't exist
    documents = session.get("documents", [])
    websites = session.get("websites", [])
    
    try:
        # Process uploaded files
        uploaded_files = request.files.getlist("file")
        for file in uploaded_files:
            if file and file.filename:
                # Save file information
                file_info = {
                    "id": str(uuid.uuid4()),
                    "name": file.filename,
                    "content": None  # Content will be processed on demand
                }
                
                # Save the content for later processing
                file_content = file.read()
                if file_content:
                    # Store the binary content in the session
                    file_info["binary_content"] = file_content
                    documents.append(file_info)
                    debug_log(f"File added: {file.filename}")
        
        # Process website URLs
        website_urls = request.form.get("urls", "").strip().split("\n")
        for url in website_urls:
            url = url.strip()
            if url and not any(w["url"] == url for w in websites):
                if not url.startswith(("http://", "https://")):
                    url = f"https://{url}"
                websites.append({
                    "id": str(uuid.uuid4()),
                    "url": url,
                    "content": None  # Content will be processed on demand
                })
                debug_log(f"Website added: {url}")
        
        # Update session data
        session["documents"] = documents
        session["websites"] = websites
        
        return jsonify({"success": True, "message": "Files and URLs processed successfully."})
    
    except Exception as e:
        debug_log(f"Error in upload: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

# Clear message history but keep uploaded documents and websites
@app.route("/clear-messages", methods=["POST"])
def clear_messages():
    session["messages"] = []
    return jsonify({"success": True, "message": "Message history cleared"})

# Reset the entire chat session including documents and websites
@app.route("/reset", methods=["POST"])
def reset():
    # Clear all session data
    session.clear()
    return jsonify({"success": True, "message": "Session reset complete"})

# Process the chat message and generate a response
@app.route("/chat", methods=["POST"])
def chat():
    try:
        # Get the user message from the request
        data = request.json
        user_message = data.get("message", "").strip()
        
        if not user_message:
            return jsonify({"success": False, "message": "No message provided"}), 400
        
        # Get existing messages or initialize if they don't exist
        messages = session.get("messages", [])
        
        # Add the user message to the conversation history
        messages.append({"role": "user", "content": user_message})
        
        # Process all documents and websites if they haven't been processed yet
        documents = session.get("documents", [])
        websites = session.get("websites", [])
        
        # Initialize the document service provider
        service_provider = DocumentServiceProvider(use_intelligent_processing=DOC_INTELLIGENT)
        
        # Process documents if they haven't been processed yet
        document_texts = []
        for doc in documents:
            try:
                if "content" not in doc or doc["content"] is None:
                    # Determine the file type and use the appropriate processor
                    filename = doc.get("name", "").lower()
                    if "binary_content" in doc:
                        binary_content = doc["binary_content"]
                        
                        if filename.endswith((".pdf")):
                            # Use the appropriate PDF processor
                            pdf_processor = service_provider.get_pdf_processor()
                            doc["content"] = pdf_processor(binary_content, filename)
                            debug_log(f"Processed PDF: {filename}")
                            
                        elif filename.endswith((".csv")):
                            # Process CSV files
                            csv_processor = service_provider.get_csv_processor()
                            doc["content"] = csv_processor(binary_content, filename)
                            debug_log(f"Processed CSV: {filename}")
                            
                        elif filename.endswith((".docx", ".doc")):
                            # Process Word documents
                            word_processor = service_provider.get_word_processor()
                            doc["content"] = word_processor(binary_content, filename)
                            debug_log(f"Processed Word document: {filename}")
                            
                        elif filename.endswith((".pptx", ".ppt")):
                            # Process PowerPoint presentations
                            powerpoint_processor = service_provider.get_powerpoint_processor()
                            doc["content"] = powerpoint_processor(binary_content, filename)
                            debug_log(f"Processed PowerPoint: {filename}")
                            
                # Add the document content to the list of document texts
                if "content" in doc and doc["content"]:
                    document_texts.append(f"=== Document: {doc['name']} ===\n{doc['content']}")
            except Exception as e:
                debug_log(f"Error processing document {doc.get('name', 'unknown')}: {str(e)}")
                # Add an error message for this document
                document_texts.append(f"=== Document: {doc['name']} === (Error: Could not process)")
        
        # Process websites if they haven't been processed yet
        website_processor = service_provider.get_website_processor()
        for website in websites:
            try:
                if "content" not in website or website["content"] is None:
                    website["content"] = website_processor(website["url"])
                    debug_log(f"Processed website: {website['url']}")
                
                # Add the website content to the list of document texts
                if "content" in website and website["content"]:
                    document_texts.append(f"=== Website: {website['url']} ===\n{website['content']}")
            except Exception as e:
                debug_log(f"Error processing website {website.get('url', 'unknown')}: {str(e)}")
                # Add an error message for this website
                document_texts.append(f"=== Website: {website['url']} === (Error: Could not process)")
        
        # Update session with processed documents and websites
        session["documents"] = documents
        session["websites"] = websites
        
        # Combine all document texts
        all_documents = "\n\n".join(document_texts)
        
        # Get the system prompt from environment variables or use default
        system_prompt = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant answering questions based on the provided documents.")
        
        # Generate a response from the AI model
        if all_documents:
            # If we have documents/websites, include them in the prompt
            ai_response = get_completion(system_prompt, user_message, all_documents)
        else:
            # If no documents/websites, just respond to the user message
            ai_response = get_completion(system_prompt, user_message, "")
        
        # Add the AI response to the conversation history
        messages.append({"role": "assistant", "content": ai_response})
        
        # Update the session messages
        session["messages"] = messages
        
        return jsonify({
            "success": True,
            "message": ai_response,
            "messages": messages
        })
    
    except Exception as e:
        debug_log(f"Error in chat: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500


# Run the Flask application when executed directly
if __name__ == "__main__":
    app.run(debug=True, port=5000)

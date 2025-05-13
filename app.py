import os
import json
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from dotenv import load_dotenv
import uuid
from app.utils.service_provider import DocumentServiceProvider
from app.utils.openai_service import get_completion

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
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static'))

# Configure server-side session
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.secret_key = os.urandom(24)
Session(app)
DOC_INTELLIGENT = os.getenv("DOC_INTELLIGENT", True)

# Initialize document service provider
document_service = DocumentServiceProvider(use_intelligent_processing=DOC_INTELLIGENT)

debug_log("Flask app initialized with debug mode: " + str(DEBUG))

@app.route('/')
def index():
    """Render the main chat interface."""
    # Get app configuration from environment variables
    app_title = os.getenv("APP_TITLE", "RAG Chatbot")
    app_welcome_title = os.getenv("APP_WELCOME_TITLE", "Welcome to the Virtual Assistant")
    app_welcome_message = os.getenv("APP_WELCOME_MESSAGE", "Upload PDFs, CSV files, Word documents, PowerPoint presentations, or provide website URLs to get relevant answers powered by AI")
    
    # Fix logo path - remove 'static/' prefix since url_for already includes it
    logo_path = os.getenv("APP_LOGO_PATH", "images/logo.png")
    if logo_path.startswith('static/'):
        logo_path = logo_path[7:]  # Remove 'static/' prefix
    debug_log(f"Using logo path: {logo_path}")
        
    app_color = os.getenv("APP_PRIMARY_COLOR", "#007bff")
    
    debug_log(f"Rendering index with title: {app_title}, logo: {logo_path}")
    
    return render_template(
        'index.html', 
        title=app_title,
        welcome_title=app_welcome_title,
        welcome_message=app_welcome_message,
        logo_path=logo_path,
        primary_color=app_color,
        debug=DEBUG
    )

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process user query and return AI response."""
    data = request.json
    query = data.get('query', '')
    
    debug_log(f"Received chat query: {query}")
    
    # Initialize session data for new users
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session['chat_history'] = []
        session['context'] = ""
        session['resource_info'] = {'files': [], 'websites': []}
        debug_log(f"New user session created with ID: {session['user_id']}")
    
    # Process user query
    if query.lower() == 'clear':
        debug_log("Clearing chat history")
        session['chat_history'] = []
        session['context'] = ""
        session['resource_info'] = {'files': [], 'websites': []}
        return jsonify({
            'response': 'Chat history cleared. You can upload new files or provide website URLs.',
            'history': []
        })
    
    # Add query to chat history
    session['chat_history'].append({'role': 'user', 'content': query})
    
    # Get context from session
    context = session.get('context', "")
    
    # Get AI response
    debug_log("Calling OpenAI service for completion")
    response = get_completion(query, context, session.get('chat_history', []))
    debug_log("Response received from OpenAI service")
    
    # Add response to chat history
    session['chat_history'].append({'role': 'assistant', 'content': response})
    
    return jsonify({
        'response': response,
        'history': session['chat_history']
    })

@app.route('/api/upload', methods=['POST'])
def upload():
    """Process uploaded files and websites."""
    debug_log("Processing upload request")
    
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session['chat_history'] = []
        session['context'] = ""
        session['resource_info'] = {'files': [], 'websites': []}
        debug_log(f"New user session created with ID: {session['user_id']}")
    
    context = ""
    uploaded_files = []
    uploaded_websites = []
    
    # Get filenames and website URLs from form data if provided
    try:
        filenames_json = request.form.get('filenames')
        website_urls_json = request.form.get('websiteUrls')
        
        if filenames_json:
            uploaded_files = json.loads(filenames_json)
            debug_log(f"Received filenames: {uploaded_files}")
        
        if website_urls_json:
            uploaded_websites = json.loads(website_urls_json)
            debug_log(f"Received website URLs: {uploaded_websites}")
    except Exception as e:
        debug_log(f"Error parsing filenames or website URLs: {str(e)}")
    
    # Get the appropriate document processors using the service provider
    pdf_processor = document_service.get_pdf_processor()
    csv_processor = document_service.get_csv_processor()
    word_processor = document_service.get_word_processor()
    powerpoint_processor = document_service.get_powerpoint_processor()
    website_processor = document_service.get_website_processor()
    
    # Process files
    if 'files' in request.files:
        files = request.files.getlist('files')
        debug_log(f"Received {len(files)} files")
        
        # If filenames weren't provided in metadata, extract them
        if not uploaded_files:
            uploaded_files = [file.filename for file in files if file.filename]
        
        for file in files:
            if file.filename.endswith('.pdf'):
                debug_log(f"Processing PDF file: {file.filename}")
                pdf_content = pdf_processor(file)
                context += f"--- Content from {file.filename} ---\n{pdf_content}\n\n"
            elif file.filename.endswith('.csv'):
                debug_log(f"Processing CSV file: {file.filename}")
                csv_content = csv_processor(file)
                context += f"--- Content from {file.filename} ---\n{csv_content}\n\n"
            elif file.filename.lower().endswith(('.docx', '.doc')):
                debug_log(f"Processing Word file: {file.filename}")
                word_content = word_processor(file)
                context += f"--- Content from {file.filename} ---\n{word_content}\n\n"
            elif file.filename.lower().endswith(('.pptx', '.ppt')):
                debug_log(f"Processing PowerPoint file: {file.filename}")
                ppt_content = powerpoint_processor(file)
                context += f"--- Content from {file.filename} ---\n{ppt_content}\n\n"
    
    # Process websites
    websites = request.form.getlist('websites')
    debug_log(f"Received {len(websites)} websites")
    
    # If website URLs weren't provided in metadata, use the request list
    if not uploaded_websites:
        uploaded_websites = [url for url in websites if url.strip()]
    
    for url in websites:
        if url.strip():
            debug_log(f"Processing website: {url}")
            website_content = website_processor(url)
            context += website_content + "\n\n"
    
    # Store context and resource info in session
    session['context'] = context
    session['resource_info'] = {
        'files': uploaded_files,
        'websites': uploaded_websites
    }
    debug_log(f"Context size: {len(context)} characters")
    debug_log(f"Stored resource info: {session['resource_info']}")
    
    # Create a nicely formatted resources message
    resources_message = format_resources_message(uploaded_files, uploaded_websites)
    
    return jsonify({
        'status': 'success',
        'message': f'Processed {len(request.files.getlist("files"))} files and {len(websites)} websites',
        'resources': resources_message
    })

@app.route('/api/clear_messages', methods=['POST'])
def clear_messages():
    """Clear chat messages while preserving uploaded resources."""
    debug_log("Clearing chat messages but preserving context and resources")
    
    if 'user_id' in session:
        # Clear chat history but keep context and resource info
        session['chat_history'] = []
        
        return jsonify({
            'status': 'success',
            'message': 'Chat messages cleared while preserving uploaded resources'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'No active session found'
        })

def format_resources_message(files, websites):
    """Format a nice message showing the uploaded resources."""
    if not files and not websites:
        return "No documents provided. You can ask general questions."
    
    message_parts = ["Processed resources:"]
    
    if files:
        file_count = len(files)
        files_text = "Files:" if file_count > 1 else "File:"
        message_parts.append(f"{files_text}")
        for i, filename in enumerate(files):
            message_parts.append(f"{i+1}. {filename}")
    
    if websites:
        # Add a blank line separator if we also had files
        if files:
            message_parts.append("")
            
        website_count = len(websites)
        websites_text = "Websites:" if website_count > 1 else "Website:"
        message_parts.append(f"{websites_text}")
        for i, url in enumerate(websites):
            message_parts.append(f"{i+1}. {url}")
    
    message_parts.append("\nYou can now ask questions about the content of these resources.")
    
    return "\n".join(message_parts)

if __name__ == '__main__':
    debug_log("Starting Flask application")
    app.run(debug=DEBUG)
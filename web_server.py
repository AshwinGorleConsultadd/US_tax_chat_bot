#!/usr/bin/env python3
"""
Web Server for US Tax Chatbot

This Flask server provides a web interface for the US Tax Chatbot,
serving the frontend files and providing API endpoints for chat functionality.

Usage:
    python web_server.py

The server will start on http://localhost:5000
"""

import logging
import os
import sys
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# Upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global chat functions instance
chat_functions = None

# Global upload progress tracking
current_upload_session = None

def initialize_chat_functions():
    """Initialize the chat functions module."""
    global chat_functions
    try:
        from chat_functions import send_message, reset_chat
        chat_functions = {
            'send_message': send_message,
            'reset_chat': reset_chat
        }
        logger.info("Chat functions initialized successfully")
        return True
    except ImportError as e:
        logger.error(f"Failed to import chat functions: {e}")
        return False

@app.route('/')
def index():
    """Serve the main chat interface."""
    return send_from_directory('frontend', 'index.html')

@app.route('/upload.html')
def upload():
    """Serve the upload page."""
    return send_from_directory('frontend', 'upload.html')

@app.route('/api/send_message', methods=['POST'])
def api_send_message():
    """API endpoint to send a message to the chatbot."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        message = data['message'].strip()
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400
        
        logger.info(f"Received message: {message[:100]}...")
        
        # Call the send_message function
        response = chat_functions['send_message'](message)
        
        logger.info(f"Generated response: {response[:100]}...")
        
        return jsonify({
            'success': True,
            'data': {
                'response': response
            }
        })
        
    except Exception as e:
        logger.error(f"Error in send_message API: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/reset_chat', methods=['POST'])
def api_reset_chat():
    """API endpoint to reset the chat context."""
    try:
        logger.info("Resetting chat context")
        
        # Call the reset_chat function
        chat_functions['reset_chat']()
        
        logger.info("Chat context reset successfully")
        
        return jsonify({
            'success': True,
            'data': {
                'message': 'Chat context reset successfully'
            }
        })
        
    except Exception as e:
        logger.error(f"Error in reset_chat API: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check endpoint."""
    try:
        # Check if chat functions are initialized
        if chat_functions is None:
            return jsonify({
                'success': False,
                'error': 'Chat functions not initialized'
            }), 500
        
        # Check OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'OpenAI API key not configured'
            }), 500
        
        return jsonify({
            'success': True,
            'data': {
                'status': 'healthy',
                'chat_functions': 'initialized',
                'openai_api': 'configured'
            }
        })
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Health check failed: {str(e)}'
        }), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """Get the current status of the chatbot."""
    try:
        # Get database info if available
        try:
            from vector_database import VectorDatabase
            db = VectorDatabase()
            db_info = db.get_collection_info()
            document_count = db_info.get('document_count', 0)
        except Exception:
            document_count = 0
        
        return jsonify({
            'success': True,
            'data': {
                'status': 'ready',
                'document_count': document_count,
                'chat_functions': 'available' if chat_functions else 'unavailable'
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Status check failed: {str(e)}'
        }), 500

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload_documents', methods=['POST'])
def api_upload_documents():
    """API endpoint to upload PDF documents and process them."""
    try:
        logger.info("Starting document upload process")
        
        # Check if files are present
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No files provided'
            }), 400
        
        files = request.files.getlist('files')
        
        if not files or all(file.filename == '' for file in files):
            return jsonify({
                'success': False,
                'error': 'No files selected'
            }), 400
        
        # Create uploads directory if it doesn't exist
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
            logger.info(f"Created uploads directory: {UPLOAD_FOLDER}")
        
        # Process uploaded files
        uploaded_files = []
        failed_files = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                
                try:
                    file.save(file_path)
                    uploaded_files.append(file_path)
                    logger.info(f"Successfully saved file: {filename}")
                except Exception as e:
                    logger.error(f"Failed to save file {filename}: {str(e)}")
                    failed_files.append(filename)
            else:
                logger.warning(f"Invalid file type: {file.filename}")
                failed_files.append(file.filename)
        
        if not uploaded_files:
            return jsonify({
                'success': False,
                'error': 'No valid PDF files were uploaded'
            }), 400
        
        logger.info(f"Successfully uploaded {len(uploaded_files)} files")
        
        # Generate unique session ID for progress tracking
        import uuid
        session_id = str(uuid.uuid4())
        progress_file = os.path.join(UPLOAD_FOLDER, f'progress_{session_id}.json')
        
        # Set global upload session
        global current_upload_session
        current_upload_session = {
            'session_id': session_id,
            'progress_file': progress_file,
            'status': 'processing',
            'uploaded_files': uploaded_files,
            'failed_files': failed_files
        }
        
        # Start processing the uploaded files asynchronously
        import threading
        from upload_documents import process_uploaded_files
        
        def process_files_async():
            global current_upload_session
            try:
                logger.info("Starting document processing...")
                success = process_uploaded_files(uploaded_files, progress_file)
                
                if success:
                    logger.info("Document processing completed successfully")
                    # Update session status to completed
                    if current_upload_session and current_upload_session['session_id'] == session_id:
                        current_upload_session['status'] = 'completed'
                else:
                    logger.error("Document processing failed")
                    # Update session status to error
                    if current_upload_session and current_upload_session['session_id'] == session_id:
                        current_upload_session['status'] = 'error'
            except Exception as e:
                logger.error(f"Error in async processing: {str(e)}")
                # Update session status to error
                if current_upload_session and current_upload_session['session_id'] == session_id:
                    current_upload_session['status'] = 'error'
        
        # Start processing in background thread
        processing_thread = threading.Thread(target=process_files_async)
        processing_thread.daemon = True
        processing_thread.start()
        
        # Return immediately with session ID for polling
        return jsonify({
            'success': True,
            'data': {
                'message': f'Upload started for {len(uploaded_files)} documents',
                'uploaded_files': [os.path.basename(f) for f in uploaded_files],
                'failed_files': failed_files,
                'session_id': session_id
            }
        })
    except Exception as e:
        logger.error(f"Error in upload_documents API: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500

@app.route('/api/upload_progress/<session_id>', methods=['GET'])
def api_upload_progress(session_id):
    """API endpoint to get upload progress for a session."""
    try:
        global current_upload_session
        
        # Check if session exists
        if not current_upload_session or current_upload_session['session_id'] != session_id:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        progress_file = current_upload_session['progress_file']
        
        # Read progress from file
        if os.path.exists(progress_file):
            try:
                import json
                with open(progress_file, 'r') as f:
                    progress_data = json.load(f)
                
                return jsonify({
                    'success': True,
                    'data': progress_data
                })
            except Exception as e:
                logger.error(f"Error reading progress file: {e}")
                return jsonify({
                    'success': False,
                    'error': 'Failed to read progress'
                }), 500
        else:
            # Progress file doesn't exist yet, return initial state
            return jsonify({
                'success': True,
                'data': {
                    'status': 'starting',
                    'percentage': 0,
                    'message': 'Starting upload...',
                    'currentFile': '',
                    'currentStage': 'initializing',
                    'totalFiles': len(current_upload_session['uploaded_files']),
                    'processedFiles': 0
                }
            })
        
    except Exception as e:
        logger.error(f"Error in upload_progress API: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Progress check failed: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

def check_environment():
    """Check if the environment is properly configured."""
    logger.info("Checking environment configuration...")
    
    # Check OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable is not set")
        logger.info("Please set your OpenAI API key in the .env file")
        return False
    
    # Check if vector database exists
    db_path = "./chroma_db"
    if not os.path.exists(db_path):
        logger.warning("Vector database not found. Please run upload_documents.py first")
        logger.info("The chatbot will still work but may not have access to your documents")
    
    logger.info("Environment configuration looks good")
    return True

def main():
    """Main function to start the web server."""
    print("=" * 60)
    print("US Tax Chatbot - Web Server")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        print("\nEnvironment check failed. Please fix the issues above.")
        sys.exit(1)
    
    # Initialize chat functions
    if not initialize_chat_functions():
        print("\nFailed to initialize chat functions. Please check the logs above.")
        sys.exit(1)
    
    # Get server configuration
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"\nStarting web server...")
    print(f"Server will be available at: http://{host}:{port}")
    print(f"Debug mode: {debug}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

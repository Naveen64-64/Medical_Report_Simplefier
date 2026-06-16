from flask import Flask, render_template, request, jsonify
from werkzeug.exceptions import HTTPException
from config import Config
from database.db import init_db
from routes.upload_routes import upload_bp
from routes.report_routes import report_bp
from routes.chatbot_routes import chatbot_bp

def create_app():
    """Application factory for the Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    with app.app_context():
        init_db()

    # Register blueprint routes
    app.register_blueprint(upload_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(chatbot_bp)

    @app.route('/')
    def index():
        """Homepage of the application."""
        return render_template('index.html')

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Global error handler. Returns JSON for API requests and styled HTML for page requests."""
        # Determine if request expects JSON
        is_api = (
            request.path.startswith('/api/') or 
            request.path == '/upload' or 
            request.path.endswith('/send') or 
            request.headers.get('Accept') == 'application/json' or
            request.is_json
        )
        
        code = 500
        if isinstance(e, HTTPException):
            code = e.code
            
        error_msg = e.description if isinstance(e, HTTPException) else str(e)
        
        if is_api:
            return jsonify({
                'success': False,
                'error': error_msg
            }), code
            
        # For standard page views, return styled HTML
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error {code} - Medical Report Simplifier</title>
            <link rel="stylesheet" href="/static/css/style.css">
        </head>
        <body style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; background-color: #070a13; color: #f8fafc; text-align: center; padding: 2rem;">
            <div style="background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(16px); padding: 3rem; border-radius: 24px; border: 1px solid rgba(255,255,255,0.08); max-width: 500px; box-shadow: 0 12px 40px rgba(0,0,0,0.5);">
                <h1 style="color: #ef4444; margin-bottom: 1rem; font-size: 2.25rem; font-family: 'Outfit', sans-serif;">System Alert: Error {code}</h1>
                <p style="color: #cbd5e1; margin-bottom: 2rem; font-family: 'Inter', sans-serif; font-size: 0.95rem; line-height: 1.6;">{error_msg}</p>
                <a href="/" class="btn-primary" style="text-decoration: none;">Return Home</a>
            </div>
        </body>
        </html>
        """
        return error_html, code

    return app

app = create_app()

if __name__ == '__main__':
    # Run development server
    app.run(host='127.0.0.1', port=5000, debug=True)

from flask import Blueprint, request, jsonify, session, current_app
import os
from werkzeug.utils import secure_filename
from utils.validations import allowed_file
from utils.helpers import generate_unique_id
from services.pdf_extractor import extract_text_from_pdf
from services.ocr_service import extract_text_from_image
from services.llm_service import simplify_report
from models.report import ReportModel

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handles medical report document upload, text extraction, and simplification."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Ensure uploads folder exists
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file with unique name
        report_id = generate_unique_id()
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{report_id}.{file_ext}"
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        try:
            # Step 1: Extract Text
            original_text = ""
            if file_ext == 'pdf':
                original_text = extract_text_from_pdf(file_path)
            else:
                # OCR for images (png, jpg, jpeg, tiff)
                original_text = extract_text_from_image(file_path)
                
            if not original_text or len(original_text.strip()) == 0:
                return jsonify({'error': 'Could not extract text. Please ensure the file is not empty or corrupted.'}), 422
                
            # Step 2: Simplify Report using Gemini
            simplified_text = simplify_report(original_text)
            
            # Step 2b: Translate if a target language is specified
            lang_code = request.form.get('lang', 'en')
            if lang_code and lang_code != 'en':
                from services.translator import translate_text
                simplified_text = translate_text(simplified_text, lang_code)
            
            # Step 3: Save to database
            user_id = session.get('user_id')  # Can be None if guest user
            ReportModel.create_report(
                report_id=report_id,
                user_id=user_id,
                filename=filename,
                file_path=file_path,
                original_text=original_text,
                simplified_text=simplified_text
            )
            
            return jsonify({
                'success': True,
                'report_id': report_id,
                'message': 'File uploaded and simplified successfully'
            })
            
        except Exception as e:
            # Clean up the file if processing failed
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'error': f"Failed to process document: {str(e)}"}), 500
    else:
        return jsonify({'error': 'Allowed file types are: pdf, png, jpg, jpeg, tiff'}), 400



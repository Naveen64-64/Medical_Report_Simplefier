from flask import Blueprint, render_template, request, jsonify, abort
from models.report import ReportModel
from services.translator import translate_text
from utils.constants import SUPPORTED_LANGUAGES

report_bp = Blueprint('report', __name__)

@report_bp.route('/report/<report_id>')
def view_report(report_id):
    """Renders the detailed simplified report page."""
    report = ReportModel.get_report_by_id(report_id)
    if not report:
        abort(404, description="Report not found")
        
    return render_template('report.html')

@report_bp.route('/api/report/<report_id>')
def get_report_api(report_id):
    """Fetches details for a specific report as JSON."""
    report = ReportModel.get_report_by_id(report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404
        
    report_data = {
        'id': report['id'],
        'filename': report['filename'],
        'original_text': report['original_text'],
        'simplified_text': report['simplified_text'],
        'created_at': report['created_at']
    }
    return jsonify({
        'success': True,
        'report': report_data,
        'languages': SUPPORTED_LANGUAGES
    })

@report_bp.route('/report/<report_id>/translate', methods=['POST'])
def translate_report(report_id):
    """Translates the simplified medical report content into a selected language."""
    data = request.get_json() or {}
    lang_code = data.get('lang')
    
    if not lang_code or lang_code not in SUPPORTED_LANGUAGES:
        return jsonify({'error': 'Invalid or missing target language code'}), 400
        
    report = ReportModel.get_report_by_id(report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404
        
    try:
        translated_text = translate_text(report['simplified_text'], lang_code)
        return jsonify({
            'success': True,
            'translated_text': translated_text,
            'language_name': SUPPORTED_LANGUAGES[lang_code]
        })
    except Exception as e:
        return jsonify({'error': f"Translation failed: {str(e)}"}), 500

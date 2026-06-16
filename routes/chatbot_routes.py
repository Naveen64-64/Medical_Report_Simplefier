from flask import Blueprint, request, jsonify
from models.report import ReportModel
from models.chat_history import ChatHistoryModel
from services.chatbot_service import get_chatbot_response

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/api/report/<report_id>/chat/history')
def get_chat_history(report_id):
    """Fetches chronological conversation logs for a report."""
    report = ReportModel.get_report_by_id(report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404
        
    raw_history = ChatHistoryModel.get_history_by_report(report_id)
    history = [{'sender': msg['sender'], 'message': msg['message']} for msg in raw_history]
    return jsonify({
        'success': True,
        'history': history
    })

@chatbot_bp.route('/report/<report_id>/chat/send', methods=['POST'])
def send_chat_message(report_id):
    """Receives user query, queries the AI helper, and logs the exchange."""
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Message content cannot be empty'}), 400
        
    report = ReportModel.get_report_by_id(report_id)
    if not report:
        return jsonify({'error': 'Report context not found'}), 404
        
    # Get previous chat history for LLM context
    raw_history = ChatHistoryModel.get_history_by_report(report_id)
    history = [{'sender': msg['sender'], 'message': msg['message']} for msg in raw_history]
    
    # Save user message to database
    ChatHistoryModel.add_message(report_id=report_id, sender='user', message=user_message)
    
    # Query Gemini for response
    try:
        bot_response = get_chatbot_response(
            report_context=report['original_text'],
            user_question=user_message,
            chat_history_list=history
        )
        
        # Save bot response to database
        ChatHistoryModel.add_message(report_id=report_id, sender='bot', message=bot_response)
        
        return jsonify({
            'success': True,
            'response': bot_response
        })
    except Exception as e:
        return jsonify({'error': f"Failed to get AI chatbot response: {str(e)}"}), 500

@chatbot_bp.route('/api/chat/general', methods=['POST'])
def general_chat():
    """Receives general health questions when no report context is loaded."""
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    history = data.get('history', [])
    
    if not user_message:
        return jsonify({'error': 'Message content cannot be empty'}), 400
        
    try:
        bot_response = get_chatbot_response(
            report_context=(
                "No report has been uploaded yet. You are a general medical AI assistant. "
                "Answer general health questions or explain how the Medical Report Simplifier works. "
                "Guide the user to upload standard medical reports (PDF/images) on the home page. "
                "Remind them that this information is educational and not medical advice."
            ),
            user_question=user_message,
            chat_history_list=history
        )
        return jsonify({
            'success': True,
            'response': bot_response
        })
    except Exception as e:
        return jsonify({'error': f"Failed to get AI response: {str(e)}"}), 500

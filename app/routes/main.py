from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import current_user
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('catalog.index'))
    
    # Check if user has modern UI preference in cookies
    ui_preference = request.cookies.get('ai_interview_ui')
    template = 'modern_index.html' if ui_preference == 'modern' else 'standalone_index.html'
    
    # Add year to template context for copyright
    year = datetime.now().year
    
    return render_template(template, year=year)

@main.route('/test')
def test():
    """Simple test endpoint to verify basic routing works."""
    return jsonify({
        'status': 'success',
        'message': 'AI Interview Platform API is working correctly'
    })

@main.route('/test-page')
def test_page():
    """Simple test page that doesn't rely on template inheritance."""
    return render_template('test.html')
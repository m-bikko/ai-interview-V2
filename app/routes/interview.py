import os
from flask import Blueprint, render_template, request, jsonify, current_app, url_for, redirect, flash
from flask_login import login_required, current_user
from app import db
from app.models import Profession, Question, Interview, Answer
from app.services.interview_service import InterviewService
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

interview = Blueprint('interview', __name__)
interview_service = InterviewService()

def allowed_audio_file(filename):
    """Check if the file has an allowed audio extension."""
    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'flac', 'webm', 'm4a'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@interview.route('/interview/start/<int:profession_id>/<string:grade>', methods=['GET', 'POST'])
@login_required
def start_interview(profession_id, grade):
    # Validate grade
    if grade not in ['Junior', 'Middle', 'Senior']:
        flash('Invalid grade selected.', 'danger')
        return redirect(url_for('catalog.index'))
    
    # Create new interview
    new_interview, error = interview_service.create_interview(current_user.id, profession_id, grade)
    
    if error:
        flash(error, 'danger')
        return redirect(url_for('catalog.index'))
    
    # Redirect to the interview process
    return redirect(url_for('interview.process', interview_id=new_interview.id))

@interview.route('/interview/process/<int:interview_id>')
@login_required
def process(interview_id):
    # Get the interview
    interview_obj = Interview.query.get_or_404(interview_id)
    
    # Check if the user owns this interview
    if interview_obj.user_id != current_user.id:
        flash('You do not have permission to access this interview.', 'danger')
        return redirect(url_for('catalog.index'))
    
    # Get the profession
    profession = Profession.query.get(interview_obj.profession_id)
    
    # Get questions for this interview
    questions, error = interview_service.get_interview_questions(interview_id)
    
    if error:
        flash(error, 'danger')
        return redirect(url_for('catalog.index'))
    
    # Check if user has modern UI preference in cookies
    ui_preference = request.cookies.get('ai_interview_ui')
    template = 'interview/modern_process.html' if ui_preference == 'modern' else 'interview/process.html'
    
    # Add year to template context for copyright
    year = datetime.now().year
    
    return render_template(
        template,
        title=f'Interview: {profession.name} - {interview_obj.grade}',
        interview=interview_obj,
        profession=profession,
        questions=questions,
        year=year
    )

@interview.route('/interview/question/<int:answer_id>')
@login_required
def question(answer_id):
    # Get the answer (which links to question)
    answer = Answer.query.get_or_404(answer_id)
    
    # Check if the user owns this answer
    interview_obj = Interview.query.get(answer.interview_id)
    if interview_obj.user_id != current_user.id:
        flash('You do not have permission to access this question.', 'danger')
        return redirect(url_for('catalog.index'))
    
    # Get the question
    question = Question.query.get(answer.question_id)
    
    # Get the profession
    profession = Profession.query.get(interview_obj.profession_id)
    
    # Check if user has modern UI preference in cookies
    ui_preference = request.cookies.get('ai_interview_ui')
    template = 'interview/modern_question.html' if ui_preference == 'modern' else 'interview/question.html'
    
    # Add year to template context for copyright
    year = datetime.now().year
    
    return render_template(
        template,
        title=f'Question: {question.question_text[:50]}...',
        interview=interview_obj,
        profession=profession,
        question=question,
        answer=answer,
        year=year
    )

@interview.route('/interview/submit_answer/<int:answer_id>', methods=['POST'])
@login_required
def submit_answer(answer_id):
    # Get the answer
    answer = Answer.query.get_or_404(answer_id)
    
    # Check if the user owns this answer
    interview_obj = Interview.query.get(answer.interview_id)
    if interview_obj.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
    
    # Check if an audio file was uploaded
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'No audio file provided'}), 400
    
    file = request.files['audio']
    
    # If the user didn't select a file
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No audio file selected'}), 400
    
    # Check if the file is allowed
    if not allowed_audio_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file format'}), 400
    
    try:
        # Check file size (limit to 10MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            return jsonify({'success': False, 'error': 'File too large (max 10MB)'}), 400
        
        # Generate a unique filename
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        file_path = os.path.join(current_app.config['AUDIO_FOLDER'], filename)
        
        # Save the file
        file.save(file_path)
        
        # Check if the file was already processed
        if answer.feedback:
            # Delete the newly uploaded file as we don't need it
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return jsonify({
                'success': True, 
                'feedback': answer.feedback,
                'rating': answer.rating,
                'next_url': url_for('interview.process', interview_id=answer.interview_id)
            })
        
        # Process the answer using the service
        answer, error = interview_service.process_answer(answer_id, file_path)
        
        if error:
            return jsonify({'success': False, 'error': error}), 500
        
        # Return success with the feedback
        return jsonify({
            'success': True, 
            'feedback': answer.feedback,
            'rating': answer.rating,
            'next_url': url_for('interview.process', interview_id=answer.interview_id)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@interview.route('/interview/feedback/<int:answer_id>')
@login_required
def feedback(answer_id):
    # Get the answer
    answer = Answer.query.get_or_404(answer_id)
    
    # Check if the user owns this answer
    interview_obj = Interview.query.get(answer.interview_id)
    if interview_obj.user_id != current_user.id:
        flash('You do not have permission to access this feedback.', 'danger')
        return redirect(url_for('catalog.index'))
    
    # Get the question
    question = Question.query.get(answer.question_id)
    
    # Get the profession
    profession = Profession.query.get(interview_obj.profession_id)
    
    # Check if feedback is available
    if not answer.feedback:
        flash('Feedback is not yet available for this answer.', 'warning')
        return redirect(url_for('interview.question', answer_id=answer_id))
    
    # Check if user has modern UI preference in cookies
    ui_preference = request.cookies.get('ai_interview_ui')
    template = 'interview/modern_feedback.html' if ui_preference == 'modern' else 'interview/feedback.html'
    
    # Add year to template context for copyright
    year = datetime.now().year
    
    return render_template(
        template,
        title='Answer Feedback',
        interview=interview_obj,
        profession=profession,
        question=question,
        answer=answer,
        year=year
    )

@interview.route('/interview/complete/<int:interview_id>')
@login_required
def complete(interview_id):
    # Get the interview
    interview_obj = Interview.query.get_or_404(interview_id)
    
    # Check if the user owns this interview
    if interview_obj.user_id != current_user.id:
        flash('You do not have permission to access this interview.', 'danger')
        return redirect(url_for('catalog.index'))
    
    # Get the interview details
    interview_details, error = interview_service.get_interview_details(interview_id)
    
    if error:
        flash(error, 'danger')
        return redirect(url_for('catalog.index'))
    
    # Check if user has modern UI preference in cookies
    ui_preference = request.cookies.get('ai_interview_ui')
    template = 'interview/modern_complete.html' if ui_preference == 'modern' else 'interview/complete.html'
    
    # Add year to template context for copyright
    year = datetime.now().year
    
    return render_template(
        template,
        title='Interview Complete',
        interview=interview_details,
        year=year
    )
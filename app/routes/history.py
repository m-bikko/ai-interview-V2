from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import Interview, Profession
from app.services.interview_service import InterviewService
from datetime import datetime

history = Blueprint('history', __name__)
interview_service = InterviewService()

@history.route('/history')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    min_rating = request.args.get('min_rating')
    max_rating = request.args.get('max_rating')
    
    # Base query for user's interviews
    query = Interview.query.filter_by(user_id=current_user.id)
    
    # Apply rating filters if provided
    if min_rating:
        query = query.filter(Interview.overall_rating >= float(min_rating))
    if max_rating:
        query = query.filter(Interview.overall_rating <= float(max_rating))
    
    # Get paginated results
    interviews = query.order_by(Interview.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    # Get profession names for each interview
    for interview in interviews.items:
        interview.profession_name = Profession.query.get(interview.profession_id).name
    
    # Check if user has modern UI preference in cookies
    ui_preference = request.cookies.get('ai_interview_ui')
    template = 'history/modern_index.html' if ui_preference == 'modern' else 'history/index.html'
    
    # Add year to template context for copyright
    year = datetime.now().year
    
    return render_template(
        template,
        title='Interview History',
        interviews=interviews,
        min_rating=min_rating,
        max_rating=max_rating,
        year=year
    )

@history.route('/history/detail/<int:interview_id>')
@login_required
def interview_detail(interview_id):
    # Get the interview details
    interview_details, error = interview_service.get_interview_details(interview_id)
    
    if error:
        return render_template('errors/404.html'), 404
    
    # Check if the user owns this interview
    if interview_details['id'] != interview_id or \
       Interview.query.get(interview_id).user_id != current_user.id:
        return render_template('errors/403.html'), 403
    
    # Check if user has modern UI preference in cookies
    ui_preference = request.cookies.get('ai_interview_ui')
    template = 'history/modern_detail.html' if ui_preference == 'modern' else 'history/detail.html'
    
    # Add year to template context for copyright
    year = datetime.now().year
    
    return render_template(
        template,
        title=f'Interview: {interview_details["profession"]} - {interview_details["grade"]}',
        interview=interview_details,
        year=year
    )
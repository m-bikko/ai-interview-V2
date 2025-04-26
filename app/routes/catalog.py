from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import Profession, Question, Interview
from sqlalchemy import func
from datetime import datetime

catalog = Blueprint('catalog', __name__)

@catalog.route('/catalog')
@login_required
def index():
    # Get all professions
    professions = Profession.query.all()
    
    # Get all grades
    grades = ['Junior', 'Middle', 'Senior']
    
    # Get count of questions for each profession/grade combination
    profession_grade_counts = {}
    for profession in professions:
        profession_grade_counts[profession.id] = {}
        for grade in grades:
            count = Question.query.filter_by(profession_id=profession.id, grade=grade).count()
            profession_grade_counts[profession.id][grade] = count
    
    # Check if user has modern UI preference in cookies
    ui_preference = request.cookies.get('ai_interview_ui')
    template = 'catalog/modern_index.html' if ui_preference == 'modern' else 'catalog/index.html'
    
    # Add year to template context for copyright
    year = datetime.now().year
    
    return render_template(
        template,
        title='Interview Catalog',
        professions=professions,
        grades=grades,
        question_counts=profession_grade_counts,
        year=year
    )

@catalog.route('/catalog/filter', methods=['GET'])
@login_required
def filter_catalog():
    profession_id = request.args.get('profession_id')
    grade = request.args.get('grade')
    search = request.args.get('search', '')
    
    # Base query
    query = Profession.query
    
    # Apply filters
    if profession_id:
        query = query.filter_by(id=profession_id)
    
    if search:
        query = query.filter(Profession.name.ilike(f'%{search}%'))
    
    # Get results
    professions = query.all()
    
    # Filter grades if specified
    grades = [grade] if grade else ['Junior', 'Middle', 'Senior']
    
    # Get count of questions for each profession/grade combination
    profession_grade_counts = {}
    for profession in professions:
        profession_grade_counts[profession.id] = {}
        for g in grades:
            count = Question.query.filter_by(profession_id=profession.id, grade=g).count()
            profession_grade_counts[profession.id][g] = count
    
    # Check if user has modern UI preference in cookies
    ui_preference = request.cookies.get('ai_interview_ui')
    template = 'catalog/modern_filtered_results.html' if ui_preference == 'modern' else 'catalog/filtered_results.html'
    
    return render_template(
        template,
        professions=professions,
        grades=grades,
        question_counts=profession_grade_counts
    )

@catalog.route('/catalog/profession/<int:profession_id>/grade/<string:grade>')
@login_required
def profession_detail(profession_id, grade):
    # Validate grade
    if grade not in ['Junior', 'Middle', 'Senior']:
        return render_template('errors/404.html'), 404
    
    # Get the profession
    profession = Profession.query.get_or_404(profession_id)
    
    # Get recent interviews for this profession and grade
    recent_interviews = Interview.query.filter_by(
        user_id=current_user.id,
        profession_id=profession_id,
        grade=grade
    ).order_by(Interview.created_at.desc()).limit(5).all()
    
    # Count total interviews for this profession and grade
    total_interviews = Interview.query.filter_by(
        user_id=current_user.id,
        profession_id=profession_id,
        grade=grade
    ).count()
    
    # Check if user has modern UI preference in cookies
    ui_preference = request.cookies.get('ai_interview_ui')
    template = 'catalog/modern_profession_detail.html' if ui_preference == 'modern' else 'catalog/profession_detail.html'
    
    # Add year to template context for copyright
    year = datetime.now().year
    
    return render_template(
        template,
        title=f'{profession.name} - {grade}',
        profession=profession,
        grade=grade,
        recent_interviews=recent_interviews,
        total_interviews=total_interviews,
        year=year
    )
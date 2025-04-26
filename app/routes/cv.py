import os
from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from app import db
from app.models import CV
from app.services.cv_service import CVService
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

cv = Blueprint('cv', __name__)
cv_service = CVService()

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@cv.route('/cvs')
@login_required
def index():
    # Get all CVs for the current user
    cvs = CV.query.filter_by(user_id=current_user.id).order_by(CV.uploaded_at.desc()).all()
    
    # Check if user has modern UI preference in cookies
    ui_preference = request.cookies.get('ai_interview_ui')
    template = 'cv/modern_index.html' if ui_preference == 'modern' else 'cv/index.html'
    
    # Add year to template context for copyright
    year = datetime.now().year
    
    return render_template(
        template,
        title='CV Management',
        cvs=cvs,
        year=year
    )

@cv.route('/cvs/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'cv_file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['cv_file']
        
        # If the user didn't select a file
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        # Check if the file is allowed
        if not allowed_file(file.filename):
            flash('Invalid file format. Only PDF files are allowed.', 'danger')
            return redirect(request.url)
        
        try:
            # Generate a unique filename
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            file_path = os.path.join(current_app.config['CV_FOLDER'], filename)
            
            # Save the file
            file.save(file_path)
            
            # Process the CV using the service
            review = cv_service.process_cv(file_path)
            
            # Create a CV record in the database
            cv_record = CV(
                user_id=current_user.id,
                filename=file.filename,
                file_path=file_path,
                review=review
            )
            
            db.session.add(cv_record)
            db.session.commit()
            
            flash('CV uploaded and reviewed successfully!', 'success')
            return redirect(url_for('cv.view', cv_id=cv_record.id))
            
        except Exception as e:
            flash(f'Error uploading CV: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template(
        'cv/upload.html',
        title='Upload CV'
    )

@cv.route('/cvs/view/<int:cv_id>')
@login_required
def view(cv_id):
    # Get the CV
    cv_record = CV.query.get_or_404(cv_id)
    
    # Check if the user owns this CV
    if cv_record.user_id != current_user.id:
        flash('You do not have permission to access this CV.', 'danger')
        return redirect(url_for('cv.index'))
    
    # Check if user has modern UI preference in cookies
    ui_preference = request.cookies.get('ai_interview_ui')
    template = 'cv/modern_view.html' if ui_preference == 'modern' else 'cv/view.html'
    
    # Add year to template context for copyright
    year = datetime.now().year
    
    return render_template(
        template,
        title=f'CV: {cv_record.filename}',
        cv=cv_record,
        year=year
    )

@cv.route('/cvs/download/<int:cv_id>')
@login_required
def download(cv_id):
    # Get the CV
    cv_record = CV.query.get_or_404(cv_id)
    
    # Check if the user owns this CV
    if cv_record.user_id != current_user.id:
        flash('You do not have permission to download this CV.', 'danger')
        return redirect(url_for('cv.index'))
    
    # Get the directory and filename
    directory = os.path.dirname(cv_record.file_path)
    filename = os.path.basename(cv_record.file_path)
    
    # Send the file
    return send_from_directory(
        directory, 
        filename, 
        as_attachment=True, 
        download_name=cv_record.filename
    )

@cv.route('/cvs/delete/<int:cv_id>', methods=['POST'])
@login_required
def delete(cv_id):
    # Get the CV
    cv_record = CV.query.get_or_404(cv_id)
    
    # Check if the user owns this CV
    if cv_record.user_id != current_user.id:
        flash('You do not have permission to delete this CV.', 'danger')
        return redirect(url_for('cv.index'))
    
    try:
        # Delete the file if it exists
        if os.path.exists(cv_record.file_path):
            os.remove(cv_record.file_path)
        
        # Delete the database record
        db.session.delete(cv_record)
        db.session.commit()
        
        flash('CV deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting CV: {str(e)}', 'danger')
    
    return redirect(url_for('cv.index'))
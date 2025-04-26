import os
from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from app import db
from app.models import User, CV, Interview
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
from PIL import Image

profile = Blueprint('profile', __name__)

def allowed_image_file(filename):
    """Check if the file has an allowed image extension."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_pdf_file(filename):
    """Check if the file has an allowed PDF extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def save_profile_picture(file):
    """Save and process profile picture."""
    # Generate a unique filename
    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
    file_path = os.path.join(current_app.config['PROFILE_PICS_FOLDER'], filename)
    
    # Save the file temporarily
    file.save(file_path)
    
    # Open the image
    img = Image.open(file_path)
    
    # Resize to a square
    size = min(img.width, img.height)
    img_cropped = img.crop((
        (img.width - size) // 2,
        (img.height - size) // 2,
        (img.width + size) // 2,
        (img.height + size) // 2
    ))
    
    # Resize to a standard size (e.g., 200x200 pixels)
    img_resized = img_cropped.resize((200, 200))
    
    # Save the processed image
    img_resized.save(file_path)
    
    return filename

@profile.route('/profile')
@login_required
def index():
    # Get user CVs
    cvs = CV.query.filter_by(user_id=current_user.id).all()
    
    # Get interview counts
    interview_count = Interview.query.filter_by(user_id=current_user.id).count()
    completed_interview_count = Interview.query.filter_by(user_id=current_user.id, completed_at=None).count()
    cv_count = len(cvs)
    
    # Check if user has modern UI preference in cookies
    ui_preference = request.cookies.get('ai_interview_ui')
    template = 'profile/modern_index.html' if ui_preference == 'modern' else 'profile/index.html'
    
    # Add year to template context for copyright
    year = datetime.now().year
    
    return render_template(
        template,
        title='User Profile',
        cvs=cvs,
        interview_count=interview_count,
        completed_interview_count=completed_interview_count,
        cv_count=cv_count,
        year=year
    )

@profile.route('/profile/update', methods=['POST'])
@login_required
def update():
    # Get form data
    full_name = request.form.get('full_name')
    
    if full_name:
        current_user.full_name = full_name
    
    # Check if a profile picture was uploaded
    if 'profile_picture' in request.files:
        file = request.files['profile_picture']
        
        if file.filename != '':
            if not allowed_image_file(file.filename):
                flash('Invalid image format. Only PNG, JPG, JPEG, and GIF files are allowed.', 'danger')
            else:
                # Delete the old profile picture if it's not the default
                if current_user.profile_picture != 'default.jpg':
                    old_picture_path = os.path.join(current_app.config['PROFILE_PICS_FOLDER'], current_user.profile_picture)
                    if os.path.exists(old_picture_path):
                        os.remove(old_picture_path)
                
                # Save the new profile picture
                filename = save_profile_picture(file)
                current_user.profile_picture = filename
    
    # Update actual CV
    if 'actual_cv' in request.files:
        file = request.files['actual_cv']
        
        if file.filename != '':
            if not allowed_pdf_file(file.filename):
                flash('Invalid CV format. Only PDF files are allowed.', 'danger')
            else:
                # Generate a unique filename
                filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                file_path = os.path.join(current_app.config['CV_FOLDER'], filename)
                
                # Save the file
                file.save(file_path)
                
                # Create a CV record in the database
                cv_record = CV(
                    user_id=current_user.id,
                    filename=file.filename,
                    file_path=file_path
                )
                
                db.session.add(cv_record)
                
                # Delete the old actual CV if it exists
                if current_user.actual_cv:
                    old_cv_path = current_user.actual_cv
                    if os.path.exists(old_cv_path):
                        os.remove(old_cv_path)
                
                # Update user's actual CV
                current_user.actual_cv = file_path
    
    # Save changes to the database
    db.session.commit()
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile.index'))

@profile.route('/profile/picture/<filename>')
def profile_picture(filename):
    # First try to find in uploads folder
    try:
        return send_from_directory(current_app.config['PROFILE_PICS_FOLDER'], filename)
    except:
        # If not found, return default image
        return send_from_directory(os.path.join(current_app.root_path, 'static/img'), 'default.jpg')

@profile.route('/profile/download_cv')
@login_required
def download_cv():
    if not current_user.actual_cv:
        flash('No CV available for download.', 'warning')
        return redirect(url_for('profile.index'))
    
    # Get the directory and filename
    directory = os.path.dirname(current_user.actual_cv)
    filename = os.path.basename(current_user.actual_cv)
    
    # Find the original filename from the CV record
    cv_record = CV.query.filter_by(file_path=current_user.actual_cv).first()
    download_name = cv_record.filename if cv_record else filename
    
    # Send the file
    return send_from_directory(
        directory, 
        filename, 
        as_attachment=True, 
        download_name=download_name
    )
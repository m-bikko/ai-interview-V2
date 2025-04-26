from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db, bcrypt
from app.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from datetime import datetime

auth = Blueprint('auth', __name__)

class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        user = User(
            full_name=form.full_name.data,
            email=form.email.data,
            password_hash=hashed_password
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    # Check if user has modern UI preference in cookies
    ui_preference = request.cookies.get('ai_interview_ui')
    template = 'auth/standalone_modern_register.html' if ui_preference == 'modern' else 'auth/simple_register.html'
    
    # Add year to template context for copyright
    year = datetime.now().year
    
    return render_template(template, form=form, year=year)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('catalog.index'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    # Check if user has modern UI preference in cookies
    ui_preference = request.cookies.get('ai_interview_ui')
    template = 'auth/standalone_modern_login.html' if ui_preference == 'modern' else 'auth/simple_login.html'
    
    # Add year to template context for copyright
    year = datetime.now().year
    
    return render_template(template, form=form, year=year)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
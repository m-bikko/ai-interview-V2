from flask import Markup
import re
from datetime import datetime

def nl2br(value):
    """Convert newlines to <br> tags."""
    if not value:
        return ""
    value = str(value)
    return Markup(value.replace('\n', '<br>'))

def get_year():
    """Return the current year."""
    return datetime.now().year

def register_filters(app):
    """Register custom Jinja filters."""
    app.jinja_env.filters['nl2br'] = nl2br
    
    # Register global functions
    app.jinja_env.globals['now'] = {
        'year': get_year
    }
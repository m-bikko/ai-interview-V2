from app import create_app, db
from app.models import User, Profession, Question, Interview, Answer, CV

app = create_app()

# Create a shell context for the Flask CLI
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Profession': Profession, 
            'Question': Question, 'Interview': Interview, 
            'Answer': Answer, 'CV': CV}

if __name__ == '__main__':
    # In production, you wouldn't want to run with debug=True or host='0.0.0.0'
    # which allows connections from any IP address
    import os
    debug = os.environ.get('FLASK_ENV') == 'development'
    port = 5007
    app.run(debug=debug, host='127.0.0.1', port=port)
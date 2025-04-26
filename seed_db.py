import json
import os
from app import create_app, db
from app.models import Profession, Question
from dotenv import load_dotenv

load_dotenv()

def seed_database():
    app = create_app()
    
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        
        # Check if professions and questions already exist
        existing_professions = Profession.query.count()
        existing_questions = Question.query.count()
        
        if existing_professions > 0 or existing_questions > 0:
            print(f"Database already contains {existing_professions} professions and {existing_questions} questions.")
            choice = input("Do you want to clear existing data and reseed? (y/n): ")
            if choice.lower() != 'y':
                print("Seeding cancelled.")
                return
            else:
                # Clear existing data
                Question.query.delete()
                Profession.query.delete()
                db.session.commit()
                print("Existing data cleared.")
        
        # Load questions from JSON file
        try:
            with open('data/questions.json', 'r') as file:
                questions_data = json.load(file)
        except FileNotFoundError:
            print("Error: questions.json file not found in the data directory.")
            return
        
        # Extract unique professions
        profession_names = set(q['profession'] for q in questions_data)
        professions = {}
        
        # Create professions
        for name in profession_names:
            profession = Profession(name=name)
            db.session.add(profession)
            db.session.flush()  # Flush to get the ID
            professions[name] = profession.id
        
        # Create questions
        for q in questions_data:
            question = Question(
                profession_id=professions[q['profession']],
                grade=q['grade'],
                question_text=q['question_text']
            )
            db.session.add(question)
        
        # Commit all changes
        db.session.commit()
        
        # Print summary
        print(f"Database seeded with {len(professions)} professions and {len(questions_data)} questions.")

if __name__ == '__main__':
    seed_database()
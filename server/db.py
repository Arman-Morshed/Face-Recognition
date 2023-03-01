from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def save(embedding_data): 
    db.session.add(embedding_data)
    db.session.commit()

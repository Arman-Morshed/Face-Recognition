from flask_sqlalchemy import SQLAlchemy
from server.model.embedding import EmbeddingModel
from sqlalchemy import select, delete
from server.db import db

def save(embedding_data): 
    db.session.add(embedding_data)
    db.session.commit()

def get(model):
    query = select(EmbeddingModel).where(EmbeddingModel.model == model)
    conn = db.get_engine().connect()
    exe =conn.execute(query)
    return exe.fetchall()
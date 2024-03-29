from server.db import db

class EmbeddingModel(db.Model):
    __tablename__ = "embeddings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(40), unique=False, nullable=False)
    model = db.Column(db.String(40), unique=False, nullable=False)
    embedding = db.Column(db.String(6000), unique=False, nullable=False)
    total_req= db.Column(db.Integer, unique=False, nullable=False)
    precision = db.Column(db.Float(precision=3), unique=False, nullable=True)

    # user_id=db.Column(db.Integer,db.ForeignKey("user_info.id"), unique=False, nullable=False)

    # user_info = db.relationship("UserInfoModel", back_populates="embeddings")
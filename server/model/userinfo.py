# from server.db import db

# class UserInfoModel(db.Model):
#     __tablename__ = "user_info"

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(40), unique=True, nullable=False)
   

#     store_id=db.Column(db.Integer,db.ForeignKey("stores.id"), unique=False, nullable=False)

#     embeddings = db.relationship("EmbeddingModel", back_populates="user_info", lazy="dynamic")
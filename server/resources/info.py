from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask import request, jsonify
from werkzeug.utils import secure_filename
from deepface import DeepFace
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename
import os
from server.db import db
from werkzeug.datastructures import ImmutableMultiDict
from server.schemas import EmbeddingSchema
from server.model.embedding import EmbeddingModel
import json


UPLOADS_PATH = join(dirname(realpath(__file__)),"images")



blp = Blueprint("user", __name__, description="Operation on user info")

@blp.route("/fetch")
class VerifyyUser(MethodView):
     @blp.response(200, EmbeddingSchema(many=True))
     def get(self):
        return EmbeddingModel.query.all()

          

@blp.route("/register")
class RegisterUser(MethodView):
    # @blp.response(201, EmbeddingSchema)
    def post(self):
        # check if the post request has the file part
        if 'file' not in request.files:
            resp = jsonify({'message' : 'No file part in the request'})
            resp.status_code = 400
            return resp
        file = request.files['file']
        data = dict(request.form)
        print(data)
        if file.filename == '':
            resp = jsonify({'message' : 'No file selected for uploading'})
            resp.status_code = 400
            return resp
        if file and allowed_file(file.filename):
            print(file.content_type)
            file_path = os.path.join(UPLOADS_PATH, secure_filename(file.filename))
            file.save(file_path)
            embedding_objs = DeepFace.represent(img_path = file_path, model_name=data['model'])
            
            # embedding_data = EmbeddingModel(name = data['name'], model=data['model'], embedding=embedding_objs[0]['embedding'])
            embedding_data = EmbeddingModel(name = data['name'], model=data['model'], embedding=json.dumps(embedding_objs[0]['embedding']))
            db.session.add(embedding_data)
            db.session.commit()
            os.remove(file_path)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            resp = jsonify({'embeddings' : embedding_objs[0]['embedding']})
            resp.status_code = 201
            return resp
        else:
            resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
            resp.status_code = 400
            return resp


ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

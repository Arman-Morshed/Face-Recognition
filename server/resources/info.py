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
from server.schemas import EmbeddingSchema, VerifySchema
from server.model.embedding import EmbeddingModel
import json
import numpy as np
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError


UPLOADS_PATH = join(dirname(realpath(__file__)),"images")



blp = Blueprint("user", __name__, description="Operation on user info")

@blp.route("/fetch")
class FetchyUser(MethodView):
     @blp.response(200, EmbeddingSchema(many=True))
     def get(self):
        return EmbeddingModel.query.all()
     
@blp.route("/verify")
class VerifyUser(MethodView):
    # @blp.response(200, VerifySchema)
    def post(self):
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

            embedding_test = DeepFace.represent(img_path = file_path, model_name=data['model'])[0]['embedding']
          
            query = select(EmbeddingModel).where(EmbeddingModel.model == data['model'])
            conn = db.get_engine().connect()
            exe =conn.execute(query)
            embedding_data = exe.fetchall()
            
            distance = 9999
            matched_embedding = embedding_data[0]
            for embedding in embedding_data:
                # print(embedding.id)
                embedding_value = json.loads(embedding.embedding)
                d = findCosineDistance(embedding_value, embedding_test)
                if d < distance: 
                    distance = d
                    matched_embedding = embedding
                print(f"{embedding.name} : {distance}")
            print()
            print(f"{matched_embedding.name}: {distance}")
            
            os.remove(file_path)  
              
            return returnResponse(distance, matched_embedding)
        else:
            resp = jsonify({'message' : 'Allowed file types is jpeg'})
            resp.status_code = 400
            return resp


          

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
            
            embedding_data = EmbeddingModel(user_id= data['id'],name = data['name'], model=data['model'], embedding=json.dumps(embedding_objs[0]['embedding']), precision=0.0, total_req=0)
            try:
                db.session.add(embedding_data)
                db.session.commit()
            except IntegrityError:
                abort(400, jsonify({'message': 'Please provide unique id'}))
            os.remove(file_path)                        #delete the file once it's embedding is saved
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            resp = jsonify({'embeddings' : embedding_objs[0]['embedding']})
            resp.status_code = 201
            return resp
        else:
            resp = jsonify({'message' : 'Allowed file types is jpeg'})
            resp.status_code = 400
            return resp


ALLOWED_EXTENSIONS = set([ 'jpeg', 'jpg'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def findCosineDistance(source_representation, test_representation):
    a = np.matmul(np.transpose(source_representation), test_representation)
    b = np.sum(np.multiply(source_representation, source_representation))
    c = np.sum(np.multiply(test_representation, test_representation))
    return 1 - (a / (np.sqrt(b) * np.sqrt(c)))

def returnResponse(distance, matched_embedding): 
    embedding_entry = EmbeddingModel.query.filter_by(user_id=matched_embedding.user_id).first()
    embedding_entry.total_req += 1
    embedding_entry.precision= (matched_embedding.precision * matched_embedding.total_req + distance) / (matched_embedding.total_req + 1)
    db.session.commit()

    if distance < 0.4:                   
        resp = jsonify({
        'id': matched_embedding.user_id,
        'name': matched_embedding.name
        })
        resp.status_code = 201
    else: 
        resp = jsonify({
        'id': -1,
        'name': "Doesn't match with anyone in the database"
        })
        resp.status_code = 404
    return resp
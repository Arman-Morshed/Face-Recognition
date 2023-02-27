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
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
import numpy as np
from sklearn.cluster import KMeans


UPLOADS_PATH = join(dirname(realpath(__file__)),"images")



blp = Blueprint("user", __name__, description="Operation on user info")
threshold = {'VGG-Face': 0.40, 'Facenet': 0.40,'Facenet512': 0.30, 'ArcFace': 0.68, 'Dlib': 0.07, 'SFace': 0.593, 'OpenFace': 0.10,'DeepFace': 0.23, 'DeepID': 0.015  }


@blp.route("/fetch")
class FetchyUser(MethodView):
     @blp.response(200, EmbeddingSchema(many=True))
     def get(self):
        return EmbeddingModel.query.all()
    
     def delete(self):
         EmbeddingModel.__table__.drop(db.engine)
         EmbeddingModel.__table__.create(db.engine)

         return jsonify({'message': "Deleted"})
    
     def post(self): 
        directory_path = "/Users/bdfayaz/Desktop/WG_IMAGE/Face-Recognition/database"
        image_names = []
        image_list = []
# iterate over all files in the directory
        for filename in os.listdir(directory_path):
           
            dir_name = os.path.join(directory_path, filename)
            if os.path.isdir(dir_name):
                for image_file in os.listdir(dir_name):
                    # print(image_file)
                    image_names.append(image_file)
                new_person = {'name': filename, 'image_names': image_names}
                # print(new_person)
                image_list.append(new_person)
                image_names = []

        for im in image_list:
            print('name: {} image name {}'.format(im['name'], im['image_names'][0]))
       
        return jsonify({'data': image_list})
    

@blp.route("/precision/<string:model_name>")
class Precision(MethodView):
    def get(self, model_name): 
        query = select(EmbeddingModel.name,EmbeddingModel.precision).where(EmbeddingModel.model == model_name)
        conn = db.get_engine().connect()
        exe =conn.execute(query)
        precision_data = exe.fetchall()
        
        # p = precision_data.iloc[1,:].to_string(header=False, index=False)

        p = json.dumps([(tuple(row)) for row in precision_data])
        resp = jsonify({'model': model_name, 'precision': p })
        resp.status_code = 200
        return resp

 
     
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
        
            embedding_test = DeepFace.represent(img_path = file_path, model_name=data['model'], detector_backend=data['detector'])[0]['embedding']
          
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
              
            return returnResponse(distance, matched_embedding, data['model'])
        else:
            resp = jsonify({'message' : 'Allowed file types is jpeg'})
            resp.status_code = 400
            return resp


          

@blp.route("/register")
class RegisterUser(MethodView):
    # @blp.response(201, EmbeddingSchema)
    def post(self):
        # check if the post request has the file part
        if len(request.files.getlist('images')) == 0:
            resp = jsonify({'message' : 'No file part in the request'})
            resp.status_code = 400
            return resp
        images = request.files.getlist('images')
        data = dict(request.form)
        print(data)
        print('Image list {}'.format(len(images)))
        embeddings = np.array([[]])

        for file in images: 
            if file.filename == '':
                resp = jsonify({'message' : 'No file selected for uploading'})
                resp.status_code = 400
                return resp
            if file and allowed_file(file.filename):
                print(file.content_type)
                file_path = os.path.join(UPLOADS_PATH, secure_filename(file.filename))
                # embedding_objs = DeepFace.represent(img_path = file_path, model_name=data['model'], detector_backend=data['detector'])
                embedding_objs = getEmbedding(file, file_path, data['model'], data['detector'])
                temp_embedding = np.array([[embedding_objs[i]] for i in range(len(embedding_objs))])
                print('Embedding length: {}'.format(len(embeddings)))
                if len(embeddings) == 1: 
                    embeddings = temp_embedding
                else: 
                    embeddings = np.concatenate((embeddings, temp_embedding), axis=1)

            else:
                resp = jsonify({'message' : 'Allowed file types is jpeg'})
                resp.status_code = 400
                return resp
            
        if len(embeddings) > 0: 
            pass
        embedding_avg = np.mean(embeddings, axis=1)
        embedding_data = EmbeddingModel(user_id= data['id'],name = data['name'], model=data['model'], embedding=json.dumps(embedding_avg.tolist()), precision=0.0, total_req=0)
        try:
            db.session.add(embedding_data)
            db.session.commit()
        except IntegrityError:
            abort(400, jsonify({'message': 'Please provide unique id'}))

        resp = jsonify({'message': 'Image registered','embeddings' : embedding_avg.tolist()})
        resp.status_code = 201
        return resp


ALLOWED_EXTENSIONS = set([ 'jpeg', 'jpg'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def findCosineDistance(source_representation, test_representation):
    a = np.matmul(np.transpose(source_representation), test_representation)
    b = np.sum(np.multiply(source_representation, source_representation))
    c = np.sum(np.multiply(test_representation, test_representation))
    return 1 - (a / (np.sqrt(b) * np.sqrt(c)))

def returnResponse(distance, matched_embedding, model_name): 


    if distance < threshold[model_name]:   
        embedding_entry = EmbeddingModel.query.filter_by(user_id=matched_embedding.user_id).first()
        embedding_entry.total_req += 1
        embedding_entry.precision= (matched_embedding.precision * matched_embedding.total_req + distance) / (matched_embedding.total_req + 1)
        db.session.commit()                
        resp = jsonify({
        'id': matched_embedding.user_id,
        'name': matched_embedding.name, 
        'distance': distance
        })
        resp.status_code = 201
    else: 
        resp = jsonify({
        'id': -1,
        'name': "Doesn't match with anyone in the database"
        })
        resp.status_code = 404
    return resp


def getEmbedding(file, file_path, model, detector):
    file.save(file_path)
    embedding_value = DeepFace.represent(img_path = file_path, model_name=model, detector_backend=detector)
    os.remove(file_path)                        #delete the file once it's embedding is saved
    return embedding_value[0]['embedding']



def getAverage(old_data, new_data):
    return np.mean(np.array(old_data) + np.array(new_data))

#/Users/bdfayaz/Desktop/WG_IMAGE/Face-Recognition/database
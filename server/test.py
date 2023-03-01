from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask import request, jsonify
from werkzeug.utils import secure_filename
from deepface import DeepFace
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename
import os
from server.db import db
import server.db as imgdb
import json
import numpy as np
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
import numpy as np
import random
import server.constants as CS
import server.imgembedding as em
import shutil

from server.model.embedding import EmbeddingModel


blp = Blueprint("test", __name__, description="Testing with data")
test_data = []

@blp.route("/test")
class TestUser(MethodView):
     def get(self):
         return jsonify({'data': test_data})
    
     def post(self): 
        USER_ID = 0
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
       
        for person in image_list:
            name =   person['name']
            images = person['image_names']
            dirname = os.path.join(directory_path, name)
            test_indices = [random.randint(0, len(images)-1) for _ in range(CS.NO_OF_TEST_IMAGES)]
            new_test_data = {'name': name, 'indices': test_indices}
            test_data.append(new_test_data)
            print(len(images))

            tested_img_dir = os.path.join(CS.TEST_IMAGE_LOC, name)
            if not os.path.exists(tested_img_dir):
                os.makedirs(tested_img_dir)

            embeddings = np.array([[]])
            for indice in test_indices: 
                im_name = images[indice]
                im_dir = os.path.join(dirname, im_name)
                shutil.copy(im_dir, tested_img_dir)
                embedding_objs = DeepFace.represent(img_path = im_dir, model_name=CS.MODEL, detector_backend=CS.DETECTOR)[0]['embedding']
                temp_embedding = np.array([[embedding_objs[i]] for i in range(len(embedding_objs))])
                print('Embedding length: {}'.format(len(embeddings)))
                if len(embeddings) == 1: 
                    embeddings = temp_embedding
                else: 
                    embeddings = np.concatenate((embeddings, temp_embedding), axis=1)

            embedding_avg = np.mean(embeddings, axis=1)
            embedding_data = EmbeddingModel(user_id=USER_ID,name = name, model=CS.MODEL, embedding=json.dumps(embedding_avg.tolist()), precision=0.0, total_req=0)
            USER_ID+=1
            try:
                imgdb.save(embedding_data)
            except IntegrityError:
                abort(400, jsonify({'message': 'Please provide unique id'}))

       
        return jsonify({'data': image_list})
    
# /Users/bdfayaz/Desktop/WG_IMAGE/Face-Recognition/server/TestData
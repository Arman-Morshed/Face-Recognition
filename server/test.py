from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask import jsonify
from werkzeug.utils import secure_filename
from deepface import DeepFace
from os.path import join, dirname, realpath
import os
from server.db import db
import server.dbop as imgdb
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
image_list = []



@blp.route("/test")
class TestUser(MethodView):
     def get(self):
         correct_match = 0
         false_match = 0
         no_match = 0
         face_error = 0
         numbers = generate_random_indices(0,10, [1,5,6, 8], 4)
         data = []
         for person in image_list:
            name =   person['name']
            images = person['image_names']
            dirname = os.path.join(CS.directory_path, name)
            trained_indices = find_data_by_name(test_data, name)['indices']
            test_indices = generate_random_indices(0, len(images)-1,trained_indices, 3)

            for indice in test_indices: 
                im_name = images[indice]
                im_dir = os.path.join(dirname, im_name)
                try: 
                    embedding_objs = DeepFace.represent(img_path = im_dir, model_name=CS.MODEL, detector_backend=CS.DETECTOR)[0]['embedding']

                    embedding_data = imgdb.get(CS.MODEL)
            
                    distance = 9999
                    matched_embedding = embedding_data[0]
                    for embedding in embedding_data:
                        # print(embedding.id)
                        embedding_value = json.loads(embedding.embedding)
                        d = em.findCosineDistance(embedding_value, embedding_objs)
                        if d < distance: 
                            distance = d
                            matched_embedding = embedding
                        print(f"{embedding.name} : {distance}")
                    print()
                    print(f"{matched_embedding.name}: {distance}")
                    if distance < CS.threshold[CS.MODEL]:   
                        embedding_entry = EmbeddingModel.query.filter_by(user_id=matched_embedding.user_id).first()
                        embedding_entry.total_req += 1
                        embedding_entry.precision= (matched_embedding.precision * matched_embedding.total_req + distance) / (matched_embedding.total_req + 1)
                        db.session.commit()  

                        if(matched_embedding.name == name): 
                            correct_match+= 1
                        else: 
                            false_match += 1
                    else: 
                        no_match+=1

                except ValueError: 
                    print(f'ValueError - {im_dir}')
                    face_error += 1
         print(f'Model {CS.MODEL}\nNo of Image trained- {CS.NO_OF_TEST_IMAGES}\n Face detector- {CS.DETECTOR}')
         print(f'correct_match - {correct_match}\nfalse_match - {false_match} \nface_error - {face_error} \nNo Match {no_match}' )
         return jsonify({'correct_match': correct_match,'false_match': false_match, 'face_error': face_error })
    
     def post(self): 
        USER_ID = 0
        image_names = []
       
# iterate over all files in the directory
        for filename in os.listdir(CS.directory_path):
            dir_name = os.path.join(CS.directory_path, filename)
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
            dirname = os.path.join(CS.directory_path, name)
            train_indices = [random.randint(0, len(images)-1) for _ in range(CS.NO_OF_TEST_IMAGES)]
            new_test_data = {'name': name, 'indices': train_indices}
            test_data.append(new_test_data)
            print(len(images))

            tested_img_dir = os.path.join(CS.TEST_IMAGE_LOC, name)
            if not os.path.exists(tested_img_dir):
                os.makedirs(tested_img_dir)

            embeddings = np.array([[]])
            for indice in train_indices: 
                im_name = images[indice]
                im_dir = os.path.join(dirname, im_name)
                shutil.copy(im_dir, tested_img_dir)
                try: 
                    embedding_objs = DeepFace.represent(img_path = im_dir, model_name=CS.MODEL, detector_backend=CS.DETECTOR)[0]['embedding']
                except ValueError: 
                    print(f'ValueError - {im_dir}')
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
     
     def delete(self): 
        for file_name in os.listdir(CS.TEST_IMAGE_LOC):
    # create the full path to the file or folder
            file_path = os.path.join(CS.TEST_IMAGE_LOC, file_name)
            # check if the file path is a file or a directory
            if os.path.isfile(file_path):
                # delete the file
                os.remove(file_path)
            elif os.path.isdir(file_path):
                # delete the folder and all its contents recursively
                os.system(f"rm -rf {file_path}")
                print('removing {}'.format(file_path))
        return jsonify({'message': 'Images removed'})
    

def generate_random_indices(start_range, end_range, existing_array, num_numbers):
    # Create a set of all numbers in the given range
    all_numbers = set(range(start_range, end_range + 1))

    # Remove any numbers that are already in the existing array
    existing_numbers = set(existing_array)
    remaining_numbers = all_numbers - existing_numbers

    # If there are not enough remaining numbers to choose from, return an empty list
    if len(remaining_numbers) < num_numbers:
        return []

    # Choose random numbers from the remaining numbers set
    random_numbers = random.sample(remaining_numbers, num_numbers)

    return random_numbers

def find_data_by_name(data_list, name):
    for data_dict in data_list:
        if data_dict['name'] == name:
            return data_dict

    # If no match is found, return None
    return None
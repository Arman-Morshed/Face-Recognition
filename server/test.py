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
import pandas as pd
import time


from server.model.embedding import EmbeddingModel


blp = Blueprint("test", __name__, description="Testing with data")
test_data = []
image_list = []

@blp.route("/test")
class TestUser(MethodView):
     def get(self):
         writer = pd.ExcelWriter(os.path.join(CS.TRAIN_IMAGE_LOC, "{}_{}.xlsx".format(time.time(), CS.MODEL)), engine='xlsxwriter')
         correct_match = 0
         false_match = 0
         no_match = 0
         face_error = 0
         
         report_data = []
         correct_data = []
         false_data = []
         no_data = []
         face_error_data = []
         for person in image_list:
            name =   person['name']
            images = person['image_names']
            dirname = os.path.join(CS.directory_path, name)
            trained_indices = find_data_by_name(test_data, name)['indices']
            test_indices = generate_random_indices(0, len(images)-1,trained_indices, CS.NO_OF_TEST_IMAGES)

            test_img_dir = os.path.join(CS.TEST_IMAGE_LOC, name)
            if not os.path.exists(test_img_dir):
                os.makedirs(test_img_dir)

            for indice in test_indices: 
                im_name = images[indice]
                im_dir = os.path.join(dirname, im_name)
                im_dir = os.path.join(dirname, im_name)
                shutil.copy(im_dir, test_img_dir)
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
                            correct_data.append({"Input name": name, "Matched name": im_name, "Distance": distance, "Verification result": "Corrrect Match", "Threshold": CS.threshold[CS.MODEL]})
                            verification_result = "Corrrect Match"
                        else: 
                            false_match += 1
                            false_data.append({"Input name": name, "Matched name": im_name, "Distance": distance, "Verification result": "False Match", "Threshold": CS.threshold[CS.MODEL]})
        
                    else: 
                        no_match+=1
                        no_data.append({"Input name": name, "Matched name": im_name, "Distance": distance, "Verification result": "No Match", "Threshold": CS.threshold[CS.MODEL]})

                except ValueError: 
                    print(f'ValueError - {im_dir}')
                    face_error += 1
                    face_error_data.append({"Input name": name, "Matched name": "None", "Distance": 0, "Verification result": "Face error", "Threshold": CS.threshold[CS.MODEL]})

         report_data = correct_data + false_data + no_data + face_error_data
         df = pd.DataFrame(report_data)
         df.to_excel(writer, index=False)
         writer.save()
         print(f'Model {CS.MODEL}\nNo of Image trained- {CS.NO_OF_TRAINED_IMAGES}\nFace detector- {CS.DETECTOR}')
         print(f'correct_match - {correct_match}\nfalse_match - {false_match} \nface_error - {face_error} \nNo Match {no_match}' )
         return jsonify({'Model':CS.MODEL,'correct_match': correct_match,'false_match': false_match, 'face_error': face_error, "No Match": no_match })
    
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
            train_indices = [random.randint(0, len(images)-1) for _ in range(CS.NO_OF_TRAINED_IMAGES)]
            new_test_data = {'name': name, 'indices': train_indices}
            test_data.append(new_test_data)
            print(len(images))

            train_img_dir = os.path.join(CS.TRAIN_IMAGE_LOC, name)
            if not os.path.exists(train_img_dir):
                os.makedirs(train_img_dir)

            embeddings = np.array([[]])
            for indice in train_indices: 
                im_name = images[indice]
                im_dir = os.path.join(dirname, im_name)
                shutil.copy(im_dir, train_img_dir)
                try: 
                    embedding_objs = DeepFace.represent(img_path = im_dir, model_name=CS.MODEL, detector_backend=CS.DETECTOR)[0]['embedding']
                    temp_embedding = np.array([[embedding_objs[i]] for i in range(len(embedding_objs))])
                    print('Embedding length: {}'.format(len(embeddings)))
                    if len(embeddings) == 1: 
                        embeddings = temp_embedding
                    else: 
                        embeddings = np.concatenate((embeddings, temp_embedding), axis=1)
                except ValueError: 
                    print(f'ValueError - {im_dir}')
 

            embedding_avg = np.mean(embeddings, axis=1)
            embedding_data = EmbeddingModel(user_id=USER_ID,name = name, model=CS.MODEL, embedding=json.dumps(embedding_avg.tolist()), precision=0.0, total_req=0)
            USER_ID+=1
            try:
                imgdb.save(embedding_data)
            except IntegrityError:
                abort(400, jsonify({'message': 'Please provide unique id'}))

       
        return jsonify({'data': image_list})
     
     def delete(self): 

        # Get a list of all the folders in the directory
        test_folders = [f for f in os.listdir(CS.TEST_IMAGE_LOC) if os.path.isdir(os.path.join(CS.TEST_IMAGE_LOC, f))]

        # Loop through the folders and delete them
        for folder in test_folders:
            folder_path = os.path.join(CS.TEST_IMAGE_LOC, folder)
            try:
                # Use the shutil module to delete the folder and its contents
                shutil.rmtree(folder_path)
                print(f"Successfully deleted {folder_path}")
            except OSError as e:
                print(f"Error: {e.filename} - {e.strerror}")
        
        train_folders = [f for f in os.listdir(CS.TRAIN_IMAGE_LOC) if os.path.isdir(os.path.join(CS.TRAIN_IMAGE_LOC, f))]

        # Loop through the folders and delete them
        for folder in train_folders:
            folder_path = os.path.join(CS.TRAIN_IMAGE_LOC, folder)
            try:
                # Use the shutil module to delete the folder and its contents
                shutil.rmtree(folder_path)
                print(f"Successfully deleted {folder_path}")
            except OSError as e:
                print(f"Error: {e.filename} - {e.strerror}")
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
from deepface import DeepFace
import os
import numpy as np

def getEmbedding(file, file_path, model, detector):
    file.save(file_path)
    embedding_value = DeepFace.represent(img_path = file_path, model_name=model, detector_backend=detector)
    os.remove(file_path)                        #delete the file once it's embedding is saved
    return embedding_value[0]['embedding']


def findCosineDistance(source_representation, test_representation):
    a = np.matmul(np.transpose(source_representation), test_representation)
    b = np.sum(np.multiply(source_representation, source_representation))
    c = np.sum(np.multiply(test_representation, test_representation))
    return 1 - (a / (np.sqrt(b) * np.sqrt(c)))

def getAverage(old_data, new_data):
    return np.mean(np.array(old_data) + np.array(new_data))
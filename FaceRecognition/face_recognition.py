from deepface import DeepFace

def verify(self, img_path1, img_path2, model_name, distance_metric, backend):
    result = DeepFace.verify(img1_path=img_path1, img2_path=img_path2, model_name=model_name, distance_metric=distance_metric, detector_backend=backend, enforce_detection=False)
    return result
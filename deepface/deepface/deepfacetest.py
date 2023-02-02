from deepface import DeepFace

result = DeepFace.verify(img1_path = "/Users/istiakmorsalin/iOffice/deepface-master/tests/dataset/img1.jpg", img2_path = "/Users/istiakmorsalin/iOffice/deepface-master/tests/dataset/img2.jpg")
print(result)
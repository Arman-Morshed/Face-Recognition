TIMEOUT = 1200
NO_OF_TRAINED_IMAGES = 4
NO_OF_TEST_IMAGES = 5
MODEL = 'Facenet'
DETECTOR = 'mtcnn'
directory_path = "/Users/bdfayaz/Desktop/WG_IMAGE/Face-Recognition/database"
REPORT_FILE_NAME = 'report.xlsx'



# Nn configurable constants
TEST_IMAGE_LOC = '/Users/bdfayaz/Desktop/WG_IMAGE/Face-Recognition/server/TestData'
TRAIN_IMAGE_LOC = '/Users/bdfayaz/Desktop/WG_IMAGE/Face-Recognition/server/TrainData'
threshold = {'VGG-Face': 0.40, 'Facenet': 0.40,'Facenet512': 0.30, 'ArcFace': 0.68, 'Dlib': 0.07, 'SFace': 0.593, 'OpenFace': 0.10,'DeepFace': 0.23, 'DeepID': 0.015  }

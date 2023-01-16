from kivymd.app import MDApp
from CaptureImage import camera

class DemoDeepFace(MDApp):
    def build(self):
        return camera.CaptureImage()
    
if __name__ == "__main__":
    DemoDeepFace().run()
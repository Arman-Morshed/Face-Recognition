from kivymd.uix.gridlayout import MDGridLayout
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from PIL import Image as PIImage
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from FaceRecognition import face_recognition
from kivymd.uix.menu import MDDropdownMenu

Builder.load_file('CaptureImage/camera.kv')


class CaptureImage(MDGridLayout):
    camera = ObjectProperty(None)
    capture_button = ObjectProperty(None)
    compare_button = ObjectProperty(None)
    capture_image = ObjectProperty(None)
    dialog = ObjectProperty(None)
    model_button = ObjectProperty(None)
    detector_backend_button = ObjectProperty(None)
    distance_metric_button = ObjectProperty(None)
    capture_image_extension = "user.png"
    modified_image_extension = ""
    compare_image_path = 'Images/arman2.JPG'
    selected_model = 'VGG-Face'
    selected_distance_metric = 'cosine'
    selected_detector_backend = 'opencv'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.camera = self.ids['camera']
        self.capture_image = self.ids['capture_image']
        self.compare_button = self.ids['compare_button']
        self.model_button = self.ids['model_button']
        self.detector_backend_button = self.ids['detector_backend_button']
        self.distance_metric_button = self.ids['distance_metric_button']
        self.configure_model_menu()
        self.configure_detector_backend_menu()
        self.configure_distance_metric_menu()

    def capture_and_reload(self):
        self.camera.export_to_png(self.capture_image_extension)
        img_png = PIImage.open(self.capture_image_extension)
        self.modified_image_extension = "user.jpg"
        img_png.save(self.modified_image_extension)
        self.capture_image.source = self.modified_image_extension
        self.capture_image.reload()

    def compare(self):
        result = face_recognition.verify(
            self, self.modified_image_extension, self.compare_image_path, self.selected_model, self.selected_distance_metric, self.selected_detector_backend)
        print(result)
        self.show_alert_dialog(result)

    def show_alert_dialog(self, result):
        self.dialog = MDDialog(
            text=f"Verified: {result['verified']} \nDistance: {result['distance']}",
            buttons=[
                   MDFlatButton(
                        text="CANCEL",
                        on_release=self.close_dialog
                    )
                ],
            )
        self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss(force=True)

    def configure_model_menu(self):
        models = [
            "VGG-Face",
            "Facenet",
            "Facenet512",
            "OpenFace",
            "DeepFace",
            "DeepID",
            "ArcFace",
            "SFace"
        ]

        menu_items = [
            {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.model_menu_callback(x),
            } for i in models
        ]
        self.model_menu = MDDropdownMenu(
            caller=self.model_button,
            items=menu_items,
            width_mult=4
        )

    def model_menu_callback(self, text_item):
        self.selected_model = text_item
        self.ids.model_label.text = self.selected_model
        self.model_menu.dismiss()

    def configure_distance_metric_menu(self):
        metrics = ["cosine", "euclidean", "euclidean_l2"]
        menu_items = [
            {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.distance_metric_menu_callback(x),
            } for i in metrics
        ]
        self.distance_metric_menu = MDDropdownMenu(
            caller=self.distance_metric_button,
            items=menu_items,
            width_mult=4
        )

    def distance_metric_menu_callback(self, text_item):
        self.selected_distance_metric = text_item
        self.ids.distance_matric_label.text = self.selected_distance_metric
        self.distance_metric_menu.dismiss()

    def configure_detector_backend_menu(self):
        backends = [
            'opencv',
            'ssd',
            'mtcnn',
            'retinaface',
            'mediapipe'
        ]
        menu_items = [
            {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.detector_backend_menu_callback(x),
            } for i in backends
        ]
        self.detector_backend_menu = MDDropdownMenu(
            caller=self.detector_backend_button,
            items=menu_items,
            width_mult=4
        )

    def detector_backend_menu_callback(self, text_item):
        self.selected_detector_backend = text_item
        self.ids.detector_backend_label.text = self.selected_detector_backend
        self.detector_backend_menu.dismiss()

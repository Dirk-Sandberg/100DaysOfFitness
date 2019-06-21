from kivy.uix.modalview import ModalView
from kivymd.elevation import RectangularElevationBehavior
from kivy.uix.floatlayout import FloatLayout
from kivymd.theming import ThemableBehavior
import certifi

from kivymd.backgroundcolorbehavior import SpecificBackgroundColorBehavior
from kivy.network.urlrequest import UrlRequest
from kivymd.updatespinner import MDUpdateSpinner
from random import randint
from kivy.app import App
class ViewSubmissionsPopup(ThemableBehavior, FloatLayout, ModalView,
                    SpecificBackgroundColorBehavior,
                    RectangularElevationBehavior):
    all_submissions = [] # List of all submissions retrieved by firebase
    current_r = 0

    def on_open(self):
        # Get the submissions
        app = App.get_running_app()
        if not app.has_loaded_motivations:
            UrlRequest(app.firebase_url + "motivation.json",
                       on_success=self.success, on_error=self.err, on_failure=self.fail,
                       ca_file=certifi.where())
            self.animate_loading(True)
        #else:
        #    self.display_submission()


    def display_submission(self, *args):
        last_r = self.current_r
        if len(self.all_submissions) == 1:
            # Only one message
            self.current_r = 0
        else:
            # Don't let the message be the same
            while self.current_r == last_r:
                self.current_r = randint(0, len(self.all_submissions)-1)
        submission = self.all_submissions[self.current_r]
        self.ids.name_field.text = "Name: " + submission['name']
        self.ids.location_field.text = "Location: " + submission['location']
        self.ids.message_field.text = submission['message']


    def fail(self, *args):
        self.animate_loading(False)
        print("FAIL", args)

    def err(self, *args):
        self.animate_loading(False)
        print("ERROR", args)

    def success(self, req, *args):
        app = App.get_running_app()
        app.has_loaded_motivations = True
        if req.result:
            # If someone deleted all of them, this fails
            for key in req.result.keys():
                submission = req.result[key]
                self.all_submissions.append(submission)
            self.display_submission()
            self.animate_loading(False)

    def animate_loading(self, active):
        self.ids.spinner.active = active


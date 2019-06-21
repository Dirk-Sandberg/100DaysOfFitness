from kivy.uix.modalview import ModalView
from kivymd.elevation import RectangularElevationBehavior
from kivy.uix.floatlayout import FloatLayout
from kivymd.theming import ThemableBehavior
import certifi
from kivy.clock import Clock
from kivymd.toast import toast
from kivy.app import App
from kivymd.backgroundcolorbehavior import SpecificBackgroundColorBehavior
from kivy.network.urlrequest import UrlRequest

class SubmissionDialog(ThemableBehavior, FloatLayout, ModalView,
                    SpecificBackgroundColorBehavior,
                    RectangularElevationBehavior):
    profane_words = ["fuck", "fuk", "fuc", "fk", "fck", "fkc", "fk", "fc",
                     "bitch", "bitche", "bitches", "bithc", "bithces", "bish",
                     "bishes", "porn", "p0rn", "ass", "dick", "penis", "balls",
                     "pussy", "cunt", "tit", "boob", "boobs", "titties",
                     "niqqa", "niqqer", "nigga", "nigger", "nibba", "nibber",
                     "shit", "shiet", "shite", "ballsack", "clit", "sex",
                     "slut", "whore", "puss", "pussi"]
    #def __init__(self, **kwargs):
    #    super().__init__(**kwargs)
    def on_open(self):
        Clock.schedule_once(self.set_field_focus, .3)

    def set_field_focus(self, interval):
        self.ids.name_field.focus = True

    def ok_click(self, name, loc, msg):
        if not name:
            name = "Anonymous"
        if not loc:
            loc = "Anonymous"
        if not msg:
            toast("A message is required")
            return
        name = name.title()
        if len(name.split(" ")) == 2:
            name = name.split(" ")[0] + " " + name.split(" ")[1][0] + "."
        loc = loc.title()
        msg = '. '.join(i.capitalize() for i in msg.split('. '))

        # Simple profanity filter
        if set(msg.lower().split(" ")).intersection(set(self.profane_words)):
            # There's a match between profane words and the message
            # Pretend to the user that it went through
            self.success()
            self.dismiss()
            return
        # Upload the message to firebase
        app = App.get_running_app()
        data = '{"name": "%s", "location": "%s", "message": "%s",' \
               '"id": "%s"}'%(name, loc, msg, app.user_localId )
        UrlRequest(App.get_running_app().firebase_url + "motivation.json",
                   req_body=data, on_failure=self.fail, on_error=self.err,
                   on_success=self.success, ca_file=certifi.where())

        self.dismiss()

    def fail(self, *args):
        print("FAIL", args)

    def err(self, *args):
        print("ERROR", args)

    def success(self, *args):
        toast("Submission received")

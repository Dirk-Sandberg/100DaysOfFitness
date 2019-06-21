import sys
sys.path.append("/".join(x for x in __file__.split("/")[:-1]))

from kivy.app import App
#from kivy.utils import platform
from kivy.uix.screenmanager import CardTransition
from kivy.network.urlrequest import UrlRequest
from kivy.graphics import Rectangle
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.properties import ColorProperty, StringProperty
from kivy.clock import Clock
from kivymd.theming import ThemeManager
from kivymd.menus import MDDropdownMenu
from kivymd.pickers import MDDatePicker, MDThemePicker
from kivymd.label import MDLabel
from kivymd.toast import toast
from kivymd.mdpickers import StandardMDDatePicker
import certifi
from random import randint
from datetime import date, timedelta
from functools import partial
import calendar
import ast

from viewsubmissionspopup import ViewSubmissionsPopup
from submissiondialog import SubmissionDialog

class MainApp(App):
    # Color themes
    firebase_url = "https://one-hundred-days-of-sweat.firebaseio.com/"
    theme_cls = ThemeManager()
    md_theme_picker = None
    theme_cls.primary_palette = 'Blue'
    theme_cls.primary_hue = '700'
    theme_cls.accent_palette = 'DeepOrange'
    theme_cls.theme_style = 'Light'
    is_editing_start_date = False
    iphone_x_notch_height = dp(30)
    notch_color = ColorProperty([1, 1, 1, 0])
    notch_source = StringProperty("FirebaseLoginScreen/wallpaper.jpg")
    # app height should be 30 px less if run on iphones type X, XR, or XS MAX
    window_height = Window.height if (Window.height != 2436 and Window.height != 2688 and Window.height != 1792) else Window.height - iphone_x_notch_height

    options_menu = None  # Dropdown menu
    celebrations = ["Nice job!", "Keep it up!", "Way to go!", "Good going!",
                    "Yes!!", "You rock!", "Great job!", "Sweet!", "Fantastic!",
                    "Awesome!"]
    workout_suggestions = ["Jumping jacks", "Body weight squats", "Jogging",
                           "Knee push-ups", "Sit ups", "Jogging", "Lunges"]
    saved_dates_file = "saved_dates.txt"
    hundred_days_file = "hundred_days.txt"
    color_theme_file = "color_theme.txt"
    hundred_days = []
    saved_dates = []
    bottom_label = None
    date_picker = None  # Main widget
    has_loaded_motivations = False  # Used to make sure we only load them once
    submission_dialog = None
    view_submissions_popup = None

    def on_start(self):
        self.submission_dialog = SubmissionDialog()
        self.view_submissions_popup = ViewSubmissionsPopup()

    def on_login(self):
    #def on_start(self):
        # Fix file names on ios
        self.saved_dates_file = App.get_running_app().user_data_dir + "/" + self.saved_dates_file
        self.hundred_days_file = App.get_running_app().user_data_dir + "/" + self.hundred_days_file
        self.color_theme_file = App.get_running_app().user_data_dir + "/" + self.color_theme_file

        # Debug
        debug = False
        if debug:
            # Clear all saved info by the app, like the user login credentials
            # Forces user to sign in again (for testing the login screen)
            with open(self.root.ids.firebase_login_screen.refresh_token_file, "w") as f:
                f.write("")
            with open(self.saved_dates_file, "w") as f:
                f.write("")
            with open(self.hundred_days_file, "w") as f:
                f.write("")
            with open(self.color_theme_file, "w") as f:
                f.write("")

        # Read the color theme file
        try:
            with open(self.color_theme_file, "r") as f:
                self.theme_cls.primary_palette = f.read()
        except:
            # No saved color theme
            pass
        # Read the saved workout dates before loading calendar
        try:
            with open(self.saved_dates_file, "r") as f:
                self.saved_dates = ast.literal_eval(f.read())
        except:
            pass

        # Try to get their start time if it's not their first time in the app
        try:
            with open(self.hundred_days_file, "r") as f:
                self.hundred_days = ast.literal_eval(f.read())
            # Immediately build the calendar
            self.build_interface()
            # Immediately switch to the main screen
            self.switch_to_main_screen()
        except:
            # It is their first time in the app
            # Open the start date picker popup
            self.open_start_date_menu(is_editing_start_date=False)
            # Wait half a second while the popup is displayed, then quietly
            # switch screens behind it
            Clock.schedule_once(partial(self.switch_to_main_screen, duration=0), .5)

        # Build dropdown list
        items = []
        options = [['View Motivation', self.view_motivation],
                   ['Send Motivation', self.submit_motivation],
                   ['Change Color', self.change_color_theme],
                   ['Edit Start Date', self.open_start_date_menu]]
        for option in options:
            items.append({'viewclass': 'OneLineListItem',
                                   'text': option[0],
                                   'on_release': option[1]
                                   })
        self.options_menu = MDDropdownMenu(items=items, width_mult=4)

        # Attempt to finish the options menu
        UrlRequest(self.firebase_url + "num_users.json",
                   ca_file=certifi.where(), on_success=self.finish_dropdown_menu)


    def switch_to_main_screen(self,*args, duration=1):
        # Switch to the main app screen
        self.root.ids.sm.transition = CardTransition(direction='down', mode='pop', duration=duration)
        # Quickly add an image to the current firebase screen to fix eyesore when changing screen
        screen = self.root.ids.firebase_login_screen.ids.screen_manager.current
        screen = self.root.ids.firebase_login_screen.ids[screen]
        with screen.canvas.before:
            Rectangle(size=screen.size, pos=screen.pos, source='FirebaseLoginScreen/wallpaper.jpg')

        self.root.ids.sm.current = 'main_screen'

    def finish_dropdown_menu(self, req, *args):
        num_users = req.result
        # Can only finish building dropdown menu after querying firebase
        self.options_menu.items.append({'viewclass': 'MDLabel',
                      'text': '[i]Global participants: %s[/i]'%num_users,
                      'halign': 'center','markup': True})


    def open_start_date_menu(self, *args,is_editing_start_date=True):
        self.is_editing_start_date = is_editing_start_date
        if self.options_menu:
            self.options_menu.dismiss()
        StandardMDDatePicker(self.choose_start_date).open()

    def choose_start_date(self, start_date):
        # Get the next 100 days
        current_date = start_date
        self.hundred_days = []
        self.hundred_days.append([current_date.day, current_date.month,
                                  current_date.year])
        for i in range(99):
            next_date = current_date + timedelta(days=1)
            current_date = next_date
            self.hundred_days.append([current_date.day, current_date.month,
                                     current_date.year])

        # Save their hundred days
        with open(self.hundred_days_file, "w") as f:
            f.write(str(self.hundred_days))
        self.build_interface()

    def build_interface(self):
        # Change notch color and image
        self.notch_color = self.theme_cls.primary_color
        self.notch_source = ""

        # Buid the calendar widget
        if self.date_picker:
            # The user picked a new date and needs to update the calendar
            self.root.ids.main_layout.remove_widget(self.date_picker)
            self.root.ids.main_layout.remove_widget(self.bottom_label)

        self.date_picker = MDDatePicker(elevation=0)
        self.root.ids.main_layout.add_widget(self.date_picker)

        # Build the scrolling suggestion field
        day = calendar.day_name[date.today().weekday()]  # 'Wednesday'
        colored_label = self.date_picker.ids.label_full_date

        self.bottom_label = MDLabel(text=day + "'s suggested activity: " +
                             self.workout_suggestions[date.today().weekday()],
                        text_color=colored_label.text_color,
                        theme_text_color='Custom',
                        halign='center')
        colored_label.bind(text_color=self.reset_bottom_text_color)
        self.root.ids.main_layout.add_widget(self.bottom_label)

    def reset_bottom_text_color(self, *args):
        self.bottom_label.text_color = self.date_picker.ids.label_full_date.text_color

    def display_menu(self, *args):
        self.options_menu.open(self.root.ids.toolbar)

    def open_verify_workout_popup(self, daybutton, active):
        # Saves the date that was selected to local storage
        # displays a small popup (toasts) a compliment
        day = int(daybutton.owner.sel_day)
        month = int(daybutton.owner.sel_month)
        year = int(daybutton.owner.sel_year)
        if active:
            self.saved_dates.append([day, month, year])
            with open(self.saved_dates_file, "w") as f:
                f.write(str(self.saved_dates))
            self.toast_random_celebration()
        else:
            self.saved_dates.remove([day,month,year])
            with open(self.saved_dates_file, "w") as f:
                f.write(str(self.saved_dates))

    def toast_random_celebration(self):
        # Choose a random celebration from the list of celebrations
        r = randint(0, len(self.celebrations)-1)
        toast(self.celebrations[r])

    def view_motivation(self, *args):
        self.options_menu.dismiss()
        self.view_submissions_popup.open()

    def submit_motivation(self, *args):
        self.options_menu.dismiss()
        self.submission_dialog.open()

    def change_color_theme(self, *args):
        # Open up the themepicker popup
        self.options_menu.dismiss()
        if not self.md_theme_picker:
            self.md_theme_picker = MDThemePicker()
        self.md_theme_picker.open()

    def save_color_theme(self, *args):
        with open(self.color_theme_file, "w") as f:
            f.write(self.theme_cls.primary_palette)

    def update_notch_color(self, *args):
        self.notch_color = self.theme_cls.primary_color

    def calculate_remaining_days(self, *args):
        time_remaining = date.today() - date(self.hundred_days[-1][2],self.hundred_days[-1][1],self.hundred_days[-1][0])
        if time_remaining.days > 0:
            # Past the end date
            return "100 Days of Sweat Complete!"
        else:
            return "Days remaining: " + str(abs(time_remaining.days))
MainApp().run()
"""
Pickers
=======

Copyright (c) 2015 Andrés Rodríguez and KivyMD contributors -
    KivyMD library up to version 0.1.2
Copyright (c) 2019 Ivanov Yuri and KivyMD contributors -
    KivyMD library version 0.1.3 and higher

For suggestions and questions:
<kivydevelopment@gmail.com>

This file is distributed under the terms of the same license,
as the Kivy framework.

Includes date, time and color picker
"""

import datetime
import calendar
from datetime import date

from kivy.lang import Builder
from kivy.uix.modalview import ModalView
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, NumericProperty, ObjectProperty,\
    BooleanProperty, ListProperty, OptionProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

from kivymd.label import MDLabel
from kivymd.button import MDIconButton
from kivymd.theming import ThemableBehavior
from kivymd.backgroundcolorbehavior import SpecificBackgroundColorBehavior
from kivymd.ripplebehavior import CircularRippleBehavior
from kivymd.elevation import RectangularElevationBehavior
from kivymd.color_definitions import colors, palette

Builder.load_string('''
#:import calendar calendar
#:import platform platform


<MDDatePicker>
    cal_layout: cal_layout
    size_hint: (None, None)
    size: [Window.width, app.window_height - app.root.ids.toolbar.height-dp(52)]
    pos_hint: {'center_x': .5, 'center_y': .5}
    #pos: [0, dp(52)]
    canvas:
        Color:
            rgb: app.theme_cls.primary_color
        Rectangle:
            size:
                [Window.width, app.window_height - app.root.ids.toolbar.height]
            pos:
                [0,0]
        Color:
            rgb: app.theme_cls.bg_normal
        Rectangle:
        # height should be Window.height - toolbar.height - label1.height - label2.height - label3.height - weekdaylabel.height
            size: 
                [Window.width, app.window_height - app.root.ids.toolbar.height - dp(29) - dp(10) - dp(30) - dp(25) - dp(25) ]#cal_layout.height/cal_layout.cols]#dp(484)-dp(106)]
            pos:
                [root.pos[0], dp(52)]
                
    MDLabel:
        id: label_full_date
        font_style: 'H4'
        text_color: root.specific_text_color
        theme_text_color: 'Custom'
        size_hint: (None, None)
        size:
            [root.width, dp(30)]
        pos:
            (root.pos[0] + (root.size[0] - self.size[0])/2, app.window_height - app.root.ids.toolbar.height - dp(25))
            #[root.pos[0] + (root.size[0] - self.size[0])/2, label_full_date.pos[1] - self.size[1] - dp(10)]
        line_height: .84
        valign: 'top'
        halign: 'center'
        text_size:
            [root.width, None]\
            if root.theme_cls.device_orientation == 'portrait'\
            else [dp(149), None]
        bold: True
        text:
            root.fmt_lbl_date(root.today.year, root.today.month, root.today.day,\
            root.theme_cls.device_orientation)

    MDLabel:
        id: label_remaining_days
        font_style: 'Subtitle1'
        text_color: root.specific_text_color
        theme_text_color: 'Custom'
        size_hint: (None, None)
        size: root.width, dp(30)
        pos:
            [root.pos[0] + (root.size[0] - self.size[0])/2, label_full_date.pos[1] - self.size[1] - dp(5)]
        valign: 'bottom'
        halign: 'center'
        text: app.calculate_remaining_days()#str(root.sel_year)

    MDLabel:
        id: label_month_selector
        font_style: 'Body2'
        text:
            calendar.month_name[root.month].capitalize() + ' ' + str(root.year)
        size_hint: (None, None)
        size: root.width, dp(30)
        pos: [root.pos[0] + (self.size[0]-root.size[0])/2, label_remaining_days.pos[1] - self.size[1] - dp(17)]
        text_color: [0,0,0,1]#app.theme_cls.primary_color #app.date_picker.ids.label_full_date.text_color if app.date_picker else [1,1,1,1]
        theme_text_color: 'Custom'
        valign: "middle"
        halign: "center"

    MDIconButton:
        icon: 'chevron-left'
        color: app.theme_cls.primary_color
        theme_text_color: 'Custom'
        pos: [root.pos[0] + dp(18), label_month_selector.pos[1] - (self.size[1] - label_month_selector.size[1])/2.0]
        on_release: root.change_month('prev')

    MDIconButton:
        icon: 'chevron-right'
        color: app.theme_cls.primary_color
        theme_text_color: 'Custom'
        pos: [root.pos[0] + root.size[0] - dp(18) - self.size[0], label_month_selector.pos[1] - (self.size[1] - label_month_selector.size[1])/2.0]
        on_release: root.change_month('next')

    GridLayout:
        id: cal_layout
        cols: 7
        size: (Window.width, app.window_height - app.root.ids.toolbar.height - label_remaining_days.size[1] - dp(10) - label_full_date.size[1] - dp(10) - label_month_selector.size[1] - dp(25) - dp(25))
        #col_default_width: self.size[0]/7
        size_hint: (None, None)
        padding: [dp(6),0,0,0]
        pos: [0, dp(52)]




<DayButton>
    #size_hint: None, None
    #size:
    #    (self.owner.width/7, self.owner.width/7) if root.theme_cls.device_orientation == 'portrait'\
    #    else (dp(32), dp(32))
    on_release:
        self.owner.set_selected_widget(self)
        app.open_verify_workout_popup(self, not checkbox.active)
        checkbox._do_press()
    MDLabel:
        pos_hint: {"right": .3, "center_y": .5}
        size_hint: .5, 1
        font_style: 'Caption'
        theme_text_color:
            'Custom'# if root.is_today and not root.is_selected else 'Primary'
        text_color: root.theme_cls.primary_color
        opposite_colors:
            False
            #root.is_selected if root.owner.sel_month == root.owner.month\
            #and root.owner.sel_year == root.owner.year\
            #and str(self.text) == str(root.owner.sel_day) else False
        #size_hint_x: None
        valign: 'middle'
        halign: 'right'
        text: root.text
        markup: True
    MDCheckbox:
        id: checkbox
        pos_hint: {"right": 1, "center_y": .5}
        size_hint: .75, 1
        #color: 1,1,1,1
        selected_color: app.theme_cls.primary_color
        #ripple_rad: 10
        on_release:
            root.owner.set_selected_widget(root)
            app.open_verify_workout_popup(root, self.active)
    

<WeekdayLabel>
    font_style: 'Caption'
    theme_text_color: 'Secondary'
    size_hint: (None, None)
    size: dp(40), dp(40)
    pos_hint: {"center_x": .5, "center_y": .5}
    text_size: self.size
    valign: 'middle'
    halign: 'right'

''')


from kivy.app import App
from kivymd.selectioncontrols import MDCheckbox
from kivy.uix.gridlayout import GridLayout
class DayButton(ButtonBehavior, ThemableBehavior, FloatLayout):
    text = StringProperty()
    owner = ObjectProperty()
    is_today = BooleanProperty(False)


    #def on_release(self):
    #    self.owner.set_selected_widget(self)


class WeekdayLabel(MDLabel):
    pass


class MDDatePicker(FloatLayout, ThemableBehavior, RectangularElevationBehavior,
                   SpecificBackgroundColorBehavior):#, ModalView):
    _sel_day_widget = ObjectProperty()
    cal_list = None
    cal_layout = ObjectProperty()
    sel_year = NumericProperty()
    sel_month = NumericProperty()
    sel_day = NumericProperty()
    day = NumericProperty()
    month = NumericProperty()
    year = NumericProperty()
    today = date.today()
    #callback = ObjectProperty()
    background_color = ListProperty([0, 0, 0, .7])

    class SetDateError(Exception):
        pass

    def __init__(self, year=None, month=None, day=None,
                 firstweekday=0, **kwargs):
        #self.callback = callback
        self.cal = calendar.Calendar(firstweekday)
        self.sel_year = year if year else self.today.year
        self.sel_month = month if month else self.today.month
        self.sel_day = day if day else self.today.day
        self.month = self.sel_month
        self.year = self.sel_year
        self.day = self.sel_day
        super().__init__(**kwargs)
        self.generate_cal_widgets()
        self.update_cal_matrix(self.sel_year, self.sel_month)
        self.set_month_day(self.sel_day)

    def fmt_lbl_date(self, year, month, day, orientation):
        d = datetime.date(int(year), int(month), int(day))
        separator = '\n' if orientation == 'landscape' else ' '
        return d.strftime('%a,').capitalize() + separator + d.strftime(
            '%b').capitalize() + ' ' + str(day).lstrip('0')

    def set_date(self, year, month, day):
        try:
            date(year, month, day)
        except Exception as e:
            print(e)
            if str(e) == "day is out of range for month":
                raise self.SetDateError(
                    " Day %s day is out of range for month %s" % (day, month))
            elif str(e) == "month must be in 1..12":
                raise self.SetDateError(
                    "Month must be between 1 and 12, got %s" % month)
            elif str(e) == "year is out of range":
                raise self.SetDateError(
                    "Year must be between %s and %s, got %s" % (
                        datetime.MINYEAR, datetime.MAXYEAR, year))
        else:
            self.sel_year = year
            self.sel_month = month
            self.sel_day = day
            self.month = self.sel_month
            self.year = self.sel_year
            self.day = self.sel_day
            self.update_cal_matrix(self.sel_year, self.sel_month)
            self.set_month_day(self.sel_day)

    def set_selected_widget(self, widget):
        self.sel_month = int(self.month)
        self.sel_year = int(self.year)
        self.sel_day = int(widget.text.replace("[b]","").replace("[/b]","").replace("[u]","").replace("[/u]",""))
        self._sel_day_widget = widget

    def set_month_day(self, day):
        for idx in range(len(self.cal_list)):
            if str(day) == str(self.cal_list[idx].text):
                self._sel_day_widget = self.cal_list[idx]
                self.sel_day = int(self.cal_list[idx].text)
                self._sel_day_widget = self.cal_list[idx]
                self.cal_list[idx].is_selected = True

    def update_cal_matrix(self, year, month):
        try:
            dates = [x for x in self.cal.itermonthdates(year, month)]
        except ValueError as e:
            if str(e) == "year is out of range":
                pass
        else:
            self.year = year
            self.month = month
            for idx in range(len(self.cal_list)):
                self.cal_list[idx].ids.checkbox.active = False
                if idx >= len(dates) or dates[idx].month != month:
                    self.cal_list[idx].disabled = True
                    self.cal_list[idx].text = ''
                    self.cal_list[idx].opacity = 0
                else:
                    self.cal_list[idx].disabled = False
                    self.cal_list[idx].text = str(dates[idx].day)
                    self.cal_list[idx].is_today = dates[idx] == self.today
                    #self.cal_list[idx].opacity = 1
                    # Mark them as part of the 100 day challenge
                    self.cal_list[idx].opacity = .4
                    self.cal_list[idx].text = self.cal_list[idx].text.replace("[b]","").replace("[/b]","")
                    if [dates[idx].day, dates[idx].month, dates[idx].year] in \
                            App.get_running_app().hundred_days:
                        self.cal_list[idx].opacity = 1
                        self.cal_list[idx].text = "[b]" + self.cal_list[idx].text + "[/b]"
                    # Mark them already checked if saved by user
                    if [dates[idx].day, dates[idx].month, dates[idx].year] in\
                        App.get_running_app().saved_dates:
                        self.cal_list[idx].ids.checkbox.active = True
                    # Special mark for the first and last day of challenge, and today
                    if [dates[idx].day, dates[idx].month, dates[idx].year] in\
                        [App.get_running_app().hundred_days[-1], App.get_running_app().hundred_days[0],
                         [self.today.day, self.today.month, self.today.year]]:
                        self.cal_list[idx].text = "[u]" + self.cal_list[idx].text + "[/u]"


    def generate_cal_widgets(self):
        cal_list = []
        from kivy.uix.widget import Widget
        for day in self.cal.iterweekdays():
            g = GridLayout(rows=1)
            g.add_widget(Widget())#size_hint=(None, None)))
            g.add_widget(WeekdayLabel(text=calendar.day_abbr[day][0].upper()))
            g.add_widget(Widget())#size_hint=(None,None)))
            self.cal_layout.add_widget(g)#
            #    WeekdayLabel(text=calendar.day_abbr[day][0].upper()))
        for i in range(6 * 7):  # 6 weeks, 7 days a week
            db = DayButton(owner=self)
            cal_list.append(db)
            self.cal_layout.add_widget(db)
        self.cal_list = cal_list

    def change_month(self, operation):
        op = 1 if operation is 'next' else -1
        sl, sy = self.month, self.year
        m = 12 if sl + op == 0 else 1 if sl + op == 13 else sl + op
        y = sy - 1 if sl + op == 0 else sy + 1 if sl + op == 13 else sy
        self.update_cal_matrix(y, m)


Builder.load_string('''
#:import MDFlatButton kivymd.button.MDFlatButton
#:import MDCheckbox kivymd.selectioncontrols.MDCheckbox
#:import CircularTimePicker kivymd.vendor.circularTimePicker.CircularTimePicker
#:import dp kivy.metrics.dp


<MDTimePicker>
    size_hint: (None, None)
    size: [dp(270), dp(335) + dp(95)]
    pos_hint: {'center_x': .5, 'center_y': .5}

    canvas:
        Color:
            rgba: self.theme_cls.bg_light
        Rectangle:
            size: [dp(270), dp(335)]
            pos: [root.pos[0], root.pos[1] + root.height - dp(335) - dp(95)]
        Color:
            rgba: self.theme_cls.primary_color
        Rectangle:
            size: [dp(270), dp(95)]
            pos: [root.pos[0], root.pos[1] + root.height - dp(95)]
        Color:
            rgba: self.theme_cls.bg_dark
        Ellipse:
            size: [dp(220), dp(220)]
            pos:
                root.pos[0] + dp(270) / 2 - dp(220) / 2, root.pos[1]\
                + root.height - (dp(335) / 2 + dp(95)) - dp(220) / 2 + dp(35)

    CircularTimePicker:
        id: time_picker
        pos: (dp(270) / 2) - (self.width / 2), root.height - self.height
        size_hint: [.8, .8]
        pos_hint: {'center_x': .5, 'center_y': .585}

    MDFlatButton:
        width: dp(32)
        id: ok_button
        pos:
            root.pos[0] + root.size[0] - self.width - dp(10),\
            root.pos[1] + dp(10)
        text: "OK"
        on_release: root.close_ok()
''')


class MDTimePicker(ThemableBehavior, FloatLayout, ModalView,
                   RectangularElevationBehavior):
    time = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_time = self.ids.time_picker.time

    def set_time(self, time):
        try:
            self.ids.time_picker.set_time(time)
        except AttributeError:
            raise TypeError(
                "MDTimePicker._set_time must receive a datetime object, "
                "not a \"" + type(time).__name__ + "\"")



Builder.load_string('''
#:import MDTabbedPanel kivymd.tabs.MDTabbedPanel
#:import MDTab kivymd.tabs.MDTab


<ColorSelector>
    size: dp(50), dp(50)
    pos: self.pos
    size_hint: (None, None)
    canvas:
        Color:
            rgba: root.rgb_hex(root.color_name)
        Ellipse:
            size: self.size
            pos: self.pos


<AccentColorSelector@ColorSelector>
    on_release: app.theme_cls.accent_palette = root.color_name


<PrimaryColorSelector@ColorSelector>
    on_release: 
        app.theme_cls.primary_palette = root.color_name
        app.update_notch_color()


<MDThemePicker>
    size_hint: (None, None)
    size: dp(284), dp(120)+dp(230)
    pos_hint: {'center_x': .5, 'center_y': .5}
    on_dismiss:
        app.save_color_theme()
    canvas:
        Color:
            rgb: app.theme_cls.primary_color
        Rectangle:
            size: self.width, dp(60)
            pos: root.pos[0], root.pos[1] + root.height-dp(60)
        Color:
            rgb: app.theme_cls.bg_normal
        Rectangle:
            size: self.width, dp(290)
            pos: root.pos[0], root.pos[1] + root.height-(dp(120)+dp(230))


    #MDFlatButton:
    #    pos: root.pos[0]+root.size[0]-self.width-dp(10), root.pos[1] + dp(15)
    #    text: "Close"
    #    on_release: root.dismiss()

    MDLabel:
        font_style: "H5"
        text: "Select a theme"
        size_hint: (None, None)
        size: dp(160), dp(50)
        pos_hint: {'center_x': .5, 'center_y': .9}
        theme_text_color: 'Custom'
        text_color: root.specific_text_color
    BoxLayout:
        spacing: dp(14)
        size_hint: (None, None)
        size: root.width, 5 * dp(40) + 4 * dp(14) # 5 rows of colors
        pos: root.pos[0] + dp(12), root.pos[1] + (root.size[1] - dp(60) - self.size[1])/2.0# + root.height-(dp(120)+dp(220))
        orientation: 'vertical'
        BoxLayout:
            size_hint: (None, None)
            pos_hint: {'center_x': .5, 'center_y': .5}
            size: root.width - dp(14)*2, dp(40)
            pos: self.pos
            halign: 'center'
            orientation: 'horizontal'

            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'Red'
            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'Pink'
            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'Purple'
            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'DeepPurple'

        BoxLayout:
            size_hint: (None, None)
            pos_hint: {'center_x': .5, 'center_y': .5}
            size: root.width - dp(14)*2, dp(40)
            pos: self.pos
            halign: 'center'
            orientation: 'horizontal'

            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'Indigo'
            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'Blue'
            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'LightBlue'
            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'Cyan'

        BoxLayout:
            size_hint: (None, None)
            pos_hint: {'center_x': .5, 'center_y': .5}
            size: root.width - dp(14)*2, dp(40)
            pos: self.pos
            halign: 'center'
            orientation: 'horizontal'
            padding: 0, 0, 0, dp(1)

            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'Teal'
            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'Green'
            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'LightGreen'
            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'Lime'

        BoxLayout:
            size_hint: (None, None)
            pos_hint: {'center_x': .5, 'center_y': .5}
            size: root.width - dp(14)*2, dp(40)
            pos: self.pos
            orientation: 'horizontal'
            halign: 'center'
            padding: 0, 0, 0, dp(1)

            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'Yellow'
            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'Amber'
            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'Orange'
            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'DeepOrange'

        BoxLayout:
            size_hint: (None, None)
            pos_hint: {'center_x': .5, 'center_y': .5}
            size: root.width - dp(14)*2, dp(40)
            #pos: self.pos
            orientation: 'horizontal'
            padding: 0, 0, 0, dp(1)

            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'Brown'
            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'Gray'
            BoxLayout:
                PrimaryColorSelector:
                    color_name: 'BlueGray'
            BoxLayout:
''')


class ColorSelector(MDIconButton):
    color_name = OptionProperty('Indigo', options=palette)

    def rgb_hex(self, col):
        return get_color_from_hex(colors[col][self.theme_cls.accent_hue])


class MDThemePicker(ThemableBehavior, FloatLayout, ModalView,
                    SpecificBackgroundColorBehavior,
                    RectangularElevationBehavior):
    pass


if __name__ == "__main__":
    from kivy.app import App
    from kivymd.theming import ThemeManager


    class ThemePickerApp(App):
        theme_cls = ThemeManager()

        def build(self):
            main_widget = Builder.load_string('''
#:import MDRaisedButton kivymd.button.MDRaisedButton
#:import MDThemePicker kivymd.pickers.MDThemePicker


FloatLayout:
    MDRaisedButton:
        size_hint: None, None
        pos_hint: {'center_x': .5, 'center_y': .5}
        size: 3 * dp(48), dp(48)
        center_x: self.parent.center_x
        text: 'Open theme picker'
        on_release: MDThemePicker().open()
        opposite_colors: True
''')
            return main_widget

    ThemePickerApp().run()

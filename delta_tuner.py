from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.modules import inspector
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from kivy.clock import Clock
from kivy.graphics import *
from kivy.core.text import Label as CoreLabel
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner, SpinnerOption
import colorsys
import serial
import serial.tools.list_ports
import printer

Window.size = (700, 420)

COL_BG = (43/255, 43/255, 43/255, 1)
COL_FG = (60/255, 63/255, 65/255, 1)
COL_GN_MARKER_HSLA = (86/255, 1, 63/255, 1)
COL_HEADER = (78/255, 80/255, 141/255, 1)
COL_DATA = (141/255, 78/255, 78/255, 1)


class DeltaTunerMain(BoxLayout):
    err_bars = ObjectProperty(None)
    com_port = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        Clock.schedule_once(self.initialize, 0.01)

        self.current_port = None
        self.com_port.app = self


    def initialize(self, dt):
        # self.err_bars.add_point(0, 90)
        # self.err_bars.add_point(0, 40)
        # self.err_bars.add_point(1, 90)
        # self.err_bars.add_point(2, 90)
        # self.err_bars.add_point(60)
        # self.err_bars.add_point(30)
        # self.err_bars.add_point(10)
        # self.err_bars.add_point(5)
        pass

    def open_com_port(self, port):
        if self.current_port != port:
            self.current_port = port
            self.ptr = printer.Printer(self.current_port)


class ComPortDropDown(BoxLayout):

    dropdown = ObjectProperty()
    btn = ObjectProperty()

    def drop_down_open(self):
        self.refresh_port_list()
        self.dropdown.open(self.btn)

    def on_dropdown_select(self, data):
        self.app.open_com_port(data)
        self.btn.background_color = (0, 1, 0, 1)
        self.btn.text = data
        self.dropdown.select(data)

    def refresh_port_list(self):
        self.dropdown.clear_widgets()
        new_list = self.get_available_ports()
        for port in new_list:
            btn = Button(text=port[0], size_hint_y=None, height=44)
            if 'Open' in port[-1]:
                btn.background_color = (0.7, 0, 0, 1)
            else:
                btn.background_color = (0, 0.7, 0, 1)
            if port[0] == self.app.current_port:
                btn.background_color = (0, 0, 0.7, 1)
            btn.bind(on_release=lambda btn: self.on_dropdown_select(btn.text))
            self.dropdown.add_widget(btn)

    def get_available_ports(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        ports = [list(port) + ['Open'] for port in list(serial.tools.list_ports.comports())]

        for port in ports:
            try:
                s = serial.Serial(port[0])
                s.close()
                port[-1] = 'Closed'
            except (OSError, serial.SerialException):
                pass
        return ports


class ColoredSpinnerOption(SpinnerOption):
    def __init__(self, *args, **kwargs):
        text, col = kwargs.get('text', ('', (0, 0, 0, 1)))
        kwargs['text'] = text
        super().__init__(*args, **kwargs)
        self.background_color = col


class ComPortSpinner(Spinner):
    option_cls = ObjectProperty(ColoredSpinnerOption)

    def drop_down_open(self):
        self.refresh_port_list()

    def on_dropdown_select(self):
        data = self.text
        try:
            self.app.open_com_port(data)
        except serial.serialutil.SerialException:
            self.text = "select other"

    def refresh_port_list(self):
        self.values = []
        new_list = self.get_available_ports()
        for port in new_list:
            if 'Open' in port[-1]:
                color = (0.7, 0, 0, 1)
            else:
                color = (0, 0.7, 0, 1)
            if port[0] == self.app.current_port:
                color = (0, 0, 0.7, 1)

            self.values.append((port[0], color))

    def get_available_ports(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        ports = [list(port) + ['Open'] for port in list(serial.tools.list_ports.comports())]

        for port in ports:
            try:
                s = serial.Serial(port[0])
                s.close()
                port[-1] = 'Closed'
            except (OSError, serial.SerialException):
                pass
        return ports

class DTErrors(BoxLayout):
    e0 = ObjectProperty(None)
    e1 = ObjectProperty(None)
    e2 = ObjectProperty(None)
    e3 = ObjectProperty(None)
    e4 = ObjectProperty(None)
    e5 = ObjectProperty(None)
    e6 = ObjectProperty(None)
    e7 = ObjectProperty(None)

    def add_point(self, bar_num, value):
        try:
            e = [self.e0, self.e1, self.e2, self.e3, self.e4, self.e5, self.e6, self.e7]
        except IndexError:
            return
        targ_e = e[bar_num]
        targ_e.add_point(value)


class DTErrorVertAxis(RelativeLayout):
    mark_length = NumericProperty(8)
    total_axis_space = NumericProperty(300)
    space_btw_marks = NumericProperty(10)
    fwidth = NumericProperty(20)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bind(height=self.on_resize)
        self.redraw()

    def redraw(self):
        self.canvas.clear()
        with self.canvas:
            Color(*COL_FG)
            total_ticks = int(self.total_axis_space/self.space_btw_marks)
            for i in range(total_ticks):
                if i % 5 == 0:
                    # Long Mark
                    mark = self.mark_length
                else:
                    # Short Mark
                    mark = self.mark_length / 2
                Line(points=[self.fwidth - mark, i * self.space_btw_marks,
                             self.fwidth, i * self.space_btw_marks,
                             self.fwidth, (i + 1) * self.space_btw_marks])
            i = int(self.total_axis_space/self.space_btw_marks)
            Line(points=[self.fwidth - self.mark_length, i * self.space_btw_marks,
                         self.fwidth, i * self.space_btw_marks])

            for i in range(int(total_ticks / 5) + 1):
                label = CoreLabel()
                label.text = "{:.1f}".format(0.1 * i)
                label.refresh()
                label_texture = label.texture
                texture_size = list(label_texture.size)
                Rectangle(texture=label_texture,
                          size=[s * 0.9 for s in texture_size],
                          pos=(0, i * 5 *self.space_btw_marks - 2))

    def on_resize(self, width, height):
        self.mark_length = 8
        self.total_axis_space = float(self.height)
        self.space_btw_marks = float(self.total_axis_space) / 30.0
        self.fwidth = 20
        self.redraw()


class DTErrorBar(RelativeLayout):
    highlight_start = NumericProperty(0)
    highlight_end = NumericProperty(0)
    highlight_color = ListProperty([1, 1, 1])

    HIGHLIGHT_COLOR_GOOD = [86 / 255, 1, 63 / 255, 1]   # HSL values
    HIGHLIGHT_COLOR_BAD = [0 / 255, 1, 63 / 255, 1]     # HSL values

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.points = []

    def add_point(self, value):
        self.points.append(value)
        self.add_widget(DTErrorMarker(value))

        if len(self.points) > 1:
            # Change highlight line dimensions
            cur = self.children[0]
            prev = self.children[1]
            self.highlight_end = cur.value + cur.radius
            self.highlight_start = prev.value + prev.radius

            # Calculate highlight line color
            delta = cur.value - prev.value
            thres = 75

            if delta < 0:
                # Good
                tmp_hsl_color = self.HIGHLIGHT_COLOR_GOOD
                tmp_hsl_color[1] = -delta/thres
            else:
                # Bad
                tmp_hsl_color = self.HIGHLIGHT_COLOR_BAD
                tmp_hsl_color[1] = delta / thres

            if tmp_hsl_color[1] > 255:
                tmp_hsl_color[1] = 255
            self.highlight_color = colorsys.hls_to_rgb(tmp_hsl_color[0],
                                                        tmp_hsl_color[2],
                                                        tmp_hsl_color[1])

        # Calculate Marker colors
        base_col = list(COL_GN_MARKER_HSLA)
        base_col[1], base_col[2] = base_col[2], base_col[1]
        base_col = base_col[0:3]
        for marker in self.children[:3]:
            marker.ball_color = colorsys.hls_to_rgb(*base_col)
            base_col[2] /= 3


class DTErrorMarker(RelativeLayout):
    value = NumericProperty(0)
    radius = NumericProperty(8)
    ball_color = ListProperty(COL_FG)

    def __init__(self, value=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = value


class DeltaTunerApp(App):
    # icon = 'custom-kivy-icon.png'
    title = "Delta Tuner"

    def build(self):
        dt = DeltaTunerMain()
        inspector.create_inspector(Window, dt)
        return dt

if __name__ == "__main__":
    DeltaTunerApp().run()

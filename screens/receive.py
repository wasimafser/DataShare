from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import StringProperty

import socket

Builder.load_string("""
<ReceiveScreen>:
    id: receive_screen
    name: 'receive_screen'
    BoxLayout:
        MDLabel:
            text: root.ip
""")

class ReceiveScreen(Screen):
    ip = StringProperty("")

    def __init__(self, *args, **kwargs):
        super(ReceiveScreen, self).__init__(*args, **kwargs)

        self.ip = socket.gethostbyname(socket.gethostname())

        if self.ip.startswith("127.") or self.ip.startswith("0."):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self.ip = s.getsockname()[0]
            s.close()

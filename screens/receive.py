from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import StringProperty

import socket
import threading
import pathlib

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

    def on_enter(self):
        thread = threading.Thread(target=self.receive_file, args=(), daemon=True)
        thread.start()

    def receive_file(self, *args):
        port = 5001
        buffer_size = 1024

        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", port))
        s.listen(5)

        client_socket, client_address = s.accept()
        print("Connected")

        file_name = client_socket.recv(buffer_size).decode('utf-8')
        print(file_name)

        pathlib.Path("received").mkdir(exist_ok=True)

        with open(f"received/{file_name}", 'wb') as file:
            packet = client_socket.recv(buffer_size)
            while len(packet) != 0:
                file.write(packet)
                packet = client_socket.recv(buffer_size)

        s.close()

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import StringProperty

import socket
import threading
import pathlib
import plyer
from struct import unpack

Builder.load_string("""
<ReceiveScreen>:
    id: receive_screen
    name: 'receive_screen'
    BoxLayout:
        MDLabel:
            text: root.ip
            font_style: 'H3'
            halign: 'center'
""")

class Receiver:
    address = '0.0.0.0'
    port = 5001

    socket = None

    def listen(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.address, self.port))
        self.socket.listen(5)
        return self.socket.accept()[0]

    def close(self):
        self.socket.close()

    def convert_int(self, integer):
        return unpack('!Q', integer)[0]


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
        self.receiver = Receiver()
        self.socket = self.receiver.listen()

        downloads_path = ""
        try:
            downloads_path = plyer.storagepath.get_downloads_dir().replace("file://", '')
        except Exception as e:
            pass

        pathlib.Path(f"{downloads_path}/DataShare").mkdir(exist_ok=True)

        # RECEIVE NUMBER OF FILES
        num_of_files = self.receiver.convert_int(self.socket.recv(8))

        for i in range(num_of_files):

            # RECEIVE FILE NAME SIZE
            file_name_size = self.receiver.convert_int(self.socket.recv(8))
            # RECEIVE FILE NAME
            file_name = self.socket.recv(file_name_size).decode('utf-8')

            # RECEIVE FILE SIZE
            file_size = self.receiver.convert_int(self.socket.recv(8))

            # RECEIVE FILE
            buffer_size = 4096
            recv_size = 0
            with open(f"{downloads_path}/DataShare/{file_name}", 'wb') as file:
                while True:
                    if file_size < buffer_size:
                        buffer_size = file_size
                    packet = self.socket.recv(buffer_size)
                    file.write(packet)
                    recv_size += buffer_size

                    delta = file_size - recv_size
                    buffer_size = delta if delta < buffer_size else buffer_size

                    if recv_size == file_size or buffer_size == 0:
                        break

            print(f"RECEIVED FILE {i+1}")

        print("RECEIVED ALL")
        self.receiver.close()

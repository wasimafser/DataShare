from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.utils import platform

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.filemanager import MDFileManager

import socket
import pathlib
from struct import pack

Builder.load_string("""
<ReceiverPropmtContent>:
    orientation: 'vertical'
    spacing: "12dp"
    size_hint_y: None
    height: "50dp"
    MDTextField:
        id: receiver_ip
        hint_text: "Receiver IP"
        helper_text: "Find the ip of the reciever in the reciever's screen"
        helper_text_mode: 'on_focus'

<SendScreen>:
    id: send_screen
    name: 'send_screen'
    MDRaisedButton:
        text: "Select File to Send"
        elevation: 10
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        on_release: root.open_filemanager()
""")


class Sender:
    address = None
    port = 5001

    socket = None

    def __init__(self, address):
        self.address = address

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.address, self.port))
        return self.socket

    def disconnect(self):
        self.socket.close()

    def convert_int(self, integer):
        return pack('!Q', integer)


class ReceiverPropmtContent(BoxLayout):
    pass


class SendScreen(Screen):
    receiver_ip = StringProperty("")

    def __init__(self, *args, **kwargs):
        super(SendScreen, self).__init__(*args, **kwargs)

        self.file_manager = MDFileManager(
            exit_manager=self.on_filemanager_exit,
            select_path=self.on_select_path,
            multiselect=True
        )

    def send_file(self, paths):

        # SEND NUMBER OF FILES
        self.socket.sendall(self.sender.convert_int(len(paths)))

        for path in paths:
            path_obj = pathlib.Path(path)
            file_name = path_obj.name
            file_size = path_obj.stat().st_size

            # SEND FILE NAME SIZE
            self.socket.sendall(self.sender.convert_int(len(file_name)))
            # SEND FILE NAME
            self.socket.sendall(file_name.encode('utf-8'))

            # SEND FILE SIZE
            self.socket.sendall(self.sender.convert_int(file_size))

            # SEND FILE
            with open(path, 'rb') as file:
                self.socket.sendfile(file)

            print("SENT !")

        self.sender.disconnect()

    def on_filemanager_exit(self, *args):
        self.file_manager.close()

    def on_select_path(self, paths):
        self.send_file(paths)
        self.file_manager.close()

    def open_filemanager(self, *args):
        path = "/"
        if platform == 'android':
            path = '/storage/emulated/0/'
        self.file_manager.show(path)

    def set_receiver_ip(self, value):
        self.receiver_ip = value

        # CONNECT TO RECEIVER
        self.sender = Sender(self.receiver_ip)
        self.socket = self.sender.connect()

        self.receiver_prompt.dismiss()

    def on_enter(self):
        self.receiver_prompt = MDDialog(
            title="Enter Receiver IP",
            type="custom",
            auto_dismiss=False,
            content_cls=ReceiverPropmtContent(),
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.set_receiver_ip(
                        self.receiver_prompt.content_cls.ids.receiver_ip.text
                    )
                )
            ]
        )
        self.receiver_prompt.open()

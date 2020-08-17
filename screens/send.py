from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.filemanager import MDFileManager

import socket
import pathlib

Builder.load_string("""
<ReceiverPropmtContent>:
    orientation: 'vertical'
    MDTextField:
        id: receiver_ip
        hint_text: "Receiver IP"
        helper_text: "Find the ip of the reciever in the reciever's screen"
        helper_text_mode: 'on_focus'

<SendScreen>:
    id: send_screen
    name: 'send_screen'
    MDFlatButton:
        text: "Select File to Send"
        on_release: root.open_filemanager()
""")

class ReceiverPropmtContent(BoxLayout):
    pass

class SendScreen(Screen):
    receiver_ip = StringProperty("")

    def __init__(self, *args, **kwargs):
        super(SendScreen, self).__init__(*args, **kwargs)

        self.file_manager = MDFileManager(
            exit_manager=self.on_filemanager_exit,
            select_path=self.on_select_path,
        )

    def send_file(self, path):
        port = 5001
        buffer_size = 1024

        s = socket.socket()
        s.connect((self.receiver_ip, port))
        print("connected")

        file_name = pathlib.Path(path).name
        s.send(file_name.encode('utf-8'))

        with open(path, 'rb') as file:
            packet = file.read(buffer_size)
            while len(packet) != 0:
                s.send(packet)
                packet = file.read(buffer_size)

        s.close()

    def on_filemanager_exit(self, *args):
        self.file_manager.close()

    def on_select_path(self, path):
        self.send_file(path)
        self.file_manager.close()

    def open_filemanager(self, *args):
        path = "/"
        self.file_manager.show(path)

    def set_receiver_ip(self, value):
        self.receiver_ip = value
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

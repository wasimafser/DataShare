from kivymd.app import MDApp

from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, Permission

from screens.send import SendScreen
from screens.receive import ReceiveScreen

class MainScreen(Screen):

    def on_enter(self):
        if platform == 'android':
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

class MainApp(MDApp):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen())
        self.sm.add_widget(SendScreen())
        self.sm.add_widget(ReceiveScreen())
        return self.sm

if __name__ == '__main__':
    MainApp().run()

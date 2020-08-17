from kivymd.app import MDApp

from kivy.uix.screenmanager import Screen, ScreenManager

from screens.send import SendScreen
from screens.receive import ReceiveScreen

class MainScreen(Screen):
    pass

class MainApp(MDApp):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen())
        self.sm.add_widget(SendScreen())
        self.sm.add_widget(ReceiveScreen())
        return self.sm

if __name__ == '__main__':
    MainApp().run()

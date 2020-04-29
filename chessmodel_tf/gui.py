from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

class MainScreen(GridLayout):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.cols = 2
        self.add_widget(Label(text='user name'))
        self.username = TextInput(multiline=False)
        self.add_widget(self.username)
        self.add_widget(Label(text='password'))
        self.password=TextInput(password=True,multiline=False)
        self.add_widget(self.password)


class MyApp(App):
#    def __init__(self):
#        super(MyApp, self).__init__()


    def build(self):
        return MainScreen()


if __name__ == '__main__':
    MyApp().run()
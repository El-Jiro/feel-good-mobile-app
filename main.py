from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

#Invocamos al método load_file del objeto Builder y le pasamos el nombre del archivo kv en forma de string
Builder.load_file("design.kv")

#Creamos una clase vacía con el mismo nombre de nuestra pantalla, esta clase debe heredar de Screen:
class LoginScreen(Screen):
    pass

#Creamos otra con el nombre RootWidget que herede de ScreenManager
class RootWidget(ScreenManager):
    pass

#Y ahora una última llamada MainApp que herede de App, esta tendrá un único método llamado build que es heredado de su clase padre,
#recibirá self como parámetro y devolverá una instancia de RootWidget
class MainApp(App):
    def build(self):
        return RootWidget()

#Si estamos ejecutando el código desde este mismo archivo y no como import en otro script, creamos una instancia anónima de MainApp
#y llamamos a su método run

if __name__ == "__main__":
    MainApp().run()

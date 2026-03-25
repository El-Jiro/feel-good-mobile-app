from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from typing import Self
from datetime import datetime
import json

#Invocamos al método load_file del objeto Builder y le pasamos el nombre del archivo kv en forma de string
Builder.load_file("design.kv")

#Creamos una clase vacía con el mismo nombre de nuestra pantalla, esta clase debe heredar de Screen:
class LoginScreen(Screen):
    
    def sign_up(self: Self):
        #llamamos self.manager.current y le asignamos el nombre de la pantalla a la que queramos navegar
        self.manager.current = "sign_up_screen"

#Debemos repetir el procedimiento con cada pantalla de nuestra app, de lo contrario el parser de Kivy no
#reconocerá la clase y obtendremos un error en tiempo de ejecución
class SignUpScreen(Screen):
    
    def login(self: Self):
        self.manager.current = "login_screen"

    def add_user(self: Self, username: str, password: str) -> None:
        #Abrimos el archivo usnado with, esto es un context manager que se encargará de cerrar el archivo automáticamente
        #al salir del bloque aunque haya habido un error en tiempo de ejecución
        with open("users.json") as file:
            #Cargamos el archivo y lo asignamos a la variable users, esto es como un diccionario gigante compuesto de otros
            #diccionarios pequeños
            users = json.load(file)

        #Creamos una clave para el diccionario users, la cual será el nombre del usuario, y como valores 
        #tendrá la contraseña y un timestamp del momento en el que fue creado
        users[username] = {"password": password, "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        
        #Abrimos el archivo users.json de nuevo pero ahora en modo de escritura y guardamos los cambios
        with open("users.json", "w") as file:
            json.dump(users, file)

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

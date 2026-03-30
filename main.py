from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import StringProperty
from typing import Self
from datetime import datetime
import json
import re

#Patrón para evaluar la contraseña:
pattern = r"^(?=.*\d).{8,}$"

#Invocamos al método load_file del objeto Builder y le pasamos el nombre del archivo kv en forma de string
Builder.load_file("design.kv")

#Creamos una clase vacía con el mismo nombre de nuestra pantalla, esta clase debe heredar de Screen:
class LoginScreen(Screen):
    
    def sign_up(self: Self) -> None:
        #llamamos self.manager.current y le asignamos el nombre de la pantalla a la que queramos navegar
        self.manager.current = "sign_up_screen"
    
    #Creamos el método login para procesar las credenciales del usuario
    def login(self: Self, username: str, password: str) -> None:
        #Leemos el archivo y cargamos sus datos en users 
        with open("users.json") as file:
            users: dict[str, dict] = json.load(file)

        if username == "" or password == "":
            self.ids.wrong_login.text = "You must provide an username and password"

        elif not username in users:
            self.ids.wrong_login.text = "Username is invalid or non-existent"
        
        elif not users.get(username, {}).get("password", {}) == password:
            self.ids.wrong_login.text = "Invalid password"
            
        else:
            popup = Popup(
                title='Success!',
                content= Label(text="You've succesfully logged in!"),
                size_hint=(None, None),
                size=(300, 200)
                )
            
            popup.open()

            main = self.manager.get_screen("main_screen")
            main.user = username

            self.manager.transition.direction = "left"
            self.manager.current = "main_screen"


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

        if len(username) < 3:
            popup = Popup(
                title='Invalid username',
                content=Label(text='Username must be at least 3 characters long'),
                size_hint=(None, None),
                size=(400, 200)
                )
            
            popup.open()

        elif not re.match(pattern, password) :

            popup = Popup(
                title='Invalid password',
                content=Label(text='Password must be at least 8 characters long \nand must also contain a number'),
                size_hint=(None, None),
                size=(500, 200)
                )
            
            popup.open()
        elif username in users:
            popup = Popup(
                title='Invalid username',
                content=Label(text='User already exists'),
                size_hint=(None, None),
                size=(300, 200)
                )

            popup.open()

        else:
            #Creamos un nuevo par clave-valor dentro de users, la clave será el nombre de usuario y el valor será
            #otro diccionario que contendrá la contraseña y un timestamp con la fecha y hora en la cual se creó el usuario
            users[username] = {"password": password, "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            #Abrimos el archivo users.json de nuevo pero ahora en modo de escritura y guardamos los cambios
            with open("users.json", "w") as file:
                json.dump(users, file)
            
            popup = Popup(
                title='Success!',
                content=Label(text='New user succesfully registered!'),
                size_hint=(None, None),
                size=(300, 200)
                )
            
            popup.open()

            self.login()

class MainScreen(Screen):

    user: StringProperty = StringProperty("")

    def logout(self: Self):
        #Usamos self.transtion.direction para añadir una animación de transición, en este caso un desplazamiento
        #hacia la derecha
        self.manager.transition.direction = "right"
        self.manager.current = "login_screen"

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

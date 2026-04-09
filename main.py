from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.storage.jsonstore import JsonStore
from typing import Self
from datetime import datetime
from pathlib import Path
import json, glob, re, random

#Patrón para evaluar la contraseña:
pattern = r"^(?=.*\d).{8,}$"

#Invocamos al método load_file del objeto Builder y le pasamos el nombre del archivo kv en forma de string
Builder.load_file("design.kv")

#Creamos una clase vacía con el mismo nombre de nuestra pantalla, esta clase debe heredar de Screen:
class LoginScreen(Screen):
    
    def on_pre_enter(self, *args):
        Clock.schedule_once(self._init_ui, 0)
    
    def _init_ui(self, dt):

        self.ids.user.text = ""
        self.ids.pswd.text = ""
        self.ids.keep_session.active = False
        self.ids.wrong_login.text = ""

    def go_to_sign_up(self: Self) -> None:
        #llamamos self.manager.current y le asignamos el nombre de la pantalla a la que queramos navegar
        self.manager.transition.direction = "right"
        self.manager.current = "sign_up_screen"

    def go_to_forgot_password(self: Self) -> None:
        self.manager.current = "forgot_password_screen"
    
    #Creamos el método login para procesar las credenciales del usuario
    def login(self: Self, username: str, password: str) -> None:
        #Leemos el archivo y cargamos sus datos en users 
        with open("users.json") as file:
            users: dict[str, dict] = json.load(file)

        if username == "" or password == "":
            self.ids.wrong_login.text = "Debes proporcionar un usuario y una contraseña"

        elif not username in users:
            self.ids.wrong_login.text = "El usuario es inválido o no existe"
        
        elif not users.get(username, {}).get("password", {}) == password:
            self.ids.wrong_login.text = "Contraseña inválida"

        else:
            popup = Popup(
                title='¡Éxito!',
                content= Label(text="¡Se ha inciado sesión con éxito!"),
                size_hint=(None, None),
                size=(300, 200)
                )
            
            popup.open()

            
            username = self.ids.user.text
            remember = self.ids.keep_session.active

            main = self.manager.get_screen("main_screen")
            print(username)
            main.user = username

            #Creamos una instancia de app
            app = App.get_running_app()

            if remember:
                app.store.put("user", name= username)

            self.manager.transition.direction = "left"
            self.manager.current = "main_screen"

#Debemos repetir el procedimiento con cada pantalla de nuestra app, de lo contrario el parser de Kivy no
#reconocerá la clase y obtendremos un error en tiempo de ejecución
class SignUpScreen(Screen):

    def on_pre_enter(self, *args):
        Clock.schedule_once(self._init_ui, 0)
    
    def _init_ui(self, dt):

        self.ids.user.text = ""
        self.ids.pswd.text = ""
        self.ids.wrong_signup.text = ""
    
    
    def login(self: Self):
        self.manager.current = "login_screen"

    def add_user(self: Self, username: str, password: str) -> None:
        #Abrimos el archivo usnado with, esto es un context manager que se encargará de cerrar el archivo automáticamente
        #al salir del bloque aunque haya habido un error en tiempo de ejecución
        with open("users.json") as file:
            #Cargamos el archivo y lo asignamos a la variable users, esto es como un diccionario gigante compuesto de otros
            #diccionarios pequeños
            users = json.load(file)

        if username == "" or password == "":
            self.ids.wrong_signup.text = "Debes proporcionar un usuario y una contraseña"

        elif len(username) < 3:
            self.ids.wrong_signup.text = "El usuario debe tener al menos 3 caracteres de longitud"

        elif not re.match(pattern, password) :
            self.ids.wrong_signup.text = "La contraseña debe tener al menos 8 caracteres \nde longitud y también debe incluir un número"

        elif username in users:
            self.ids.wrong_signup.text = "El usuario ya existe"
        
        else:
            #Creamos un nuevo par clave-valor dentro de users, la clave será el nombre de usuario y el valor será
            #otro diccionario que contendrá la contraseña y un timestamp con la fecha y hora en la cual se creó el usuario
            users[username] = {"password": password, "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            #Abrimos el archivo users.json de nuevo pero ahora en modo de escritura y guardamos los cambios
            with open("users.json", "w") as file:
                json.dump(users, file)
            
            popup = Popup(
                title='¡Éxito!',
                content=Label(text='¡Se ha registrado exitosamente el usuario!'),
                size_hint=(None, None),
                size=(400, 200)
                )
            
            popup.open()

            self.login()

class MainScreen(Screen):

    user: StringProperty = StringProperty("")

    def logout(self: Self):

        app = App.get_running_app()

        if app.store.exists("user"):
            app.store.delete("user")
        #Usamos self.transtion.direction para añadir una animación de transición, en este caso un 
        #desplazamiento hacia la derecha
        self.manager.transition.direction = "right"
        self.manager.current = "login_screen"

    #Creamos un método para obtener la emoción introducida por el usuario y mostrar una cita acorde:
    def get_quote(self: Self, feel: str):
        #Ponemos todo el input en mínusculas para que no haya problemas al compararlo con los nombres de los archivos
        feel = feel.lower()
        #Obtenemos las rutas de todos los archivos que se encuentren dentro de la carpeta quotes
        avlb_feelings: list[str] = glob.glob("quotes/*")
        #Ahora obtenemos sólo los nombres de archivo en sí sin todas las carpetas ni la extensión 
        #mediante Path().stem y la comprensión de listas
        avlb_feelings = [Path(file).stem for file in avlb_feelings]

        #Si la emoción introducida está en la lista de las emociones disponibles, abrimos su archivo .txt correspondiente:
        if feel in avlb_feelings:
            with open(f"quotes/{feel}.txt", encoding="utf8") as file:
                #obtenemos las citas con readlines()
                quotes: list[str] = file.readlines()
                #mostramos una cita de la lista al azar en nuestro label mediante random.choice
                self.ids.quote.text = random.choice(quotes)
        else: 
            #De lo contrario enviamos un mensaje diciendo al usuario que intente con una emoción distinta
            self.ids.quote.text = "Prueba con otra emoción"
            self.ids.quote.color = "yellow"

class ForgotPasswordScreen(Screen):

    def on_pre_enter(self, *args):
        Clock.schedule_once(self._init_ui, 0)

    def _init_ui(self: Self, dt: int) -> None:

        self.ids.user.text = ""
        self.ids.pswd.text = ""
        self.ids.error_msg.text = ""
    
    def go_to_login(self: Self) -> None:

        self.manager.transition.direction = "right"
        self.manager.current = "login_screen"

    def reset_password(self: Self, username: str, password: str) -> None:

        #Cargamos el archivo de users.json y guardamos sus datos en la variable homónima
        with open("users.json") as file:
            users: dict[str, dict] = json.load(file)
        
        #Comprobamos que ambos campos estén llenos, si están vacíos enviamos un mensaje de error
        if username == "" or password == "":
            self.ids.error_msg.text = "Debes proporcionar un nombre \nde usuario y una contraseña"
        else:
            #Comprobamos que el usuario exista
            if not username in users:
                self.ids.error_msg.text = "El usuario es inválido o no existe"
            else:
                #Cuando hayamos validado el usuario, comprobamos que la nueva contraseña cumpla con el formato requrido y que sea
                #distinta de la actual
                if not re.match(pattern, password):
                    self.ids.error_msg.text = "La contraseña debe tener al menos 8 caracteres \nde longitud y también debe incluir un número"
                elif users.get(username, {}).get("password",{}) == password:
                    self.ids.error_msg.text = "La contraseña nueva debe ser distinta de la actual"
                else:
                    #actualizamos la contraseña en users
                    users.get(username, {})["password"] = password

                    #Sobreescribimos el archivo json
                    with open("users.json", "w") as file:
                        json.dump(users, file)

                    #Mandamos un popup con un mensaje de éxito
                    popup = Popup(
                        title='Contraseña actualizada',
                        content= Label(text="¡Se ha actualizado la \ncontraseña con éxito!"),
                        size_hint=(None, None),
                        size=(400, 200)
                    )
                    
                    popup.open()

                    #Volvemos a la pantalla de login
                    self.manager.transition.direction= "left"
                    self.manager.current = "login_screen"

#Creamos otra con el nombre RootWidget que herede de ScreenManager
class RootWidget(ScreenManager):
    pass

#Y ahora una última llamada MainApp que herede de App, esta tendrá un único método llamado build que es heredado de su clase padre,
#recibirá self como parámetro y devolverá una instancia de RootWidget
class MainApp(App):
    def build(self: Self):
        self.sm = RootWidget()

        #Creamos un archivo JSON que almacene la sesión mediante JsonStore y lo guardamos en el atributo store de la classe
        self.store = JsonStore("session.json")

        #Si el archivo existe y tiene la clave user, obtenemos el nombre de usuario
        if self.store.exists("user"):
            username = self.store.get("user")["name"]
            #Hacemos referencia a la pantalla principal y le pasamos dicho nombre
            main = self.sm.get_screen("main_screen")
            main.user = username
            self.sm.current= "main_screen"

        return self.sm

#Si estamos ejecutando el código desde este mismo archivo y no como import en otro script, creamos una instancia anónima de MainApp
#y llamamos a su método run
if __name__ == "__main__":
    MainApp().run()

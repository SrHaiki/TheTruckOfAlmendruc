from os import system, name, walk, _exit, getcwd, chdir
from libs.server_config import ServerConfig
from libs.personal_prompt import PersonalPrompt
from libs.server_manage import ServerManage

class CommandParser:

    def __init__(self, global_vars_instance):
        self.commands = {
            "clear": self._clearscreen,
            "server": self._server,
            "exit": self._exit,
            "help": self._help,
        }

        self.server_func = ServerConfig()
        self.personal_prompt = PersonalPrompt()
        self.server_manage = ServerManage(global_vars_instance)

    def _server(self, param):
        param_process = ' '.join(param)

        if param_process == "config":
            self.server_func.server_config()
        elif param_process == "newconfig":
            self.server_func.server_newconfig()
        elif param_process == "start":
                self.personal_prompt.prompt_change_status("server")

                get_ip = self.server_func.get_ip()
                get_port = self.server_func.get_port()

                self.server_manage.server_start(get_ip, get_port)
                print("\033[34m[INFO]\033[0m Cerrando el \033[31mservidor\033[0m ...")
                print("\033[34m[INFO]\033[0m Completado.")
        else:
            print("\033[31m[ERROR]\033[0m Comando desconocido o mal utilizado, porfavor lea la informacion con help server .")

    def parser(self, lowly_command):
        if not lowly_command:
            return
        
        low_command = lowly_command.split()
        if len(low_command) >= 2:
            try:
                self.commands.get(low_command[0])(low_command[1:])
            except Exception as e:
                print(e)
                print("\033[31m[ERROR]\033[0m Comando desconocido o mal utilizado, porfavor lea la informacion con help .")
                pass
        else:
            try:
                self.commands.get(low_command[0])()
            except Exception as e:
                print(e)
                print("\033[31m[ERROR]\033[0m Comando desconocido o mal utilizado, porfavor lea la informacion con help .")
                pass
    
    def _clearscreen(self):
        system('clear')
        return

    def _exit(self):
        print("\n\n\033[0mLowly force close (CRTL^C)")
        exit()

    def _help(self):
        return print("""

        \033[0mINFORMACION DE COMANDOS:
        \033[31m========================\033[0m
        \033[34m- help | Show command information.
        - exit | Close app ( Lowly )
        - clear | Clear screen

        \033[0m""")
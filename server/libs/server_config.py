from os import system, name, walk, _exit, getcwd, chdir
from configparser import ConfigParser

class ServerConfig:

    ip_Get = None
    port_Get = None

    def __init__(self):
        self.configparser = ConfigParser()
        pass

    def get_ip(self):
        self.get_data()
        return self.ip_Get
    
    def get_port(self):
        self.get_data()
        return self.port_Get

    def get_data(self):
        self.configparser.read('data/data_server.cfg')

        self.ip_Get = self.configparser.get('SERVER', 'ip')
        self.port_Get = self.configparser.get('SERVER', 'port')

        return self.ip_Get, self.port_Get

    def server_newconfig(self):
        print("\033[34m[INFO]\033[0m Introduce tu direccion IPv4 (Publica o Privada) para el servidor")
        new_ip = input("\033[0m[ \033[31mIP\033[0m > ")
        print("\033[34m[INFO]\033[0m Introduce un numero de 4 cifras para asignarle al puerto (Ej: 4444)")
        new_port = input("\033[0m[ \033[31mPORT\033[0m > ")

        self.configparser.read('data/data_server.cfg')

        self.configparser['SERVER']['ip'] = new_ip
        self.configparser['SERVER']['port'] = new_port

        with open('data/data_server.cfg', 'w') as configfile:
               self.configparser.write(configfile)

        return  print("\033[34m[INFO]\033[0m Consulta el comando [ \033[31mserver config\033[0m ] para verificar la nueva configuracion.")


    def server_config(self):
        self.get_data()
        print("""
        \033[0m[------- \033[34mCONFIGURACION DEL SERVIDOR\033[0m -----]
        \033[31mIP\033[0m = {0}
        \033[31mPORT\033[0m = {1}
        """.format(self.ip_Get, self.port_Get))
        return
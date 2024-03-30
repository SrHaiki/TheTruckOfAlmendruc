import sys
import rsa
from colorama import init, Fore, Style
from libs.command_parser import CommandParser
from libs.personal_prompt import PersonalPrompt
from libs.banner import banner
from data.global_vars import GlobalVars
from os import system, name, walk, _exit, getcwd, chdir

class TheTrucOfAlmendruc:
    def __init__(self):
        self.global_vars = GlobalVars()
        self.command_parser = CommandParser(self.global_vars)
        self.personal_prompt = PersonalPrompt()
    
    def generate_cert(self):
        rsa_pub, rsa_priv = rsa.newkeys(1024)

        self.global_vars.set_rsa_priv(rsa_priv)

        self.global_vars.set_rsa_pub(rsa_pub)

        return

    def console(self):

        banner()

        self.generate_cert()

        while True:
            try:
                thetrucofalmendruc_input = input(self.personal_prompt.prompt())
                self.command_parser.parser(thetrucofalmendruc_input.lower())
            except KeyboardInterrupt:
                print("\n\n\033[0mLowly force close (CRTL^C)")
                print("\033[34m[INFO]\033[0m \033[32mBorrando\033[0m interfaz para ligolo y removiendo rutas...")
                system("sudo ip link del ligolo")
                if (len(self.global_vars.list_of_routes_for_ligolo) >= 1):
                    for ip_range in self.global_vars.list_of_routes_for_ligolo:
                        system("sudo ip route del {0} dev ligolo".format(ip_range))
                else:
                    pass
                print("\033[34m[INFO]\033[0m Completado.")
                sys.exit()

if __name__ == "__main__":
    system('cls' if name=='nt' else 'clear')
    init()
    TheTrucOfAlmendruc().console()
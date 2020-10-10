import cmd2
import time
import sys
from colorama import *
from glob import glob
import random

def load_logos():

    color_map = {
    
        "%bld": Style.BRIGHT,
        "%blk": Fore.BLACK,
        "%blu": Fore.BLUE,
        "%clr": Fore.RESET + Style.NORMAL,
        "%cya": Fore.CYAN,
        "%grn": Fore.GREEN,
        "%mag": Fore.MAGENTA,
        "%red": Fore.RED,
        "%whi": Fore.WHITE,
        "%yel": Fore.YELLOW,
    }

    logos = []
    fnames = glob("data/logos/*.txt")
    for fname in fnames:
        with open(fname) as h:
            logo = h.read()
            for color in color_map.keys():
                logo = logo.replace(color, color_map[color])
        logos.append(logo)
    return logos


class App(cmd2.Cmd):

    def __init__(self):

        super().__init__()
        self.prompt = f"{cmd2.ansi.UNDERLINE_ENABLE}msf6{cmd2.ansi.UNDERLINE_DISABLE} > "
        pass

    def sigint_handler(self, signum: int, frame):
        self.async_alert(f"{self.prompt}Interrupt: use the 'exit' command to quit")


    def do_exit(self, args):
        return True


def startup():
    start = "[*] Starting the Metasploit Framework console..."
    animations = "|/-\\"
    for i in range(len(animations)*5):
        print(start[:4+i] +start[4+i].upper() + start[5+i:] + animations[i%len(animations)] + "\r",end="")
        time.sleep(0.1)

    print(" "*50+"\r\n")
    print(random.choice(load_logos()))
    print(Fore.RESET + Style.NORMAL)


startup()

app = App()
app.cmdloop()
# for logo in load_logos():
#     print(logo)
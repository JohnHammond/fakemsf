#!/usr/bin/env python

import cmd2
import time
import sys
import os
from colorama import *
from glob import glob
import random
from pprint import pprint

def load_logos():
    """
    Load and map color to the default logos that msfconsole uses
    """

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


def load_modules():
    modules = {}

    for root, dirs, files in os.walk("modules"):
        for fname in files:
            fpath = "/".join(os.path.join(root, fname).split("/")[1:])
            group = fpath.split("/")[0]
            if group not in modules:
                modules[group] = []
            if fpath.endswith(".rb"):
                modules[group].append(fpath)

    return modules


class App(cmd2.Cmd):

    def __init__(self):
        """
        Display a msfconsole prompt
        """
        super().__init__()
        self.prompt = f"{cmd2.ansi.UNDERLINE_ENABLE}msf6{cmd2.ansi.UNDERLINE_DISABLE} > "
        pass


    def perror(self, msg = '', *, end: str = '\n', apply_style: bool = True):
        """
        Display high-level error messages in a similar way that msfconsole does
        """
        default_error = "is not a recognized command, alias, or macro"
        parse_error = "No closing quotation"
        if default_error in msg:
            print(f"{Style.BRIGHT+Fore.RED}[-]{Style.NORMAL+Fore.RESET} Unknown command: {msg.split()[0]}")
        elif parse_error in msg:
            print(f"{Style.BRIGHT+Fore.RED}[-]{Style.NORMAL+Fore.RESET} Parse error: Unmatched double quote")
        else:
            sys.stderr.write(msg + end)


    def sigint_handler(self, signum: int, frame):
        """
        Handle Ctrl+C interrupts like msfconsole does
        """
        self.async_alert(f"{self.prompt}Interrupt: use the 'exit' command to quit")


    def do_exit(self, args):
        return True


def startup():
    """
    Start in a similar fashion to msfconsole
    """
    start = "[*] Starting the Metasploit Framework console..."
    animations = "|/-\\"
    for i in range(len(animations)*5):
        print(start[:4+i] +start[4+i].upper() + start[5+i:] + animations[i%len(animations)] + "\r",end="")
        time.sleep(0.1)

    print(" "*50+"\r\n")
    print(random.choice(load_logos()))
    print(Fore.RESET + Style.NORMAL)

    modules = load_modules()
    print(f"       =[ {Fore.YELLOW}metasploit v6.0.10-dev-7be36a772d{Fore.RESET}               ]")
    print(f"+ -- --=[ {len(modules['exploits'])} exploits - {len(modules['auxiliary'])} auxiliary - {len(modules['post'])} post       ]")
    print(f"+ -- --=[ {len(modules['payloads'])} payloads - {len(modules['encoders'])} encoders - {len(modules['nops'])} nops            ]")
    print(f"+ -- --=[ {len(modules['evasion'])} evasion                                       ]")
    print()
    print("Metasploit tip:")
    print()



startup()
app = App()
app.cmdloop()


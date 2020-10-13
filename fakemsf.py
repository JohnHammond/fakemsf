#!/usr/bin/env python

import cmd2
import time
import sys
import os
import shutil
import subprocess
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
            new_logo = []
            for line in logo.split("\n"):
                new_logo.append(f"{Fore.CYAN}{line}{Fore.RESET}")
            logo = "\n".join(new_logo)
        logos.append(logo)
    return logos


def load_tips():

    tips = []
    with open("data/tips.txt") as h:
        for tip in h:
            tip = tip.strip()
            tip = tip.replace("#{highlight('", Fore.GREEN)
            tip = tip.replace("')}", Fore.RESET)
            tips.append(tip)
    return tips

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


    def default(self, statement):
        """
        Handle regular shell commands appropriately
        """
        if ( shutil.which(statement.command) ):
            self.stdout.write(f"{Fore.BLUE+Style.BRIGHT}[*]{Fore.RESET+Style.NORMAL} exec: {statement.raw}\n\n")
            p = subprocess.Popen(statement.raw, stderr = subprocess.STDOUT, stdout = subprocess.PIPE, shell=True)
            self.stdout.write(p.stdout.read().decode("latin-1"))
        elif statement.command == "cd":
            try:
                if ( statement.args == "" ):
                    os.chdir(os.getenv("HOME"))
                else:
                    os.chdir(statement.args)
            except FileNotFoundError:
                self.perror(f"The specified path does not exist")
        else:
            self.perror(f"{statement.command} is not a recognized command, alias, or macro")

        return False

    def perror(self, msg = '', *, end: str = '\n', apply_style: bool = True):
        """
        Display high-level error messages in a similar way that msfconsole does
        """
        default_error = "is not a recognized command, alias, or macro"
        parse_error = "No closing quotation"

        if default_error in msg:
            sys.stderr.write(f"{Style.BRIGHT+Fore.RED}[-]{Style.NORMAL+Fore.RESET} Unknown command: {msg.split()[0]}\n")
        elif parse_error in msg:
            sys.stderr.write(f"{Style.BRIGHT+Fore.RED}[-]{Style.NORMAL+Fore.RESET} Parse error: Unmatched double quote\n")
        else:
            sys.stderr.write(f"{Style.BRIGHT+Fore.RED}[-]{Style.NORMAL+Fore.RESET} {msg}" + end)


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
    print("Metasploit tip: " + random.choice(load_tips()))
    print()



# startup()
app = App()
app.cmdloop()


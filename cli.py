#!/usr/bin/python3
from Class.cli import CLI
import sys

cli = CLI()
cert = Cert()

if len(sys.argv) == 1:
    print("init")
elif sys.argv[1] == "init":
    cli.init()

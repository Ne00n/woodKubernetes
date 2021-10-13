#!/usr/bin/python3
from Class.cli import CLI
import sys

cli = CLI()

if len(sys.argv) == 1:
    print("init, cert, machine")
elif sys.argv[1] == "init":
    cli.init()
elif sys.argv[1] == "cert":
    if len(sys.argv) == 2:
        print("cert add <domain> <email> <machine> <api>\cert list\cert del <domain>")
    elif sys.argv[2] == "add":
        cli.addCert(sys.argv[3:])
    elif sys.argv[2] == "list":
        cli.getTable("certs")
    elif sys.argv[2] == "del":
        cli.deleteCert(sys.argv[3:])
elif sys.argv[1] == "machine":
    if len(sys.argv) == 2:
        print("machine add <name> <os> <memory> <ports> <deploy>\nmachine list\nmachine del <name>")
    elif sys.argv[2] == "add":
        cli.addMachine(sys.argv[3:])
    elif sys.argv[2] == "list":
        cli.getTable("machines")
    elif sys.argv[2] == "del":
        cli.deleteMachine(sys.argv[3:])

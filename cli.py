#!/usr/bin/python3
from Class.cli import CLI
import sys

cli = CLI()

if len(sys.argv) == 1:
    print("init, machine")
elif sys.argv[1] == "init":
    cli.init()
elif sys.argv[1] == "machine":
    if len(sys.argv) == 2:
        print("machine add <name> <os> <cores> <memory> <storage> <deploy>")
        print("machine add <name> <os> <cores> <memory> <storage> <deploy> <ports>")
        print("machine add <name> <os> <cores> <memory> <storage> <deploy> <ports> <mount>")
        print("machine list")
        print("machine del <name>")
    elif sys.argv[2] == "add":
        cli.addMachine(sys.argv[3:])
    elif sys.argv[2] == "list":
        cli.getTable("machines")
    elif sys.argv[2] == "del":
        cli.deleteMachine(sys.argv[3:])

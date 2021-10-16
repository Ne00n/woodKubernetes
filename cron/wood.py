#!/usr/bin/python3
import sys
sys.path.append("..") # Adds higher directory to python modules path.

from Class.lxd import LXD

if len(sys.argv) == 1:
    print("lxd")
elif sys.argv[1] == "lxd":
    lxd = LXD()
    lxd.run()

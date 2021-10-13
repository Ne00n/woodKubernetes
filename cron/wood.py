#!/usr/bin/python3
import sys
sys.path.append("..") # Adds higher directory to python modules path.

from Class.lxd import LXD

lxd = LXD()

if len(sys.argv) == 1:
    print("lxd, cert")
elif sys.argv[1] == "lxd":
    lxd.run()

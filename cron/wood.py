#!/usr/bin/python3
import sys
sys.path.append("..") # Adds higher directory to python modules path.

from Class.lxd import LXD
from Class.cert import Cert

if len(sys.argv) == 1:
    print("lxd, cert")
elif sys.argv[1] == "lxd":
    lxd = LXD()
    lxd.run()
elif sys.argv[1] == "cert":
    cert = Cert()
    cert.renew()

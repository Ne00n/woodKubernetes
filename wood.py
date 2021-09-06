from Class.wood import Wood
import sys

print("woodKubernetes")
config = "servers.json"

if len(sys.argv) > 2:
    config = sys.argv[2]
wood = Wood(config)

if len(sys.argv) == 1:
    print("lxd")
elif sys.argv[1] == "lxd":
    wood.lxd()
elif sys.argv[1] == "rqlite":
    wood.rqlite()
elif sys.argv[1] == "wood":
    wood.wood()
elif sys.argv[1] == "service":
    wood.service()
elif sys.argv[1] == "preload":
    wood.preload()
elif sys.argv[1] == "update":
    wood.update()

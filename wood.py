from Class.wood import Wood
import sys

print("woodKubernetes")
config = "servers.json"
param = ""

if len(sys.argv) > 2:
    config = sys.argv[2]
if len(sys.argv) > 3:
    param = sys.argv[3]
wood = Wood(config)

if len(sys.argv) == 1:
    print("lxd, rqlite, wood, service, preload, update")
elif sys.argv[1] == "lxd":
    wood.lxd()
elif sys.argv[1] == "rqlite":
    wood.rqlite(param)
elif sys.argv[1] == "wood":
    wood.wood()
elif sys.argv[1] == "service":
    wood.service(param)
elif sys.argv[1] == "preload":
    wood.preload()
elif sys.argv[1] == "update":
    wood.update(param)

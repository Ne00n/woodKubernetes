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

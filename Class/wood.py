import subprocess, time, json, re

servers = {}

class Wood:
    def __init__(self,config="servers.json"):
        print("Loading",config)
        with open(config) as handle:
            self.servers = json.loads(handle.read())

    def cmd(self,server,command,interactive):
        cmd = ['ssh','root@'+server,command]
        if interactive == True:
            return subprocess.check_output(cmd).decode("utf-8")
        else:
            subprocess.run(cmd)

    def lxd(self):
        for server in self.servers:
            print(server['name'],"Installing LXD")
            self.cmd(server['ip'],'apt-get update && apt-get install snap snapd -y && snap install core && snap install lxd --channel=4.0/stable',False)

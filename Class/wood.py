from Class.templator import Templator
import subprocess, time, json, re

servers = {}

class Wood:
    def __init__(self,config="servers.json"):
        self.templator = Templator()
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
            self.cmd(server['ip'],'apt-get update && apt-get install snap snapd -y && snap install core && snap install lxd --channel=4.0/stable && /snap/bin/lxd init --auto',False)

    def rqlite(self):
        for server in self.servers:
            print(server['name'],"Installing rqlite")
            rqliteConfig = self.templator.rqlite(server['name'],server['vpn'],self.servers[0]['vpn'])
            self.cmd(server['ip'],'useradd rqlite -m -d /home/rqlite/ -s /bin/bash && su rqlite -c "cd; wget https://github.com/rqlite/rqlite/releases/download/v6.0.0/rqlite-v6.0.0-linux-amd64.tar.gz && tar xvf rqlite-v6.0.0-linux-amd64.tar.gz && mv rqlite-v6.0.0-linux-amd64 rqlite"',False)
            self.cmd(server['ip'],'echo "'+rqliteConfig+'" > /etc/systemd/system/rqlite.service && systemctl enable rqlite && systemctl start rqlite',False)

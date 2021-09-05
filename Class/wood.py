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
        for name,details in items(self.servers['servers']):
            print(name,"Installing LXD")
            self.cmd(server['ip'],'apt-get update && apt-get install snap snapd -y && snap install core && snap install lxd --channel=4.0/stable && /snap/bin/lxd init --auto',False)

    def rqlite(self):
        for name,details in items(self.servers['servers']):
            print(name,"Installing rqlite")
            rqliteConfig = self.templator.rqlite(name,server['vpn'],self.servers[0]['vpn'])
            self.cmd(server['ip'],'useradd rqlite -m -d /home/rqlite/ -s /bin/bash && su rqlite -c "cd; wget https://github.com/rqlite/rqlite/releases/download/v6.0.0/rqlite-v6.0.0-linux-amd64.tar.gz && tar xvf rqlite-v6.0.0-linux-amd64.tar.gz && mv rqlite-v6.0.0-linux-amd64 rqlite"',False)
            self.cmd(server['ip'],'echo "'+rqliteConfig+'" > /etc/systemd/system/rqlite.service && systemctl enable rqlite && systemctl start rqlite',False)
            self.cmd(server['ip'],'echo "'+server['vpn']+' rqlite" >> /etc/hosts',False)

    def wood(self):
        for name,details in items(self.servers['servers']):
            print(name,"Installing woodKubernetes")
            self.cmd(server['ip'],'apt-get install git python3-pip -y && pip3 install psutil && useradd woodKubernetes -m -d /home/woodKubernetes/ -s /bin/bash && groupadd lxd && sudo usermod -a -G lxd woodKubernetes && su woodKubernetes -c "cd; git clone https://github.com/Ne00n/woodKubernetes.git"',False)

    def service(self):
        for name,details in items(self.servers['servers']):
            print(name,"Installing service")
            woodConfig = self.templator.woodKubernetes()
            self.cmd(server['ip'],'echo "'+woodConfig+'" > /etc/systemd/system/woodKubernetes.service && systemctl enable woodKubernetes && systemctl start woodKubernetes',False)

    def update(self):
        for name,details in items(self.servers['servers']):
            print(name,"Stopping woodKubernetes service")
            self.cmd(server['ip'],'systemctl stop woodKubernetes',False)
            print(name,"Updating local git repo")
            self.cmd(server['ip'],'su woodKubernetes -c "cd /home/woodKubernetes/woodKubernetes/ && git pull"',False)
            print(name,"Starting woodKubernetes service")
            self.cmd(server['ip'],'systemctl start woodKubernetes',False)

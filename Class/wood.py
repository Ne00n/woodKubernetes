from Class.templator import Templator
import subprocess, random, time, json, re

servers = {}

class Wood:

    def __init__(self,config="servers.json"):
        self.templator = Templator()
        print("Loading",config)
        with open(config) as handle:
            self.servers = json.loads(handle.read())

    def cmd(self,server,command):
        cmd = ['ssh','root@'+server,command]
        for run in range(4):
            try:
                p = subprocess.run(cmd, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
                if p.returncode != 0:
                    print("Warning got returncode",p.returncode,"on",server)
                    print("Error:",p.stderr.decode('utf-8'))
                if p.returncode != 255: return [p.stdout.decode('utf-8'),p.stderr.decode('utf-8')]
            except Exception as e:
                print("Error:",e)
            print("Retrying",cmd,"on",server)
            time.sleep(random.randint(5, 15))

    def lxd(self):
        size = input("How big should the btrfs storage pool be? (GB): ")
        for name,details in self.servers['servers'].items():
            print(name,"Installing LXD")
            self.cmd(details['ip'],'apt-get update && apt-get install snap snapd -y && snap install core && snap install lxd --channel=4.0/stable && /snap/bin/lxd init --auto  --storage-backend=btrfs --storage-create-loop='+str(size))

    def rqlite(self):
        for name,details in self.servers['servers'].items():
            print(name,"Installing rqlite")
            rqliteConfig = self.templator.rqlite(name,server['vpn'],self.servers[0]['vpn'])
            self.cmd(details['ip'],'useradd rqlite -m -d /home/rqlite/ -s /bin/bash && su rqlite -c "cd; wget https://github.com/rqlite/rqlite/releases/download/'+str(rqlite)+'/rqlite-'+str(rqlite)+'-linux-amd64.tar.gz && tar xvf rqlite-'+str(rqlite)+'-linux-amd64.tar.gz && mv rqlite-'+str(rqlite)+'-linux-amd64 rqlite"')
            self.cmd(details['ip'],'echo "'+rqliteConfig+'" > /etc/systemd/system/rqlite.service && systemctl enable rqlite && systemctl start rqlite')
            self.cmd(details['ip'],'echo "'+server['vpn']+' rqlite" >> /etc/hosts')

    def wood(self):
        for name,details in self.servers['servers'].items():
            print(name,"Installing woodKubernetes")
            self.cmd(details['ip'],'apt-get install git python3-pip -y && pip3 install psutil && useradd woodKubernetes -m -d /home/woodKubernetes/ -s /bin/bash && groupadd lxd && sudo usermod -a -G lxd woodKubernetes && su woodKubernetes -c "cd; git clone https://github.com/Ne00n/woodKubernetes.git"')

    def service(self):
        for name,details in self.servers['servers'].items():
            print(name,"Installing service")
            woodConfig = self.templator.woodKubernetes()
            self.cmd(details['ip'],'echo "'+woodConfig+'" > /etc/systemd/system/woodKubernetes.service && systemctl enable woodKubernetes && systemctl start woodKubernetes')

    def update(self):
        for name,details in self.servers['servers'].items():
            print(name,"Stopping woodKubernetes service")
            self.cmd(details['ip'],'systemctl stop woodKubernetes')
            print(name,"Updating local git repo")
            self.cmd(details['ip'],'su woodKubernetes -c "cd /home/woodKubernetes/woodKubernetes/ && git pull"')
            print(name,"Starting woodKubernetes service")
            self.cmd(details['ip'],'systemctl start woodKubernetes')

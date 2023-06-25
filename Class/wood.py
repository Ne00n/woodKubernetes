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
        poolDriver = input("What storage type should be used? (btrfs or lvm): ")
        poolType = input("Loop disk or Dedicated partition/disk? (loop or /dev/sda..,): ")
        poolSize = input(f"How big should the {poolType} storage pool be? min. 5GB (GB): ") if poolType == "loop" else 0
        for name,details in self.servers['servers'].items():
            lxd = "apt-get update && apt-get install lxd -y && /usr/bin/lxd --auto"
            print(name,"Installing LXD")
            if poolType == "loop":
                self.cmd(details['ip'],f'{lxd} --storage-backend={poolDriver} --storage-create-loop={str(size)}')
            else:
                self.cmd(details['ip'],f'{lxd} --storage-backend={poolDriver} --storage-create-device={poolType}')

    def rqlite(self,option):
        first = next(iter(self.servers['servers'].keys()))
        for name,details in self.servers['servers'].items():
            if option == "purge":
                print(name,"Purging rqlite")
                self.cmd(details['ip'],'systemctl disable rqlite && systemctl stop rqlite')
                self.cmd(details['ip'],'userdel -r rqlite')
            else:
                print(name,"Installing rqlite")
                rqliteConfig = self.templator.rqlite(name,details['vpn'],self.servers['servers'][first]['vpn'])
                self.cmd(details['ip'],'useradd rqlite -m -d /home/rqlite/ -s /bin/bash && su rqlite -c "cd; wget https://github.com/rqlite/rqlite/releases/download/v'+str(self.servers['rqlite'])+'/rqlite-v'+str(self.servers['rqlite'])+'-linux-amd64.tar.gz && tar xvf rqlite-v'+str(self.servers['rqlite'])+'-linux-amd64.tar.gz && mv rqlite-v'+str(self.servers['rqlite'])+'-linux-amd64 rqlite"')
                self.cmd(details['ip'],'echo "'+rqliteConfig+'" > /etc/systemd/system/rqlite.service && systemctl enable rqlite && systemctl start rqlite')
                self.cmd(details['ip'],'echo "'+details['vpn']+' rqlite" >> /etc/hosts')

    def wood(self):
        if len(self.servers['servers']) < 3:
            print("Warning, you need at least 3 servers to build a cluster")
            abort = input("Continue (y/n): ")
            if abort != "y": exit("aborting")
        for name,details in self.servers['servers'].items():
            print(name,"Installing woodKubernetes")
            self.cmd(details['ip'],'apt-get install git python3-pip -y && pip3 install psutil && useradd woodKubernetes -m -d /home/woodKubernetes/ -s /bin/bash && groupadd lxd -f && sudo usermod -a -G lxd woodKubernetes && su woodKubernetes -c "cd; git clone https://github.com/Ne00n/woodKubernetes.git"')

    def service(self,option):
        for name,details in self.servers['servers'].items():
            if option == "disable":
                print(name,"Disabling service")
                self.cmd(details['ip'],'systemctl disable woodKubernetes && systemctl stop woodKubernetes')
            else:
                print(name,"Installing service")
                woodConfig = self.templator.woodKubernetes()
                self.cmd(details['ip'],'echo "'+woodConfig+'" > /etc/systemd/system/woodKubernetes.service && systemctl enable woodKubernetes && systemctl start woodKubernetes')

    def update(self,branch="master"):
        for name,details in self.servers['servers'].items():
            print(name,"Stopping woodKubernetes service")
            self.cmd(details['ip'],'systemctl stop woodKubernetes')
            print(name,"Updating local git repo")
            self.cmd(details['ip'],f'su woodKubernetes -c "cd /home/woodKubernetes/woodKubernetes/ && git checkout {branch} && git pull"')
            print(name,"Starting woodKubernetes service")
            self.cmd(details['ip'],'systemctl start woodKubernetes')

    def preload(self):
        print("--- Quick options ---")
        os = ["debian/bullseye/amd64","debian/bullseye/arm64","debian/bookworm/amd64","debian/bookworm/arm64"]
        for index, entry in enumerate(os):
            print(index,entry)
        template = input("What image should be preloaded? ")
        if template.isnumeric():
            for index, entry in enumerate(os):
                if int(template) == index: 
                    template = entry
                    break
        for name,details in self.servers['servers'].items():
            print(name,"preloading",template)
            self.cmd(details['ip'],'/snap/bin/lxc image copy images:'+template+' local: --copy-aliases --auto-update')

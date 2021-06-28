from Class.rqlite import rqlite
import subprocess, socket, psutil, json, time

class LXD(rqlite):

    def run(self):
        hostname = socket.gethostname()
        if "." in hostname:
            sub = hostname.split(".", 1)[0]
        else:
            sub = hostname

        memory = int(psutil.virtual_memory().total / 1e+6)
        while True:
            node = self.query(['SELECT * FROM nodes WHERE name = "'+hostname+'"'])
            if node is False: time.sleep(30)

            if not 'values' in node['results'][0]:
                result = self.execute(['INSERT INTO nodes(name,memory,updated) VALUES(?, ?, ?)',hostname,memory,int(time.time())])
            else:
                self.execute(['UPDATE nodes SET memory = ?, updated = ?',memory,int(time.time())])
            break

        while True:
            nodes = self.nodes()
            if hostname+":4002" not in nodes:
                print("Warning, could not find",hostname,"in rqlite nodes")
                time.sleep(60)
                continue

            current = nodes[hostname+":4002"]
            if current['leader'] is True:
                print("leader")

            machines = self.query(['SELECT * FROM machines'])
            if machines is False or not 'values' in machines['results'][0]:
                time.sleep(60)
                continue

            machineList,containerList = {},[]
            for machine in machines['results'][0]['values']:
                machineList[machine[0]] = machine[1]

            containersRaw = subprocess.check_output(['lxc', 'list', '--format=json']).decode("utf-8")
            containers = json.loads(containersRaw)
            #check existing containers
            for container in containers:
                containerList.append(container['name'])
                if container['name'] not in machineList:
                    self.terminate(container)
                else:
                    if machineList[container['name']] != hostname:
                        self.terminate(container)
            #check if we should deploy a new one
            for machine in machines['results'][0]['values']:
                if machine[1] == hostname and machine[0] not in containerList:
                    self.deploy(machine)
            time.sleep(300)

    def deploy(self,machine):
        print("Deploying",machine[0])
        subprocess.call(['lxc', 'launch',machine[2],machine[0],"-c","limits.memory="+str(machine[3])+"MB"])
        time.sleep(15)
        print("Script",machine[0])
        subprocess.call(['lxc', 'exec',machine[0],"--","bash","-c",machine[4]])

    def terminate(self,machine):
        print("Deleting",machine['name'])
        if machine['state']['status'] == "Running":
            subprocess.call(['lxc', 'stop',machine['name']])
        subprocess.call(['lxc', 'delete',machine['name']])

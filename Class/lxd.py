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
            if hostname not in nodes:
                print("Warning, could not find",hostname,"in rqlite nodes")
                time.sleep(30)
                continue

            containersRaw = subprocess.check_output(['lxc', 'list', '--format=json']).decode("utf-8")
            containers = json.loads(containersRaw)

            machines = self.query(['SELECT * FROM machines'])
            if machines is False or not 'values' in machines['results'][0]:
                print("No machines found")
                if machines is not False: for container in containers: self.terminate(container)
                time.sleep(30)
                continue

            machineList,containerList = {},[]
            for machine in machines['results'][0]['values']:
                machineList[machine[0]] = machine[1]

            current = nodes[hostname]
            if current['leader'] is True:
                for machine,node in machineList.items():
                    #check if anything is not allocated
                    if node is None:
                        self.switchMachine(nodes,machine)
                        continue
                    #checking if anything wen't down
                    if node in nodes and nodes[node]['reachable'] is not True:
                        self.switchMachine(nodes,machine)

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
            time.sleep(30)

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

    def switchMachine(self,nodes,machine):
        print("Switching",machine)
        for node,data in nodes.items():
            if data['reachable'] is True:
                print("Switching",machine,"to",node)
                self.execute(['UPDATE machines SET node = ?',node])

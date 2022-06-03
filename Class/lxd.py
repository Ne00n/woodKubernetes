from Class.rqlite import rqlite
import subprocess, socket, psutil, json, time

class LXD(rqlite):

    def run(self):
        hostname = socket.gethostname()
        if "." in hostname:
            sub = hostname.split(".", 1)[0]
        else:
            sub = hostname

        hostMemory = int(psutil.virtual_memory().total / 1e+6)
        while True:
            node = self.query(['SELECT * FROM nodes WHERE name =  ?',hostname])
            if node is False:
                time.sleep(10)
                continue

            if not 'values' in node['results'][0]:
                result = self.execute(['INSERT INTO nodes(name,memory,updated) VALUES(?, ?, ?)',hostname,hostMemory,int(time.time())])
            else:
                self.execute(['UPDATE nodes SET memory = ?, updated = ? WHERE name = ?',hostMemory,int(time.time()),hostname])
            break

        while True:
            nodes = self.nodes()
            if hostname not in nodes:
                print("Warning, could not find",hostname,"in rqlite nodes")
                time.sleep(10)
                continue

            containersRaw = subprocess.check_output(['lxc', 'list', '--format=json']).decode("utf-8")
            containers = json.loads(containersRaw)

            machines = self.query(['SELECT * FROM machines'])
            if machines is False or not 'values' in machines['results'][0]:
                print("No machines found")
                if machines is not False:
                    for container in containers: self.terminate(container)
                time.sleep(10)
                continue

            machineList,containerList = {},[]
            for machine in machines['results'][0]['values']:
                machineList[machine[0]] = {"node":machine[1],"memory":machine[3]}

            current = nodes[hostname]
            if current['leader'] is True:
                for machine,details in machineList.items():
                    #check if anything is not allocated
                    if details['node'] is None:
                        self.switchMachine(nodes,machine,machines,hostMemory,details['memory'])
                        continue
                    #checking if anything wen't down
                    if details['node'] in nodes and nodes[details['node']]['reachable'] is not True:
                        self.switchMachine(nodes,machine,machines,hostMemory,details['memory'])

            #check existing containers
            for container in containers:
                containerList.append(container['name'])
                if container['name'] not in machineList or machineList[container['name']]['node'] != hostname:
                    self.terminate(container)
            #check if we should deploy a new one
            for machine in machines['results'][0]['values']:
                if machine[1] == hostname and machine[0] not in containerList:
                    self.deploy(machine)
            time.sleep(10)

    def getMemoryUsage(self,node,machines):
        total = 0
        for machine in machines['results'][0]['values']:
            if machine[1] == node: total = total + int(machine[3])
        return total

    def deploy(self,machine):
        print("Deploying",machine[0])
        subprocess.call(['lxc', 'launch',machine[2],machine[0],"-c","limits.memory="+str(machine[4])+"MB"])
        subprocess.call(['lxc','config','set',machine[0],f'limits.cpu {machine[3]}'])
        time.sleep(15)
        print("Script",machine[0])
        subprocess.call(['lxc', 'exec',machine[0],"--","bash","-c",machine[5]])
        if machine[6] != 0:
            print(f"{machine[0]} Ports")
            ports = machine[6].split(",")
            for port in ports:
                ingress, egress = port.split(':')
                subprocess.call(['lxc','config','device','add',machine[0],f'port{str(ingress)}','proxy',f'listen=tcp:0.0.0.0:{str(egress)}',f'connect=tcp:127.0.0.1:{str(egress)}'])
            mounts = machine[6].split(",")
        if machine[7] != "none":
            print(f"{machine[0]} Mounts")
            mounts = machine[7].split(",")
            for mount in mounts:
                parts = mount.split(":")
                source, path = mount.split(':')
                subprocess.call(['lxc','config','device','add',machine[0],{source},'disk',f'source={source}',f'path={path}'])

    def terminate(self,machine):
        print("Deleting",machine['name'])
        if machine['state']['status'] == "Running":
            subprocess.call(['lxc', 'stop',machine['name']])
        subprocess.call(['lxc', 'delete',machine['name']])

    def switchMachine(self,nodes,machine,machines,hostMemory,memory):
        print("Switching",machine)
        for node,data in nodes.items():
            if data['reachable'] is True and hostMemory > int(memory) + self.getMemoryUsage(node,machines):
                print("Switching",machine,"to",node)
                self.execute(['UPDATE machines SET node = ? WHERE name = ?',node,machine])

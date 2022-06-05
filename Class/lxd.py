from Class.rqlite import rqlite
import subprocess, socket, psutil, random, json, time

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
            if nodes is False:
                print("Warning, could not fetch nodes")
                time.sleep(10)
                continue
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
            for machine in self.table(machines):
                machineList[machine['name']] = machine

            current = nodes[hostname]
            if current['leader'] is True:
                for machine,details in machineList.items():
                    #check if anything is not allocated
                    if details['nodes'] is None:
                        self.switchMachine(nodes,hostname,machine,machines,hostMemory,details)
                        continue
                    #checking if anything wen't down
                    if set(details['nodes'].split(',')).issubset(nodes) and nodes[details['node']]['reachable'] is not True:
                        self.switchMachine(nodes,hostname,machine,machines,hostMemory,details,True)

            #check existing containers
            for container in containers:
                containerList.append(container['name'])
                if container['name'] not in machineList or machineList[container['name']]['node'] != hostname:
                    self.terminate(container)
            #check if we should deploy a new one
            for machine in self.table(machines):
                if hostname in machine['nodes'].split(",") and machine['name'] not in containerList:
                    self.deploy(machine)
            time.sleep(10)

    def getMemoryUsage(self,node,machines):
        total = 0
        for machine in self.table(machines):
            if node in machine['nodes'].split(","): total = total + int(machine['memory'])
        return total

    def deploy(self,machine):
        print("Deploying",machine['name'])
        response = subprocess.call(['lxc','launch',machine['os'],machine['name'],'-c',f'limits.memory={machine['memory']}MB','-c',f'limits.cpu={machine['cores']}'])
        #on failure, try re-deploy on different node
        if response != 0:
            self.execute(['UPDATE machines SET nodes = NULL WHERE name = ?',machine['name']])
            return False
        #apply storage limit
        subprocess.call(['lxc','config','device','override',machine['machine'],'root',f'size={machine['storage']}GB'])
        #wait for boot
        time.sleep(15)
        #run script
        print("Script",machine[0])
        subprocess.call(['lxc', 'exec',machine['machine'],"--","bash","-c",machine['deploy']])
        if machine['ports'] != "none":
            print(f"{machine['name']} Ports")
            ports = machine['ports'].split(",")
            for port in ports:
                ingress, egress = port.split(':')
                subprocess.call(['lxc','config','device','add',machine['name'],f'port{str(ingress)}','proxy',f'listen=tcp:0.0.0.0:{str(egress)}',f'connect=tcp:127.0.0.1:{str(egress)}'])
        if machine['mounts'] != "none":
            print(f"{machine['name']} Mounts")
            mounts = machine['mounts'].split(",")
            for mount in mounts:
                parts = mount.split(":")
                source, path = mount.split(':')
                subprocess.call(['lxc','config','device','add',machine['name'],{source},'disk',f'source={source}',f'path={path}'])

    def terminate(self,machine):
        print("Deleting",machine['name'])
        if machine['state']['status'] == "Running":
            subprocess.call(['lxc', 'stop',machine['name']])
        subprocess.call(['lxc', 'delete',machine['name']])

    def switchMachine(self,nodes,hostname,machine,machines,hostMemory,details,outage=False):
        #randomize
        nodeItems = list(nodes.items())
        random.shuffle(nodeItems)
        nodes = dict(nodeItems)
        #switching
        print("Switching",machine)
        deploy = details['nodes'].split(',') if outage: else []
        for node,data in nodes.items():
            if data['reachable'] is True and hostMemory > int(details['memory']) + self.getMemoryUsage(node,machines) and node not in deploy:
                print("Switching",machine,"to",node)
                #remove old node that has been marked as offline
                if outage and hostname in deploy: deploy.remove(hostname)
                #append new node
                deploy.append(node)
                #break if replica limit reached or 0 for all nodes
                if details['replica'] != 0 and details['replica'] == len(deploy): break
        self.execute(['UPDATE machines SET node = ? WHERE name = ?',','.join(deploy),machine])

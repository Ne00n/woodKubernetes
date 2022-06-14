from Class.rqlite import rqlite
import json, time

class CLI(rqlite):

    def addMachine(self,data):
        print(f"Deploying {data[0]}")
        mount = data[8] if len(data) > 8 else "none"
        ports = data[7] if len(data) > 7 else "none"
        response = self.execute(['INSERT INTO machines(name,replica,os,cores,memory,storage,deploy,ports,mounts) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)',data[0],data[1].replace("r",""),data[2],data[3],data[4].replace("MB",""),data[5].replace("GB",""),data[6],ports,mount])
        print(json.dumps(response, indent=4, sort_keys=True))

    def addHaproxy(self,data):
        print(f"Adding {data[0]}")
        response = self.execute(['INSERT INTO haproxy(domain,machine) VALUES(?, ?)',data[0],data[1]])
        print(json.dumps(response, indent=4, sort_keys=True))

    def getTable(self,table="machines"):
        response = self.query(["SELECT rowid, * FROM "+table])
        print(json.dumps(response, indent=4, sort_keys=True))

    def deleteMachine(self,data):
        response = self.execute(['DELETE FROM machines WHERE name=?',data[0]])
        print(json.dumps(response, indent=4, sort_keys=True))

    def deleteHaproxy(self,data):
        response = self.execute(['DELETE FROM haproxy WHERE domain=?',data[0]])
        print(json.dumps(response, indent=4, sort_keys=True))

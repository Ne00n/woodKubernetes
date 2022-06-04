from Class.rqlite import rqlite
import json, time

class CLI(rqlite):

    def addMachine(self,data):
        print(f"Deploying {data[0]}")
        mount = data[7] if len(data) > 7 else "none"
        ports = data[6] if len(data) > 6 else "0"
        response = self.execute(['INSERT INTO machines(name,os,cores,memory,storage,deploy,ports,mount) VALUES(?, ?, ?, ?, ?, ?, ?, ?)',data[0],data[1],data[2],data[3].replace("MB",""),data[4].replace("GB",""),data[5],ports,mount])
        print(json.dumps(response, indent=4, sort_keys=True))

    def getTable(self,table="machines"):
        response = self.query(["SELECT rowid, * FROM "+table])
        print(json.dumps(response, indent=4, sort_keys=True))

    def deleteMachine(self,data):
        response = self.execute(['DELETE FROM machines WHERE name=?',data[0]])
        print(json.dumps(response, indent=4, sort_keys=True))

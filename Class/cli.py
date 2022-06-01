from Class.rqlite import rqlite
import json, time

class CLI(rqlite):

    def addMachine(self,data):
        print("deploying",data[0])
        mount = data[5] if len(data) > 5 else "none"
        ports = data[4] if len(data) > 4 else 0
        response = self.execute(['INSERT INTO machines(name,os,memory,deploy,ports,mount) VALUES(?, ?, ?, ?, ?, ?)',data[0],data[1],data[2],data[3],ports,mount])
        print(json.dumps(response, indent=4, sort_keys=True))

    def getTable(self,table="machines"):
        response = self.query(["SELECT rowid, * FROM "+table])
        print(json.dumps(response, indent=4, sort_keys=True))

    def deleteMachine(self,data):
        response = self.execute(['DELETE FROM machines WHERE name=?',data[0]])
        print(json.dumps(response, indent=4, sort_keys=True))

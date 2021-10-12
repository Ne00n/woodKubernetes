from Class.rqlite import rqlite
import json, time

class CLI(rqlite):

    def addMachine(self,data):
        print("deploying",data[0])
        response = self.execute(['INSERT INTO machines(name,os,memory,ports,deploy) VALUES(?, ?, ?, ?, ?)',data[0],data[1],data[2],data[3],data[4]])
        print(json.dumps(response, indent=4, sort_keys=True))

    def addCert(self,data):
        print("adding",data[0])
        response = self.execute(['INSERT INTO certs(domain,machine,api) VALUES(?, ?, ?)',data[0],data[1],data[2]])
        print(json.dumps(response, indent=4, sort_keys=True))

    def getTable(self,table="machines"):
        response = self.query(["SELECT rowid, * FROM "+table])
        print(json.dumps(response, indent=4, sort_keys=True))

    def deleteMachine(self,data):
        response = self.execute(['DELETE FROM machines WHERE name=?',data[0]])
        print(json.dumps(response, indent=4, sort_keys=True))

    def deleteCert(self,data):
        response = self.execute(['DELETE FROM certs WHERE domain=?',data[0]])
        print(json.dumps(response, indent=4, sort_keys=True))

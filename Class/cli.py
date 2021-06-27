from Class.rqlite import rqlite
import json, time

class CLI(rqlite):

    def addContainer(self,data):
        print("deploying",data[0])
        response = self.execute(['INSERT INTO machines(name,os,memory,deploy) VALUES(?, ?, ?, ?)',data[0],data[1],data[2],data[3]])
        print(json.dumps(response, indent=4, sort_keys=True))

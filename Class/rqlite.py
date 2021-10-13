import requests, time, json

class rqlite:

    ip,port = "rqlite",4003

    def curl(self,url,query):
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        #retry 4 times
        for run in range(4):
            try:
                if not query:
                    r = requests.get(url,allow_redirects=False)
                else:
                    query = json.dumps(query)
                    r = requests.post(url, data=query, headers=headers,allow_redirects=False)
                if r.status_code == 301:
                    leader = r.headers['Location']
                    r = requests.post(leader, data=query, headers=headers,allow_redirects=False)
                if (r.status_code == 200):
                    return r.json()
            except Exception as e:
                print(e)
            time.sleep(2)
        return False

    def query(self,query,level="none",timings="&timings"):
        url = 'http://'+self.ip+':'+str(self.port)+'/db/query?pretty'+timings+'&level='+level
        return self.curl(url,query)

    def execute(self,query):
        url = 'http://'+self.ip+':'+str(self.port)+'/db/execute?pretty&timings'
        query = [query]
        return self.curl(url,query)

    def status(self):
        url = 'http://'+self.ip+':'+str(self.port)+'/status?pretty'
        return self.curl(url,[])

    def nodes(self):
        url = 'http://'+self.ip+':'+str(self.port)+'/nodes?pretty'
        return self.curl(url,[])

    def init(self):
        self.execute(["CREATE TABLE nodes (name TEXT NOT NULL PRIMARY KEY, memory INTEGER NOT NULL, updated INTEGER NOT NULL)"])
        self.execute(["CREATE TABLE machines (name TEXT NOT NULL PRIMARY KEY, node TEXT NULL, os TEXT NOT NULL, memory INTEGER NOT NULL, ports TEXT NOT NULL, deploy TEXT NULL, FOREIGN KEY(node) REFERENCES nodes(name) ON DELETE CASCADE)"])
        self.execute(["CREATE TABLE certs (domain TEXT NOT NULL PRIMARY KEY, email TEXT NOT NULL, machine TEXT NOT NULL, api TEXT NOT NULL, fullchain TEXT NULL, privkey TEXT NULL, updated INTEGER NULL, FOREIGN KEY(machine) REFERENCES machines(name) ON DELETE CASCADE)"])
        self.execute(["CREATE TABLE apis (name TEXT NOT NULL PRIMARY KEY, type TEXT NOT NULL, up TEXT NOT NULL, down TEXT NOT NULL)"])
        self.execute(["CREATE TABLE fids (fid TEXT NOT NULL PRIMARY KEY, machine TEXT NULL, tag TEXT NOT NULL, FOREIGN KEY(machine) REFERENCES machines(name) ON DELETE CASCADE)"])
        self.execute(["PRAGMA foreign_keys = ON"])

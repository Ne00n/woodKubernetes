from Class.rqlite import rqlite
import simple_acme_dns, requests, json, time, sys, os

class Cert(rqlite):

    def updateCert(self,data):
        print("updating",data[0])
        response = self.execute(['UPDATE certs SET fullchain = ?,privkey = ?,updated = ? WHERE domain = ?',data[1],data[2],data[3],data[0]])
        print(json.dumps(response, indent=4, sort_keys=True))

    def buildbuildUrls(self,urls,domain,token):
        response = []
        for url in urls:
            subdomain = ""
            parts = domain.split(".")
            if len(parts) > 2:
                parts = parts[:len(parts) -2]
                subdomain = '.'.join(parts)
            #api.dns.com/mahkey/%domain%/%sub%/TXT/add/%challenge%
            url = url.replace("domain",domain.replace(subdomain+".",""))
            subdomain = "_acme-challenge." + subdomain
            url = url.replace("sub",subdomain)
            url = url.replace("challenge",token)
            response.append(url)
        return response

    def buildUrls(self,domain,token,api):
        apis = self.query(["SELECT * FROM apis WHERE name = ?",api])
        if apis is False: return False
        if 'values' not in apis['results'][0]: return False
        apis = apis['results'][0]['values'][0]
        response = {"up":[],"down":[]}
        urls = apis[2].split(",")
        response['up'] = self.buildbuildUrls(urls,domain,token)
        urls = apis[3].split(",")
        response['down'] = self.buildbuildUrls(urls,domain,token)
        return response

    def getCert(self,domain,email,api):
        #directory = "https://acme-v02.api.letsencrypt.org/directory"
        directory = "https://acme-staging-v02.api.letsencrypt.org/directory"
        try:
            client = simple_acme_dns.ACMEClient(domains=[domain],email=email,directory=directory,nameservers=["8.8.8.8", "1.1.1.1"],new_account=True,generate_csr=True)
        except Exception as e:
            print(e)
            return False

        for acmeDomain, token in client.request_verification_tokens():
            print("adding {domain} --> {token}".format(domain=acmeDomain, token=token))
            urls = self.buildUrls(domain,token,api)
            if urls is False: return False
            for url in urls['up']:
                r = requests.get(url,allow_redirects=False)
                if (r.status_code != 200): return False

        print("Waiting for dns propagation")
        try:
            if client.check_dns_propagation(timeout=1200):
                print("Requesting certificate")
                client.request_certificate()
                fullchain = client.certificate.qqdecode()
                privkey = client.private_key.decode()
                self.updateCert([domain,fullchain,privkey,int(time.time())])
            else:
                print("Failed to issue certificate for " + str(client.domains))
                client.deactivate_account()
                return False
        except Exception as e:
            print(e)
            return False
        finally:
            for url in urls['down']:
                r = requests.get(url,allow_redirects=False)
                if (r.status_code != 200): return False
        return True

    def renew(self):
        status = self.status()
        if status is False:
            print("rqlite gone")
            return False

        state = status['store']['raft']['state']
        if state != "Leader":
            print("Not leader, aborting.")
            return False

        print("Getting certs")
        domains = self.query(['SELECT * FROM certs'])

        if domains is False:
            print("rqlite gone")
            return False
        if 'values' not in domains['results'][0]:
            print("no certs added")
            return False

        for row in domains['results'][0]['values']:
            if row[4] == None:
                print("Missing cert for",row[0])

                response = self.getCert(row[0],row[1],row[3])
                if response is False:
                    print("Failed to get cert for",row[0])
                    return False

            else:
                print("Checking cert for",row[0])
                if time.time() > (row[6] + (86400 * 30)):
                    print("Certificate is older than 30 days")

                    response = self.getCert(row[0],row[1],row[3])
                    if response is False:
                        print("Failed to get cert for",row[0])
                        return False

# woodKubernetes

## Work in Progress

**Idea**<br />
- High Availability of LXD containers without LXD cluster and/or CephFS

**Why**
- Kubernetes is way to complex for my use case
- LXD Cluster needs CephFS storage backend + won't work well on higher latency

**Software**<br />
- [LXD](https://github.com/lxc/lxd) for running the containers
- [rqlite](https://github.com/rqlite/rqlite) to store containers info/leader choice

**Features**<br />
- High Availability
- Port Forwarding
- Mount Folders from glusterFS/seaweedFS
- Replica

**Requirements**
- 3+ Nodes with Ubuntu 20/22.04 or Debian 10/11
- Each node should have at least 1GB of Memory
- Mesh VPN connecting them together ([Tinc](https://www.tinc-vpn.org/)/[VpnCloud](https://github.com/dswd/vpncloud)/[Wireguard](https://www.wireguard.com/))

**Prepare**<br />
Rename servers.example.json to servers.json and fill it up<br />

## Setup<br />
1. Deploy LXD on all Nodes and init<br />
By default a loop file is used with lvm
```
python3 wood.py lxd
```
2. Deploy rqlite on all Nodes<br />
Check if the version is up to date
```
python3 wood.py rqlite
```
Check the rqlite cluster status:
```
curl rqlite:4003/nodes?pretty
```
3. Deploy woodKubernetes
```
python3 wood.py wood
```
4. SSH into any machine and Initialize the Database
```
su woodKubernetes -c "cd /home/woodKubernetes/woodKubernetes/ && python3 cli.py init"
```
5. Deploy the primary service
```
python3 wood.py service
```
6. Deploy the first container<br />

Before you deploy, you should preload the os images you need.<br />
This results in faster deploy times and don't affect you if the image server is down or slow.<br />

nginx example
```
python3 cli.py machine add one r1 debian/11 1 256MB 2GB "apt-get install nginx -y" \
80:80,443:443 
```
nginx example + dir mount
```
python3 cli.py machine add one r1 debian/11 1 256MB 2GB "apt-get install nginx -y" \
80:80,443:443 /mnt/data/www/:/var/www/
```
znc example
```
python3 cli.py machine add one r1 debian/11 1 256MB 2GB "apt-get install wget znc -y" \
1025:1025
```
If you want no port forwarding use none instead

**Preload**<br/>
preload os templates
```
python3 wood.py preload
```

**HAProxy**<br/>
```
python3 cli.py haproxy add domain.com one
```

**Service**<br/>
```
python3 wood.py service <config> disable
```

**rqlite**<br/>
```
python3 wood.py rqlite <config> purge
```

**Update**
```
python3 wood.py update
python3 wood.py update <config> <branch>
```

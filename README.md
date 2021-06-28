# woodKubernetes

## Work in Progress

**Idea**<br />
- High Availability of LXD containers without LXD cluster and/or CephFS

**Why**
- I Dislike Kubernetes, I like Docker, sadly Docker has dogshit IPv6 support
- LXD Cluster needs CephFS storage backend

**Software**<br />
- LXD for running the containers
- rqlite to store containers info/leader choice

**Features**<br />
- High Availability

**Requirements**
- 3+ Nodes with Ubuntu 20.04 or Debian 10
- Mesh VPN connecting them together (Tinc/Wireguard)

**Prepare**<br />
Rename servers.example.json to servers.json and fill it up<br />

## Setup<br />
1. Deploy LXD on all Nodes and init
```
python3 wood.py lxd
```
2. Deploy rqlite on all Nodes
```
python3 wood.py rqlite
```
Check cluster status:
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

**Update**
```
python3 wood.py update
```

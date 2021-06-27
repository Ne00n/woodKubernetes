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
1. Deploy LXD on all Nodes
```
python3 wood.py lxd
```
2. Configure LXD on all nodes
```
lxd init
```

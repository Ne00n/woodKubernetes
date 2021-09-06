# woodKubernetes

## Work in Progress

**Idea**<br />
- High Availability of LXD containers without LXD cluster and/or CephFS

**Why**
- I dislike Kubernetes, I like Docker, sadly Docker has shit IPv6 support
- LXD Cluster needs CephFS storage backend + won't work well on higher latency

**Software**<br />
- [LXD](https://github.com/lxc/lxd) for running the containers
- [rqlite](https://github.com/rqlite/rqlite) to store containers info/leader choice

**Features**<br />
- High Availability

**Requirements**
- 3+ Nodes with Ubuntu 20.04 or Debian 10
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
Check if version is up to date
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
6. Deploy the first container
Nginx example
```
python3 cli.py machine add one debian/buster 256 \
"wget -qO - https://gist.githubusercontent.com/Ne00n/c33cd89a69c039f0279930c70d46433b/raw/ec64796e6bd4bb489932e6db97782477c3e36ffb/test | bash"
```
znc example
```
python3 cli.py machine add one debian/buster 256 \
"wget -qO - https://gist.githubusercontent.com/Ne00n/1fa5851bb86927e68ac82015da5a6744/raw/4a3b783719c12781004202cac3bf9c96d73582b3/znc%2520test%2520deploy | bash"
```

**preload**<br />
preload os templates
```
python3 wood.py preload
```

**Update**
```
python3 wood.py update
```

class Templator:

    def rqlite(self,node,vpn,firstNode):
        template = '''[Unit]
Description=rqlite service
Wants=network-online.target
After=network-online.target

[Service]
User=rqlite
Group=rqlite
Type=simple
WorkingDirectory=/home/rqlite/rqlite
ExecStartPre=/bin/sh -c 'until ping -c1 '''+vpn+'''; do sleep 1; done;'
ExecStart=/home/rqlite/rqlite/rqlited -node-id '''+node+''' -http-addr '''+vpn+''':4003 -raft-addr '''+vpn+''':4004'''
        if not vpn.endswith(".1"): template += ' -join http://'+firstNode+':4003'
        template += ''' datadir

[Install]
WantedBy=multi-user.target'''
        return template

    def woodKubernetes(self):
        template = '''[Unit]
Description=woodKubernetes service
Wants=network-online.target
After=network-online.target

[Service]
User=woodKubernetes
Group=woodKubernetes
Type=simple
WorkingDirectory=/home/woodKubernetes/woodKubernetes/cron/
ExecStart=/usr/bin/python3 wood.py lxd

[Install]
WantedBy=multi-user.target
        '''
        return template

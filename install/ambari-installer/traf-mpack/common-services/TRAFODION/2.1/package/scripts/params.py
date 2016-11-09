#!/usr/bin/env python
from resource_management import *

# config object that holds the configurations declared in the config xml file
config = Script.get_config()

java_home = config['hostLevelParams']['java_home']
dcs_servers = config['configurations']['trafodion-env']['dcs.servers']
dcs_port = config['configurations']['trafodion-env']['dcs.port']
dcs_info_port = config['configurations']['trafodion-env']['dcs.info.port']
traf_db_admin = config['configurations']['trafodion-env']['traf.db.admin']

traf_conf_dir = config['configurations']['trafodion-env']['traf.conf.dir']
traf_env_template = config['configurations']['trafodion-env']['content'] + '\n'

traf_user = 'trafodion'
traf_group = 'trafodion'
traf_priv_key = config['configurations']['trafodion-env']['traf.sshkey.priv']

traf_nodes = default_string("/clusterHostInfo/trafodion_node_hosts", '', ' ')

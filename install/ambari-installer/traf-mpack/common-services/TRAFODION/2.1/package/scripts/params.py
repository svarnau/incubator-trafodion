#!/usr/bin/env python
from resource_management import *

# config object that holds the configurations declared in the config xml file
config = Script.get_config()

java_home = config['hostLevelParams']['java_home']
dcs_servers = config['configurations']['trafodion-env']['dcs.servers']
dcs_port = config['configurations']['trafodion-env']['dcs.port']
dcs_info_port = config['configurations']['trafodion-env']['dcs.info.port']
traf_db_admin = config['configurations']['trafodion-env']['traf.db.admin']

traf_conf_dir = '/etc/trafodion/conf' # path is hard-coded in /etc/trafodion_trafodion_config
traf_env_template = config['configurations']['trafodion-env']['content'] + '\n'

traf_user = 'trafodion'
traf_group = 'trafodion'
traf_priv_key = config['configurations']['trafodion-env']['traf.sshkey.priv']

traf_node_list = default("/clusterHostInfo/traf_node_hosts", '')
traf_nodes = ' '.join(traf_node_list)
traf_w_nodes = '-w ' + ' -w '.join(traf_node_list)
traf_node_count = len(traf_node_list)

traf_scratch = config['configurations']['trafodion-env']['traf.node.dir']

#!/usr/bin/env python
from resource_management import *

# config object that holds the configurations declared in the config xml file
config = Script.get_config()

java_home = config['hostLevelParams']['java_home']
dcs_servers = config['configurations']['dcs-env']['dcs.servers']
dcs_port = config['configurations']['dcs-env']['dcs.port']
dcs_info_port = config['configurations']['dcs-env']['dcs.info.port']
traf_db_admin = config['configurations']['trafodion-env']['traf.db.admin']

traf_conf_dir = '/etc/trafodion/conf' # path is hard-coded in /etc/trafodion_trafodion_config
traf_env_template = config['configurations']['trafodion-env']['content'] + '\n'
traf_clust_template = config['configurations']['traf-cluster-env']['content'] + '\n'
traf_dcs_env_template = config['configurations']['dcs-env']['content'] + '\n'

traf_user = 'trafodion'
traf_group = 'trafodion'
hdfs_user = config['configurations']['hadoop-env']['hdfs_user']
hbase_user = config['configurations']['hbase-env']['hbase_user']

traf_priv_key = config['configurations']['trafodion-env']['traf.sshkey.priv']

traf_node_list = default("/clusterHostInfo/traf_node_hosts", '')

traf_scratch = config['configurations']['trafodion-env']['traf.node.dir']

#HDFS Dir creation
hostname = config["hostname"]
hadoop_conf_dir = "/etc/hadoop/conf"
hdfs_user_keytab = config['configurations']['hadoop-env']['hdfs_user_keytab']
security_enabled = config['configurations']['cluster-env']['security_enabled']
kinit_path_local = functions.get_kinit_path(default('/configurations/kerberos-env/executable_search_paths', None))
hdfs_site = config['configurations']['hdfs-site']
default_fs = config['configurations']['core-site']['fs.defaultFS']
import functools
#create partial functions with common arguments for every HdfsDirectory call
#to create hdfs directory we need to call params.HdfsDirectory in code
HdfsDirectory = functools.partial(
  HdfsResource,
  type="directory",
  hadoop_conf_dir=hadoop_conf_dir,
  user=hdfs_user,
  hdfs_site=hdfs_site,
  default_fs=default_fs,
  security_enabled = security_enabled,
  keytab = hdfs_user_keytab,
  kinit_path_local = kinit_path_local
)


import sys, os, pwd, signal, time
from resource_management import *

class Node(Script):
  def install(self, env):
  
    # Install packages listed in metainfo.xml
    self.install_packages(env)
    import params
  
    ##################
    # trafodion cluster-wide ssh config
    trafhome = os.path.expanduser("~" + params.traf_user)
    Directory(os.path.join(trafhome,".ssh"), 
              mode=0700,
              owner = params.traf_user, 
              group = params.traf_group)
    File(os.path.join(trafhome,".ssh/id_rsa"),
         owner = params.traf_user, 
         group = params.traf_group, 
         content=params.traf_priv_key,
         mode=0600)

    cmd = "ssh-keygen -y -f " + trafhome + "/.ssh/id_rsa > " + trafhome + "/.ssh/authorized_keys"
    Execute(cmd,user=params.traf_user)
    cmd = "chmod 0600 " + trafhome + "/.ssh/authorized_keys"
    Execute(cmd,user=params.traf_user)
    sshopt = format('Host *\n' + '    StrictHostKeyChecking=no\n')
    File(os.path.join(trafhome,".ssh/config"),
         owner = params.traf_user, 
         group = params.traf_group, 
         content=sshopt,
         mode=0600)

    ##################
    # create env files
    env.set_params(params)
    Directory(params.traf_conf_dir, 
              mode=0755, 
              owner = params.traf_user, 
              group = params.traf_group, 
              create_parents = True)
    traf_conf_path = os.path.join(params.traf_conf_dir, "trafodion-env.sh")
    File(traf_conf_path,
         owner = params.traf_user, 
         group = params.traf_group, 
         content=InlineTemplate(params.traf_env_template,trim_blocks=False),
         mode=0644)
    # cluster file will be over-written by trafodionmaster install
    # until then, make file that shell can source without error
    traf_conf_path = os.path.join(params.traf_conf_dir, "traf-cluster-env.sh")
    File(traf_conf_path,
         owner = params.traf_user, 
         group = params.traf_group, 
         content="# place-holder",
         mode=0644)
    # initialize & verify env (e.g., creates $SQROOT/tmp as trafodion user)
    cmd = "source ~/.bashrc"
    Execute(cmd,user=params.traf_user)


    # All Trafodion Nodes need DCS config files
    # In future, should move DCS conf to traf_conf_dir
    File(os.path.join(trafhome,"dcs-env.sh"),
         owner = params.traf_user, 
         group = params.traf_group, 
         content = params.dcs_env_template,
         mode=0644)

    serverlist = params.dcs_mast_node_list[0] + '\n'
    File(os.path.join(trafhome,"master"),
         owner = params.traf_user, 
         group = params.traf_group, 
         content = serverlist,
         mode=0644)

    serverlist = '\n'.join(params.dcs_back_node_list) + '\n'
    File(os.path.join(trafhome,"backup-masters"),
         owner = params.traf_user, 
         group = params.traf_group, 
         content = serverlist,
         mode=0644)

    serverlist = ''
    node_cnt = len(traf_node_list)
    per_node = int(params.dcs_servers) // node_cnt
    extra = int(params.dcs_servers) % node_cnt
    for nnum, node in enumerate(params.dcs_back_node_list, start=0):
      if nnum < extra:
         serverlist += '%s %s\n' % (node, per_node + 1)
      else:
         serverlist += '%s %s\n' % (node, per_node)
    File(os.path.join(trafhome,"servers"),
         owner = params.traf_user, 
         group = params.traf_group, 
         content = serverlist,
         mode=0644)
    # install DCS conf files
    cmd = "mv -f ~/dcs-env.sh ~/master ~/backup-masters ~/servers $DCS_INSTALL_DIR/conf/"
    Execute(cmd,user=params.traf_user)



    ##################
    # Link TRX files into HBase lib dir
    hlib = "/usr/hdp/current/hbase-regionserver/lib/"
    trx = "$SQ_HOME/export/lib/hbase-trx-hdp2_3-${TRAFODION_VER}.jar"
    util = "$SQ_HOME/export/lib/trafodion-utility-${TRAFODION_VER}.jar"

    cmd = "rm -f " + hlib + "hbase-trx-* " + hlib + "trafodion-utility-*"
    Execute(cmd)

    # run as root, but expand variables using trafodion env
    cmd = "source ~" + params.traf_user + "/.bashrc ; ln -s " + trx + " " + hlib
    Execute(cmd)
    cmd = "source ~" + params.traf_user + "/.bashrc ; ln -s " + util + " " + hlib
    Execute(cmd)

    ##################
    # create trafodion scratch dirs
    for sdir in params.traf_scratch.split(','):
      Directory(sdir,
                mode=0777,
                owner = params.traf_user,
                group = params.traf_group,
                create_parents = True)
 

  def stop(self, env):
    return True

  def start(self, env):
    return True
	
  def status(self, env):
    import params
    Execute('source ~/.bashrc ; sqcheck -f',user=params.traf_user)

if __name__ == "__main__":
  Node().execute()

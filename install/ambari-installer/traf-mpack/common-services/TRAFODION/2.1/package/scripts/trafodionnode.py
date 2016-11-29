import sys, os, pwd, signal, time
from resource_management import *
#from subprocess import call
#from shutil import copyfile

class Node(Script):
  def install(self, env):
  
    # Install packages listed in metainfo.xml
    self.install_packages(env)
    import params
  
    self.configure(env)

    # create scratch dirs
    for sdir in params.traf_scratch.split(','):
      Directory(sdir,
                mode=0777,
                owner = params.traf_user,
                group = params.traf_group,
                create_parents = True)
 
  def configure(self, env):
    import params
    env.set_params(params)

    Directory(params.traf_conf_dir, 
              mode=0755, 
              owner = params.traf_user, 
              group = params.traf_group, 
              create_parents = True)
    traf_conf_path = os.path.join(params.traf_conf_dir, "trafodion-env.sh")
    File(traf_conf_path,
         owner = params.traf_user, 
         group = params.traf_user, 
         content=InlineTemplate(params.traf_env_template,trim_blocks=False),
         mode=0555)

    # trafodion cluster-wide ssh
    trafhome = os.path.expanduser("~" + params.traf_user)
    Directory(os.path.join(trafhome,".ssh"), 
              mode=0700,
              owner = params.traf_user, 
              group = params.traf_group)
    File(os.path.join(trafhome,".ssh/id_rsa"),
         owner = params.traf_user, 
         group = params.traf_user, 
         content=params.traf_priv_key,
         mode=0600)

    cmd = "ssh-keygen -y -f " + trafhome + "/.ssh/id_rsa > " + trafhome + "/.ssh/authorized_keys"
    Execute(cmd,user=params.traf_user)
    cmd = "chmod 0600 " + trafhome + "/.ssh/authorized_keys"
    Execute(cmd,user=params.traf_user)
    sshopt = format('Host *\n' + '    StrictHostKeyChecking=no\n')
    File(os.path.join(trafhome,".ssh/config"),
         owner = params.traf_user, 
         group = params.traf_user, 
         content=sshopt,
         mode=0600)

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

  def stop(self, env):
    return True

  def start(self, env):
    return True
	
  def status(self, env):
    Execute('source ~/.bashrc ; sqcheck -f',user=params.traf_user)

if __name__ == "__main__":
  Node().execute()

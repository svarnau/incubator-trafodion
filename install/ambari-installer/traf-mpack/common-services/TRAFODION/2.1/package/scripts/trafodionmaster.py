import sys, os, subprocess
from resource_management import *
from tempfile import TemporaryFile

class Master(Script):
  def install(self, env):
    import params
  
    # Install packages listed in metainfo.xml
    self.install_packages(env)

    # generate sqconfig file
    cmd = "lscpu|grep -E '(^CPU\(s\)|^Socket\(s\))'|awk '{print $2}'"
    ofile = TemporaryFile()
    Execute(cmd,stdout=ofile)
    ofile.seek(0) # read from beginning
    core, processor = ofile.read().split('\n')[:2]
    ofile.close()

    core = int(core)-1 if int(core) <= 256 else 255

    lines = ['begin node\n']
    loc_node_list = []
    for node_id, node in enumerate(params.traf_node_list):
        # find the local hostname for each node
        cmd = "ssh %s hostname" % node
        ofile = TemporaryFile()
        Execute(cmd,user=params.traf_user,stdout=ofile)
        ofile.seek(0) # read from beginning
        localhn = ofile.readline().rstrip()
        ofile.close()
 
        line = 'node-id=%s;node-name=%s;cores=0-%d;processors=%s;roles=connection,aggregation,storage\n' \
                 % (node_id, localhn, core, processor)
        lines.append(line)
        loc_node_list.append(localhn)

    lines.append('end node\n')
    lines.append('\n')
    lines.append('begin overflow\n')
    for scratch_loc in params.traf_scratch.split(','):
        line = 'hdd %s\n' % scratch_loc
        lines.append(line)
    lines.append('end overflow\n')

    # write sqconfig in trafodion home dir
    trafhome = os.path.expanduser("~" + params.traf_user)
    File(os.path.join(trafhome,"sqconfig"),
         owner = params.traf_user,
         group = params.traf_user,
         content=''.join(lines),
         mode=0644)

    # install sqconfig
    Execute('source ~/.bashrc ; mv -f ~/sqconfig $MY_SQROOT/sql/scripts/',user=params.traf_user)

    # write cluster-env in trafodion home dir
    traf_nodes = ' '.join(loc_node_list)
    traf_w_nodes = '-w ' + ' -w '.join(loc_node_list)
    traf_node_count = len(loc_node_list)
    if traf_node_count != len(params.traf_node_list):
      print "Error cannot determine local hostname for all Trafodion nodes"
      exit(1)

    cl_env_temp = os.path.join(trafhome,"traf-cluster-env.sh")
    File(cl_env_temp,
         owner = params.traf_user,
         group = params.traf_user,
         content=InlineTemplate(params.traf_clust_template,
                                traf_nodes=traf_nodes,
                                traf_w_nodes=traf_w_nodes,
                                traf_node_count=traf_node_count),
         mode=0644)

    # install cluster-env on all nodes
    for node in params.traf_node_list:
        cmd = "scp %s %s:%s/" % (cl_env_temp, node, params.traf_conf_dir)
        Execute(cmd,user=params.traf_user)
    cmd = "rm -f %s" % (cl_env_temp)
    Execute(cmd,user=params.traf_user)

    # Execute SQ gen
    Execute('source ~/.bashrc ; sqgen',user=params.traf_user)


  #To stop the service, use the linux service stop command and pipe output to log file
  def stop(self, env):
    import params
    Execute('source ~/.bashrc ; sqstop',user=params.traf_user)

  #To start the service, use the linux service start command and pipe output to log file      
  def start(self, env):
    import params

    # Check HDFS set up
    # Must be in start section, since we need HDFS running
    params.HdfsDirectory("/hbase/archive",
                         action="create_on_execute",
                         owner=params.hbase_user,
                         group=params.hbase_user,
                        )
    # To Be Added: 
    #   /hbase-staging
    #   /user/trafodion//{trafodion_backups,bulkload,lobs}
    # ACLs for /hbase/archive
    params.HdfsDirectory(None, action="execute")

    # Start trafodion
    Execute('source ~/.bashrc ; sqstart',user=params.traf_user)
	
  #To get status of the, use the linux service status command      
  def status(self, env):
    import params
    Execute('source ~/.bashrc ; sqcheck -f',user=params.traf_user)
 
  def initialize(self, env):
    ########################## TBD
    returnCode = 0

    if returnCode == 0:
       print "good!"
    else:
       sys.exit(-1)
 

if __name__ == "__main__":
  Master().execute()

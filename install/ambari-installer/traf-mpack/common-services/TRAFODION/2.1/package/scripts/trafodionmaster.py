import sys, os, subprocess
from resource_management import *

class Master(Script):
  def install(self, env):
    import params
  
    # Install packages listed in metainfo.xml
    self.install_packages(env)

    # generate sqconfig file
    cmd = "lscpu|grep -E '(^CPU\(s\)|^Socket\(s\))'|awk '{print $2}'"
    ###p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    ###stdout, stderr = p.communicate()

    ###core, processor = stdout.strip().split('\n')[:2]
    core, processor = as_user(cmd,params.traf_user).split('\n')[:2]

    core = int(core)-1 if int(core) <= 256 else 255

    lines = ['begin node\n']
    for node_id, node in enumerate(params.traf_node_list):
        # find the local hostname for each node
        cmd = "ssh %s hostname" % node
        localhn = as_user(cmd,params.traf_user)
 
        line = 'node-id=%s;node-name=%s;cores=0-%d;processors=%s;roles=connection,aggregation,storage\n' \
                 % (node_id, localhn, core, processor)
        lines.append(line)

    lines.append('end node\n')
    lines.append('\n')
    # To be added - need to set config value for scratch loc or pick data disk?
    #lines.append('begin overflow\n')
    #for scratch_loc in scratch_locs:
    #    line = 'hdd %s\n' % scratch_loc
    #    lines.append(line)
    #lines.append('end overflow\n')

    # write sqconfig in trafodion home dir
    trafhome = os.path.expanduser("~" + params.traf_user)
    File(os.path.join(trafhome,"sqconfig"),
         owner = params.traf_user,
         group = params.traf_user,
         content=''.join(lines),
         mode=0644)

    # install sqconfig
    Execute('source ~/.bashrc ; cp -f ~/sqconfig $MY_SQROOT/sql/scripts/',user=params.traf_user)

    # Execute SQ gen
    Execute('source ~/.bashrc ; sqgen',user=params.traf_user)

  #To stop the service, use the linux service stop command and pipe output to log file
  def stop(self, env):
    import params
    Execute('source ~/.bashrc ; sqstop',user=params.traf_user)

  #To start the service, use the linux service start command and pipe output to log file      
  def start(self, env):
    import params

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

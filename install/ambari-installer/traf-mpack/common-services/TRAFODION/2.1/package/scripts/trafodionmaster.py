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

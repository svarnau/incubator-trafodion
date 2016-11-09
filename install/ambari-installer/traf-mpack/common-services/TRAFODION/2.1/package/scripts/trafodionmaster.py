import sys, os, pwd, signal, time
from resource_management import *
from subprocess import call
from shutil import copyfile

class Master(Script):
  def install(self, env):
  
    # Install packages listed in metainfo.xml
    self.install_packages(env)

  def configure(self, env):
    pass

  #To stop the service, use the linux service stop command and pipe output to log file
  def stop(self, env):
    import params
    Execute('sqstop',user=params.traf_user)

  #To start the service, use the linux service start command and pipe output to log file      
  def start(self, env):
    import params
    Execute('sqgen',user=params.traf_user)
    Execute('sqstart',user=params.traf_user)
	
  #To get status of the, use the linux service status command      
  def status(self, env):
    import params
    Execute('sqcheck -f',user=params.traf_user)
 
  def initialize(self, env):
    ########################## TBD
    returnCode = 0

    if returnCode == 0:
       print "good!"
    else:
       sys.exit(-1)
 

if __name__ == "__main__":
  Master().execute()

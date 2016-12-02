import sys, os, pwd, signal, time
from resource_management import *
#from subprocess import call
#from shutil import copyfile

class DCS(Script):
  def install(self, env):
  
    # Install packages listed in metainfo.xml
    self.install_packages(env)

  def configure(self, env):
    return True

  def stop(self, env):
    import params
    Execute('source ~/.bashrc ; reststop',user=params.traf_user)

  # REST should run on all DCS backup and master nodes
  def start(self, env):
    import params
    Execute('source ~/.bashrc ; sqcheck -f -c rest || reststart',user=params.traf_user)
	
  def status(self, env):
    import params
    Execute('source ~/.bashrc ; sqcheck -f -c dcs',user=params.traf_user)

if __name__ == "__main__":
  DCS().execute()

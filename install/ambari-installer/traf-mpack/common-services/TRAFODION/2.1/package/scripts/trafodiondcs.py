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
    return True

  def start(self, env):
    return True
	
  def status(self, env):
    import params
    Execute('sqcheck -f -c dcs',user=params.traf_user)

if __name__ == "__main__":
  DCS().execute()

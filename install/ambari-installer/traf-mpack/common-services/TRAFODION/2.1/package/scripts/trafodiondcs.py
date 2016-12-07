# @@@ START COPYRIGHT @@@
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# @@@ END COPYRIGHT @@@
import sys, os, pwd, signal, time
from resource_management import *

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

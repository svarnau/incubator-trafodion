<!--
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
 -->

## Trafodion Installers

* **install** - This is the current command-line installer. It installs a server tarball
  on an existing CDH or HDP Hadoop cluster.
* **python-installer** - This is the new command-line installer, meant to replace current
  command-line installer. Likewise, installs server tarball on existing CDH, HDP,
  or APACHE cluster.
* **ambari-installer** - This integrates with Ambari cluster manager, so only applies to HDP.
  In this case, trafodion server is installed via RPM. This is installed on Ambari server as
  a management pack. Trafodion can be included in the initial cluster creation or added later.

## Ambari Integration

The Ambari MPack (management pack) is also packaged as an RPM, having a dependency on ambari-server.
Given a proper yum repo file, `traf_ambari` rpm
can be installed directly and it pulls in ambari-server.

#### Packaging

Part of Ambari's job is to set up yum repo files on each node in order to install packages.
The default URLs are for Hortonworks' public repos. But since your custom-built Trafodion is
not hosted there, you need to specify a URL for your local yum repo server. To build that into
the `traf_ambari` package, use make to specify value of `REPO_URL`.

   `make all REPO_URL=http://my.repo.server/repo/...`

This can be done either in the install directory or from a top-level "make package-all".
This is not necessarily the URL where `traf_ambari` is hosted, but rather where the
`apache-trafodion_server` is hosted.

#### Hosting RPM Repo

Once you build the RPM packages, you need to copy them to a web server accessible location and
then use createrepo command to set up the yum meta-data. (sudo yum install createrepo)

#### Source Files

The code for the ambari mpack is here in the install tree, but files that are distributed to each
node are part of the trafodion server RPM, and are located in core/sqf/sysinstall

#### Trafodion Environment Variables

The trafodion user environment is set using ~trafodion/.bashrc, which sources in values set by the RPM
installation, values set by the Ambari install, and values from the installed Trafodion software.

* `/etc/trafodion/trafodion_config` - RPM sets the `SQ_HOME` value, which is location of Trafodion installation.
* `/etc/trafodion/conf/trafodion-env.sh` - user-specified values set by Ambari trafodion-node install step.
* `/etc/trafodion/conf/traf-cluster-env.sh` - node list info set by Ambari install trafodion-master step.
* `/home/trafodion/.../sqenv.sh` - various derived values.


#!/bin/bash

# generate new unique key local to ambari server
tf=/tmp/trafssh.$$
rm -f ${tf}*
/usr/bin/ssh-keygen -q -t rsa -N '' -f $tf

instloc="$1"

config="${instloc}/traf-mpack/common-services/TRAFODION/2.1/configuration/trafodion-env.xml"

chmod 0600 $config  # protect key
sed -i -e "/TRAFODION-GENERATED-SSH-KEY/r $tf" $config # add key to config properties

rm -f ${tf}*

# tar up the mpack, included generated key
tball="${instloc}/traf-mpack.tar.gz"

cd "${instloc}"
tar czf "$tball" traf-mpack

# install ambari mpack
ambari-server install-mpack --verbose --mpack="$tball"
ret=$?

# HACK until Ambari 2.4.2 available -- update stack repo file
for v in 2.3 2.4 2.5
do
  sed -i -e "/redhat6/r ${instloc}/mpack-install/repo" /var/lib/ambari-server/resources/stacks/HDP/$v/repos/repoinfo.xml
done

exit $ret

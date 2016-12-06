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

exit $ret

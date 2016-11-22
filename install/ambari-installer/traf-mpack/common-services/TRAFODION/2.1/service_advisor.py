#!/usr/bin/env ambari-python-wrap
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import imp
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STACKS_DIR = os.path.join(SCRIPT_DIR, '../../../../../stacks/')
PARENT_FILE = os.path.join(STACKS_DIR, 'service_advisor.py')

try:
  with open(PARENT_FILE, 'rb') as fp:
    service_advisor = imp.load_module('service_advisor', fp, PARENT_FILE, ('.py', 'rb', imp.PY_SOURCE))
except Exception as e:
  traceback.print_exc()
  print "Failed to load parent"

class TRAFODION21ServiceAdvisor(service_advisor.DefaultStackAdvisor):
 
  def colocateService(self, hostsComponentsMap, serviceComponents):
    # Co-locate TRAF_NODE with HBase REGIONSERVERS, if no hosts allocated
    traf_node = [component for component in serviceComponents if component["StackServiceComponents"]["component_name"] == "TRAF_NODE"][0]
    if not self.isComponentHostsPopulated(traf_node):
      for hostName in hostsComponentsMap.keys():
        hostComponents = hostsComponentsMap[hostName]
        if {"name": "HBASE_REGIONSERVER"} in hostComponents and {"name": "TRAF_NODE"} not in hostComponents:
          hostsComponentsMap[hostName].append( { "name": "TRAF_NODE" } )
        if {"name": "HBASE_REGIONSERVER"} not in hostComponents and {"name": "TRAF_NODE"} in hostComponents:
          hostComponents.remove({"name": "TRAF_NODE"})

    # Place TRAF_DCS_SECOND on different nodes from TRAF_DCS_PRIME
    dcsS = [component for component in serviceComponents if component["StackServiceComponents"]["component_name"] == "TRAF_DCS_SECOND"][0]
    if not self.isComponentHostsPopulated(dcsS):
      placed = False
      for hostName in hostsComponentsMap.keys():
         hostComponents = hostsComponentsMap[hostName]
         if {"name": "TRAF_DCS_PRIME"} in hostComponents and {"name": "TRAF_DCS_SECOND"} in hostComponents:
            hostComponents.remove({"name": "TRAF_DCS_SECOND"})
         if {"name": "TRAF_DCS_PRIME"} not in hostComponents and not placed:
            hostsComponentsMap[hostName].append( { "name": "TRAF_DCS_SECOND" } )
            placed = True

 
  def getServiceComponentLayoutValidations(self, services, hosts):
    componentsListList = [service["components"] for service in services["services"]]
    componentsList = [item["StackServiceComponents"] for sublist in componentsListList for item in sublist]

    trafNodeHosts = self.getHosts(componentsList, "TRAF_NODE")
    regionHosts = self.getHosts(componentsList, "HBASE_REGIONSERVER")
    hiveHosts = self.getHosts(componentsList, "HIVE_CLIENT")
    dataHosts = self.getHosts(componentsList, "DATANODE")

    items = []

    # Generate WARNING if any TRAF_NODE is not colocated with a DATANODE
    mismatchHosts = sorted(set(trafNodeHosts).symmetric_difference(set(dataHosts)))
    if len(mismatchHosts) > 0:
      hostsString = ', '.join(mismatchHosts)
      message = "Trafodion Nodes should be installed on all HDFS Data Nodes. " \
                "{0} host(s) do not satisfy the colocation recommendation: {1}".format(len(mismatchHosts), hostsString)
      items.append( { "type": 'host-component', "level": 'WARN', "message": message, "component-name": 'TRAF_NODE' } )

    # Generate WARNING if any TRAF_NODE is not colocated with a HBASE_REGIONSERVER
    mismatchHosts = sorted(set(trafNodeHosts).symmetric_difference(set(regionHosts)))
    if len(mismatchHosts) > 0:
      hostsString = ', '.join(mismatchHosts)
      message = "Trafodion Nodes should be installed on all HBase Region Servers. " \
                "{0} host(s) do not satisfy the colocation recommendation: {1}".format(len(mismatchHosts), hostsString)
      items.append( { "type": 'host-component', "level": 'WARN', "message": message, "component-name": 'TRAF_NODE' } )

    # Generate WARNING if any TRAF_NODE is not colocated with a HIVE_CLIENT
    mismatchHosts = sorted(set(trafNodeHosts).difference(set(hiveHosts)))
    if len(mismatchHosts) > 0:
      hostsString = ', '.join(mismatchHosts)
      message = "Hive Client should be installed on all Trafodion Nodes. " \
                "{0} host(s) do not satisfy recommendation: {1}".format(len(mismatchHosts), hostsString)
      items.append( { "type": 'host-component', "level": 'WARN', "message": message, "component-name": 'TRAF_NODE' } )

    return items
 
  def getServiceConfigurationRecommendations(self, configurations, clusterSummary, services, hosts):
    # Update HBASE properties in hbase-site
    if "hbase-site" in services["configurations"]:
      hbase_site = services["configurations"]["hbase-site"]["properties"]
      putHbaseSiteProperty = self.putProperty(configurations, "hbase-site", services)

      for property, desired_value in self.getHbaseSiteDesiredValues().iteritems():
        if property not in hbase_site or hbase_site[property] != desired_value:
          putHbaseSiteProperty(property, desired_value)

   # Update HDFS properties in hdfs-site
    if "hdfs-site" in services["configurations"]:
      hdfs_site = services["configurations"]["hdfs-site"]["properties"]
      putHdfsSiteProperty = self.putProperty(configurations, "hdfs-site", services)

      for property, desired_value in self.getHdfsSiteDesiredValues().iteritems():
        if property not in hdfs_site or hdfs_site[property] != desired_value:
          putHdfsSiteProperty(property, desired_value)

    # Update ZOOKEEPER properties in zoo.cfg
    if "zoo.cfg" in services["configurations"]:
      zoo_cfg = services["configurations"]["zoo.cfg"]["properties"]
      putZooCfgProperty = self.putProperty(configurations, "zoo.cfg", services)

      for property, desired_value in self.getZooCfgDesiredValues().iteritems():
        if property not in zoo_cfg or zoo_cfg[property] != desired_value:
          putZooCfgProperty(property, desired_value)

 
  def getServiceConfigurationsValidationItems(self, configurations, recommendedDefaults, services, hosts):
    items = []

    val_items = []
    cfg = configurations["hbase-site"]["properties"]
    for property, desired_value in self.getHbaseSiteDesiredValues().iteritems():
       if property not in cfg or cfg[property] != desired_value:
          message = "Trafodion recommends value of " + desired_value
          val_items.append({"config-name": property, "item": self.getWarnItem(message)})
    items.extend(self.toConfigurationValidationProblems(val_items, "hbase-site"))

    val_items = []
    cfg = configurations["hdfs-site"]["properties"]
    for property, desired_value in self.getHdfsSiteDesiredValues().iteritems():
       if property not in cfg or cfg[property] != desired_value:
          message = "Trafodion recommends value of " + desired_value
          val_items.append({"config-name": property, "item": self.getWarnItem(message)})
    items.extend(self.toConfigurationValidationProblems(val_items, "hdfs-site"))

    val_items = []
    cfg = configurations["zoo.cfg"]["properties"]
    for property, desired_value in self.getZooCfgDesiredValues().iteritems():
       if property not in cfg or cfg[property] != desired_value:
          message = "Trafodion recommends value of " + desired_value
          val_items.append({"config-name": property, "item": self.getWarnItem(message)})
    items.extend(self.toConfigurationValidationProblems(val_items, "zoo.cfg"))

    return items

##### Desired values in other service configs
  def getHbaseSiteDesiredValues(self):
    desired = {
        "hbase.master.distributed.log.splitting": "false",
        "hbase.snapshot.master.timeoutMillis": "600000",
        "hbase.coprocessor.region.classes": "org.apache.hadoop.hbase.coprocessor.transactional.TrxRegionObserver,org.apache.hadoop.hbase.coprocessor.transactional.TrxRegionEndpoint,org.apache.hadoop.hbase.coprocessor.AggregateImplementation",
        "hbase.hregion.impl": "org.apache.hadoop.hbase.regionserver.transactional.TransactionalRegion",
        "hbase.regionserver.region.split.policy": "org.apache.hadoop.hbase.regionserver.ConstantSizeRegionSplitPolicy",
        "hbase.snapshot.enabled": "true",
        "hbase.bulkload.staging.dir": "/hbase-staging",
        "hbase.regionserver.region.transactional.tlog": "true",
        "hbase.snapshot.region.timeout": "600000",
        "hbase.client.scanner.timeout.period": "600000"
    }
    return desired

  def getHdfsSiteDesiredValues(self):
    desired = {
        "dfs.namenode.acls.enabled": "true"
    }
    return desired

  def getZooCfgDesiredValues(self):
    desired = {
        "maxClientCnxns": "0"
    }
    return desired

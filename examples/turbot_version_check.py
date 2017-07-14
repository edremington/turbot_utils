#!/usr/bin/env python

import turbotutils
import turbotutils.cluster
import turbotutils.guardrails
import turbotutils.get_turbot
import sys

turbot_host_certificate_verification = True

# Set to your Turbot Host URL
turbot_host = turbotutils.get_turbot_host()

# Get the access and secret key pairs
(turbot_api_access_key, turbot_api_secret_key) = turbotutils.get_turbot_access_keys()
urn_format = turbotutils.cluster.get_cluster_id(turbot_host, turbot_api_access_key, turbot_api_secret_key, turbot_host_certificate_verification)

source_account_urn = urn_format
version=turbotutils.get_turbot.version(turbot_api_access_key, turbot_api_secret_key,turbot_host_certificate_verification,turbot_host,urn_format )
#
# this try will verify that the turbot version is acceptable to us based on the "known_versions" list. the 2nd element is there just for 
# show at this point if the returned 'version' is not in the list we will exit due to an exception.
try:
    known_versions = ['1.7.3','1.74']
    goodVer=known_versions.index(version)
except:
    print("Sorry %s is not an approved turbot version" % version)
    sys.exit(1)
    
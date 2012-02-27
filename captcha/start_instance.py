#!/usr/bin/env python


import sys

argc = len(sys.argv)
if argc != 2:
    print("supply an AMI ID")
    sys.exit(1)
    
ami_id = sys.argv[1]

import time
import ConfigParser
from boto.ec2.connection import EC2Connection
import subprocess

config_file = "%s/credentials.cfg" % sys.path[0]

config = ConfigParser.RawConfigParser()
config.read(config_file)

access_key = config.get("credentials", "access_key")
secret_key = config.get("credentials", "secret_key")

conn = EC2Connection(access_key, secret_key)

reservation = conn.run_instances(ami_id,
    key_name='bioc-default',
    instance_type='t1.micro',
    security_groups=['rstudio-only'])
    
instance = reservation.instances[0]

instance.add_tag("Name", "tryitnow")

ip = None


while True:
        desc = conn.get_all_instances([instance.id])
        if desc[0].instances[0].state == "running":
            ip = desc[0].instances[0].public_dns_name
            break
        time.sleep(1)


print("got ip: %s" % ip)

url = "http://%s:8787/auth-public-key" % ip
print("url = %s" % url)
#curl -m 1 --retry 200 --retry-dela-178.compute-1.amazonaws.com:8787/auth-public-key

while True:
    print("attempt...")
    proc = subprocess.Popen(["curl",  "-m", "1",  "--retry", "200", "--retry-delay", "1", url], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    print "program output:", out
        
auth = out.strip()
print ("%s;%s" % (ip, auth))


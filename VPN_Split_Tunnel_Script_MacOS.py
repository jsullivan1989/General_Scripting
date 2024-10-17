#! /usr/bin/env python3

''' General Python 3 script to run on MacOS by parsing netstat when split tunneling a remote access VPN.
This is assuming the remote access VPN hands out a higher priority default route than the home office gateway.
Run this script after connecting, and add as many routes to internal networks as necessary.  Routes to RFC1918 have been included
as an example to point over the utun interface. 

The tag <Home_Wi-Fi_Gateway> will be the gateway IP address on your home router.  Modify according to local subnet.'''

import os
import subprocess
import re

# Collect output of MacOS route table with netstat using subprocess

full_rt = subprocess.run(['netstat', '-nr'], capture_output=True, text=True)

# Separate the route entries into lines

route_entries = full_rt.stdout.splitlines()


# Instantiate default routes container, will have one pointing to VPN and one pointing to Home Wi-Fi Gateway.  May have IPv6 as well 

default_routes = []

# Collecting all default routes into a list

for line in route_entries:
    if 'default' in line:
        default_routes.append(line)


# Active route will be the first in the list and point over the utun interface

tunnel_default_route = default_routes[0]

# This tunnel default route is of type string.  Separate into an iterable list, so that we can grab the tunnel interface out of the last (fourth index)

tunnel_default_route_list = tunnel_default_route.split()


# Create tunnel interface variable to use as static route next-hop interface in below entries

tunnel_interface = tunnel_default_route_list[3]

# View your tunnel interface (optional)

print(tunnel_interface)

# Delete default route pointing to tunnel interface

os.system("sudo route delete -net 0.0.0.0 -ifp " + tunnel_interface)

# add default route to Wi-Fi Gateway, change if not at home

os.system("sudo route add -net 0.0.0.0/0 <Home_Wi-Fi_Gateway>")

# Add internal remote access routes as needed to point to tunnel interface.  Below lists three RFC1918 addresses, but there will probably be more if company has ARIN assigned and protected public IP addresses.

os.system("sudo route add -net 10.0.0.0/8 -interface " + tunnel_interface)
os.system("sudo route add -net 192.168.0.0/16 -interface " + tunnel_interface)
os.system("sudo route add -net 172.16.0.0/12 -interface " + tunnel_interface)

# Add more internal routes as needed ...

#!/bin/bash

#######################
###      INPUT      ###
#######################

if [[ $# != 1 ]]; then
	echo "Usage: $0 <ip>"
	echo -e "\tip: controller ip"
	exit 1
fi



#######################
###    Variables    ###
#######################

controller_ip=$1



#######################
###  Factory state  ###
#######################

iptables -F
iptables -F -t nat
iptables -F -t mangle
iptables -X

# FILTER
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

# NAT
iptables -t nat -P PREROUTING ACCEPT
iptables -t nat -P INPUT ACCEPT
iptables -t nat -P OUTPUT ACCEPT
iptables -t nat -P POSTROUTING ACCEPT

# MANGLE
iptables -t mangle -P PREROUTING ACCEPT
iptables -t mangle -P INPUT ACCEPT
iptables -t mangle -P FORWARD ACCEPT
iptables -t mangle -P OUTPUT ACCEPT
iptables -t mangle -P POSTROUTING ACCEPT



######################
###    FIREWALL    ###
######################

iptables -A INPUT -t filter -i lo -j ACCEPT # Accept local traffic
iptables -A INPUT -t filter -p tcp -m state --state ESTABLISHED,RELATED -j ACCEPT # Accept established connections
iptables -A INPUT -t filter -s ${controller_ip} -j ACCEPT # Accept controller traffic
iptables -A INPUT -t filter -p tcp --dport 22 # Accept attackers connections
iptables -A INPUT -t filter -p udp -i wg-srv --sport 1024:65535 --dport 53 -m state --state NEW,ESTABLISHED -j ACCEPT # Accept DNS requests
iptables -A INPUT -t filter -p udp --sport 53 --dport 1024:65535 -m state --state ESTABLISHED -j ACCEPT # Accept the answers to DNS requests
iptables -A INPUT -t filter -p icmp -m state --state ESTABLISHED -j ACCEPT # Accept ping replies
iptables -t filter -P INPUT DROP # Drop everything else

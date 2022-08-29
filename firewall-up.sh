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

iptables -A PREROUTING -t mangle -i lo -j ACCEPT # Accept local traffic
iptables -A PREROUTING -t mangle -p tcp	-m state --state ESTABLISHED,RELATED -j ACCEPT # Accept established connections
iptables -A PREROUTING -t mangle -s $controller_ip -j ACCEPT # Accept controller traffic
iptables -A PREROUTING -t mangle -p tcp --dport 22 -j ACCEPT # Accept attackers connections
iptables -t mangle -P PREROUTING DROP # Drop everything else

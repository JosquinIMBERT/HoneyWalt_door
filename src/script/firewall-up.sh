#!/bin/bash

#######################
###      INPUT      ###
#######################

if [[ $# -le 0 || $# -gt 2 ]]; then
	echo "Usage: $0 <ctrl_ip> [ips]"
	echo -e "\tctrl_ip: controller ip"
	echo -e "\tips: ip white list (coma separated list)"
	exit 1
fi



#######################
###    Variables    ###
#######################

controller_ip=$1
white_list=${controller_ip} # White list contains at least the controller IP
if [[ $# -eq 2 && ! -z ${2} ]]; then
	white_list=$(echo ${white_list},${2}) # Add other white list IPs
fi



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

iptables -A PREROUTING -t nat -i eth0 -p tcp --dport 22 -j REDIRECT --to-port 2222 # Cowrie traffic will be redirected to port 2222
iptables -A INPUT -t filter -i lo -j ACCEPT # Accept local traffic
iptables -A INPUT -t filter -p tcp -m state --state ESTABLISHED,RELATED -j ACCEPT # Accept established connections
iptables -A INPUT -t filter -s ${white_list} -j ACCEPT # Accept controller traffic
iptables -A INPUT -t filter -p tcp --dport 22 # Accept attackers connections
iptables -A INPUT -t filter -p udp -i wg-srv --sport 1024:65535 --dport 53 -m state --state NEW,ESTABLISHED -j ACCEPT # Accept DNS requests
iptables -A INPUT -t filter -p udp --sport 53 --dport 1024:65535 -m state --state ESTABLISHED -j ACCEPT # Accept DNS replies
iptables -A INPUT -t filter -p icmp -m state --state ESTABLISHED -j ACCEPT # Accept ping replies
iptables -t filter -P INPUT DROP # Drop everything else

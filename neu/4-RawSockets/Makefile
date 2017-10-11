all: rawhttpget
	chmod 777 rawhttpget
	iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP
	ethtool --offload eth0 rx off tx off
	ethtool -K eth0 gso off
	ethtool -K eth0 gro off
/interface wireguard
add name=wg0 listen-port=51820 private-key="REPLACE_WITH_WG_PRIV_KEY"
/ip address
add address=10.0.0.1/16 interface=wg0
/ip pool
set [find name=default] ranges=10.0.0.10-10.0.255.254
/ip firewall filter
add chain=input protocol=udp dst-port=51820 action=accept comment="Allow WireGuard"
/ip firewall nat
add chain=srcnat out-interface=ether1 src-address=10.0.0.0/16 action=masquerade

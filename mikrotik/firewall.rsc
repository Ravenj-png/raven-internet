/ip firewall filter
add chain=input connection-state=invalid action=drop
add chain=forward connection-state=invalid action=drop
add chain=forward dst-port=3333,4444,8080,1080,3128 protocol=tcp action=drop comment="Block mining/proxy"

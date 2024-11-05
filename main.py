#/usr/bin/python3
# alvessh - 2024-11-05

import requests
import ipaddress

url = "https://www.gstatic.com/ipranges/cloud.json"

scope_filter = "us-central1"

output_file = "all_ips.txt"

with open(output_file, "w") as f:
    pass

response = requests.get(url)
data = response.json()

for prefix in data['prefixes']:
    if prefix.get('scope') == scope_filter:
        ip_prefix = prefix.get('ipv4Prefix')
        if ip_prefix:
            try:
                network = ipaddress.ip_network(ip_prefix, strict=False)
                with open(output_file, "a") as f:
                    for ip in network.hosts():
                        f.write(str(ip) + "\n")
            except ValueError as e:
                print(f"Erro ao processar o range {ip_prefix}: {e}")

print(f"Todos os IPs foram salvos em {output_file}.")
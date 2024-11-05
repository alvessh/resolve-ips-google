#!/usr/bin/python3
# alvessh - 2024-11-05

import requests
import ipaddress
import argparse
import shutil
import os
import sys
import socket

if os.geteuid() != 0:
    print("Este script precisa ser executado com permissões de superusuário. Use 'sudo main.py {scope} {domain_file.txt}'.")
    sys.exit(1)

parser = argparse.ArgumentParser(description="Filtra IPs por escopo e salva em arquivo.")
parser.add_argument("scope", type=str, help="Scope desejado para filtrar IPs (exemplo: us-central1)")
parser.add_argument("domains_file", type=str, help="Caminho da lista de dominios (exemplo: domains.txt)")
args = parser.parse_args()

url = "https://www.gstatic.com/ipranges/cloud.json"

output_file = "all_ips.txt"
domains_file = args.domains_file

dnsmasq_conf_file = "/etc/dnsmasq.d/custom.conf"
backup_dnsmasq_conf_file = "/etc/dnsmasq.d/custom.conf.backup"

try:
    shutil.copy(dnsmasq_conf_file, backup_dnsmasq_conf_file)
    print(f"Backup do arquivo dnsmasq.conf criado em {backup_dnsmasq_conf_file}")
except IOError as e:
    print(f"Erro ao criar backup de {dnsmasq_conf_file}: {e}")
    exit(1)

with open(output_file, "w") as f:
    pass

try:
    with open(domains_file, "r") as df:
        hostnames = [line.strip() for line in df if line.strip()]
except FileNotFoundError:
    print(f"Erro: O arquivo '{domains_file}' não foi encontrado.")
    exit(1)

response = requests.get(url)
data = response.json()

# Escreve IPs e nomes de domínio no arquivo dnsmasq
with open(dnsmasq_conf_file, "w") as dnsmasq_conf:
    for prefix in data['prefixes']:
        if prefix.get('scope') == args.scope:
            ip_prefix = prefix.get('ipv4Prefix')
            if ip_prefix:
                try:
                    network = ipaddress.ip_network(ip_prefix, strict=False)
                    for ip in network.hosts():
                        for hostname in hostnames:
                            dnsmasq_conf.write(f"address=/{hostname}/{ip}\n")
                            print(f"Adicionando {ip} para {hostname} no dnsmasq.")
                except ValueError as e:
                    print(f"Erro ao processar o range {ip_prefix}: {e}")

print(f"Todas as configurações de DNS foram salvas em {dnsmasq_conf_file}.")
print("Lembre-se de reiniciar o dnsmasq para aplicar as novas configurações.")

def resolve_and_request(domain):
    try:
        ip = socket.gethostbyname(domain)
        print(f"IP resolvido para {domain}: {ip}")
        
        try:
            response = requests.get(f"https://{domain}", timeout=0.001)
            print(f"Resposta recebida de {domain}: {response.status_code}")
        except requests.Timeout:
            print(f"Timeout ao tentar conectar a {domain}")
    except socket.gaierror:
        print(f"Erro ao resolver o domínio: {domain}")

for domain in hostnames:
    resolve_and_request(domain)
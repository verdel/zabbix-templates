# Zabbix template for Squid proxy monitoring


## Installation

- Import **'Template Squid proxy with auth.xml'** template into Zabbix

- Add script **'squid_zabbix_monitoring.py'** into the externalscripts directory on Zabbix Server or Zabbix Proxy

- Copy **'requirements.txt'** file to the temporary directory on Zabbix Server or Zabbix Proxy

- Install python script requirements with `pip install -f requirements.txt` command
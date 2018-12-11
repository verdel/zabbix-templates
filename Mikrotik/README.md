# Zabbix template for Mikrotik CAP Wi-Fi client

The template uses the LLD script for auto discovery of Wi-Fi clients.

It uses the value of the comment field in the dhcp server lease section as the client name if it is populated.



## Installation

- Import **'Template Mikrotik CAP Wi-Fi Clients.xml'** template into Zabbix

- Add script **'getAPClient.py'** into the externalscripts directory on Zabbix Server or Zabbix Proxy

- Copy **'requirements.txt'** file to the temporary directory on Zabbix Server or Zabbix Proxy

- Install python script requirements with `pip install -f requirements.txt` command

- Set **'{$ROS_USERNAME}'** and **'{$ROS_PASSWORD}'** macros in the host settings on Zabbix

- Enable API on Mikrotik CAP


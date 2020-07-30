# Zabbix template for check the status or expiration date of ssl certificate


## Installation

- Import **'Template SSL Cert Check External.xml'** template into Zabbix

- Add script **'ssl-check-cert.py'** into the externalscripts directory on Zabbix Server or Zabbix Proxy

- Set **'{$SSL_PORT}'** macros in the host settings on Zabbix
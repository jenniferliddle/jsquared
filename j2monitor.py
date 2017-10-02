'''
j2monitor.py

Jenifer Liddle <jennifer@jsquared.co.uk>

This is a bit Heath-Robinson, but the way this works is:
jtwo.org sends an email to jsquared.co.uk
This code then ckecks syslog for the email to extract the IP address.
It then checks it against a stored copy of the IP address to see
if it has changed.
If it has, it sends an email and uses the Mythic Beasts API to update
the DNS entries for jtwo.org and hydranet.co.uk
'''
import smtplib
import sys
import re
import subprocess
import urllib
import urllib2

''' Send email to j2@jsquared.co.uk with new IP address'''
def sendMail(newip):
	s = smtplib.SMTP('localhost')
	msg = "Subject: New IP address for jtwo\nIP address for jtwo is: "+newip
	s.sendmail("sentry@jsquared.co.uk",["j2@jsquared.co.uk"],msg)

''' Update single DNS record '''
def updateDNS(values):
	url = 'https://dnsapi.mythic-beasts.com/'
	data = urllib.urlencode(values)
	req = urllib2.Request(url, data)
	response = urllib2.urlopen(req)

''' Update DNS records for jtwo.org and hydranet.co.uk
using the Mythic Beasts API
'''
def updateAllDNS(newip, password):
	values = {'domain'   : 'jtwo.org', 'password' : password, 'command'  : 'REPLACE @ 86400 A '+newip }
	updateDNS(values)

	values = {'domain'   : 'jtwo.org', 'password' : password, 'command'  : 'REPLACE www 86400 A '+newip }
	updateDNS(values)

	values = {'domain'   : 'hydranet.co.uk', 'password' : password, 'command'  : 'REPLACE @ 86400 A '+newip }
	updateDNS(values)

	values = {'domain'   : 'hydranet.co.uk', 'password' : password, 'command'  : 'REPLACE www 86400 A '+newip }
	updateDNS(values)

	values = {'domain'   : 'hydranet.co.uk', 'password' : password, 'command'  : 'REPLACE dev 86400 A '+newip }
	updateDNS(values)

''' 
Parse syslog to extract the IP address of jtwo.org, and see if it has changed
'''
password = sys.argv[1]
txt = subprocess.check_output(["tail","-500","/var/log/syslog"])
m=re.search('\n.*root@jtwo.*\n(.*)\n',txt)
if (m and len(m.groups()) > 0):
	x = m.group(1)
	m=re.search("net\[(.*)\]",x)
	if (m and len(m.groups()) > 0):
		n = len(m.groups())
		newip = m.group(n)
		oldip = subprocess.check_output(["cat","/etc/jtwo_ip"])
		if (oldip != newip):
			sendMail(newip)
			updateAllDNS(newip,password)
			f = open("/etc/jtwo_ip","w")
			f.write(newip)
			f.close()




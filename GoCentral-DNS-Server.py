# Original sudomemoDNS v1.0
# (c) 2019 Austin Burk/Sudomemo
# All rights reserved

# Based on RiiConnect24 DNS Server v1.2
# Created by Austin Burk/Sudomemo. Edited by KcrPL and Larsenv.

# GoCentral DNS Server v2.0
# Created by Austin Burk/Sudomemo. Modified for GoCentral by qfoxb

from datetime import datetime
from time import sleep

from dnslib import DNSLabel, QTYPE, RD, RR
from dnslib import A, AAAA, CNAME, MX, NS, SOA, TXT
from dnslib.server import DNSServer

import socket
import requests
import json
import sys
import re

def get_platform():
    platforms = {
        'linux1' : 'Linux',
        'linux2' : 'Linux',
        'darwin' : 'OS X',
        'win32' : 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform

    return platforms[sys.platform]

def query_yes_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)
    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")

GOCENTRALDNS_VERSION = "2.0"
CROSSPLAY = False
SAFEMODE = True
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))
get_zones = requests.get("https://raw.githubusercontent.com/qfoxb/GoCentral-DNS/master/dns_zones.json")
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

EPOCH = datetime(1970, 1, 1)
SERIAL = int((datetime.utcnow() - EPOCH).total_seconds())
MY_IP = get_ip()

print("+===============================+")
print("|      GoCentral DNS Server     |")
print("|          Version " + GOCENTRALDNS_VERSION + "          |")
print("+===============================+\n")
print("Hello! This server will allow you to connect to GoCentral when your Internet Service Provider does not work with custom DNS.")
print("\nHere are the DNS settings you need to type in on your PlayStation 3/Wii in the DNS section:\n")
print(":---------------------------:")
print("  Primary DNS:  ",MY_IP  )
print("  Secondary DNS: 1.1.1.1")
print(":---------------------------:")
print("#### Getting Help ####\n")
print("Need help? Open a GitHub issue.\n")
#if query_yes_no("Would you like to enable PS3 and Wii Crossplay?"):
#    prGreen("Enabling crossplay!")
#    CROSSPLAY = True
#    crossplay_zones = requests.get("https://raw.githubusercontent.com/qfoxb/GoCentral-DNS/master/dns_zones_crossplay.json")

print("--- Starting up ---")

TYPE_LOOKUP = {
    A: QTYPE.A,
    AAAA: QTYPE.AAAA,
    CNAME: QTYPE.CNAME,
    MX: QTYPE.MX,
    NS: QTYPE.NS,
    SOA: QTYPE.SOA,
    TXT: QTYPE.TXT,
}

# Can't seem to turn off DNSLogger with a None type so let's just null it out with a dummy function

class RiiConnect24DNSLogger(object):
    def log_recv(self, handler, data):
        pass
    def log_send(self, handler, data):
        pass
    def log_request(self, handler, request):
        print("[DNS] {" + datetime.now().strftime('%H:%M:%S') + "} Received: DNS Request from: " + handler.client_address[0])
    def log_reply(self, handler, reply):
        print("[DNS] {" + datetime.now().strftime('%H:%M:%S') + "} Sent    : DNS Response to:  " + handler.client_address[0])
    def log_error(self, handler, e):
        prRed("[INFO] {" + datetime.now().strftime('%H:%M:%S') + "} Invalid DNS request from " + handler.client_address[0])
    def log_truncated(self, handler, reply):
        pass
    def log_data(self, dnsobj):
        pass


class Record:
    def __init__(self, rdata_type, *args, rtype=None, rname=None, ttl=None, **kwargs):
        if isinstance(rdata_type, RD):
            # actually an instance, not a type
            self._rtype = TYPE_LOOKUP[rdata_type.__class__]
            rdata = rdata_type
        else:
            self._rtype = TYPE_LOOKUP[rdata_type]
            if rdata_type == SOA and len(args) == 2:
                # add sensible times to SOA
                args += ((
                    SERIAL,  # serial number
                    60 * 60 * 1,  # refresh
                    60 * 60 * 3,  # retry
                    60 * 60 * 24,  # expire
                    60 * 60 * 1,  # minimum
                ),)
            rdata = rdata_type(*args)

        if rtype:
            self._rtype = rtype
        self._rname = rname
        self.kwargs = dict(
            rdata=rdata,
            ttl=self.sensible_ttl() if ttl is None else ttl,
            **kwargs,
        )

    def try_rr(self, q):
        if q.qtype == QTYPE.ANY or q.qtype == self._rtype:
            return self.as_rr(q.qname)

    def as_rr(self, alt_rname):
        return RR(rname=self._rname or alt_rname, rtype=self._rtype, **self.kwargs)

    def sensible_ttl(self):
        if self._rtype in (QTYPE.NS, QTYPE.SOA):
            return 60 * 60 * 24
        else:
            return 300

    @property
    def is_soa(self):
        return self._rtype == QTYPE.SOA

    def __str__(self):
        return '{} {}'.format(QTYPE[self._rtype], self.kwargs)


ZONES = {}

try:
  get_zones = requests.get("https://raw.githubusercontent.com/qfoxb/GoCentral-DNS/master/dns_zones.json")
  motd = requests.get("https://raw.githubusercontent.com/qfoxb/GoCentral-DNS/master/motd")
  versioncheck = requests.get("https://raw.githubusercontent.com/qfoxb/GoCentral-DNS/master/latest.version")
  specified_domains = requests.get("https://raw.githubusercontent.com/qfoxb/GoCentral-DNS/master/specified_domains")
except requests.exceptions.Timeout:
  print("[ERROR] Couldn't load DNS data: connection to GitHub timed out.")
  print("[ERROR] Are you connected to the Internet?")
except requests.exceptions.RequestException as e:
  print("[ERROR] Couldn't load DNS data.")
  print("[ERROR] Exception: ",e)
  sys.exit(1)
try:
        zones = json.loads(get_zones.text)
except ValueError as e:
  print("[ERROR] Couldn't load DNS data: invalid response from server")

for zone in zones:
  if zone["type"] == "a":
    ZONES[zone["name"]] = [ Record(A, zone["value"]) ]
  elif zone["type"] == "p":
    ZONES[zone["name"]] = [ Record(A, socket.gethostbyname(zone["value"])) ]
#with open(specified_domains) as file:
 #   specified_domains = [line.strip() for line in file]

print("[INFO] DNS information has been downloaded successfully.")

class Resolver:
    def __init__(self):
        self.zones = {DNSLabel(k): v for k, v in ZONES.items()}
        self.blocked_domains_log = "blocked_domains.txt"  # Specify the path to the log file

    def log_blocked_domain(self, domain):
        with open(self.blocked_domains_log, 'a') as log_file:
            log_file.write(f"{domain}\n")

    def resolve(self, request, handler):
        reply = request.reply()
        zone = self.zones.get(request.q.qname)
        if zone is not None:
            print(request.q.qname)
            for zone_records in zone:
                rr = zone_records.try_rr(request.q)
                rr and reply.add_answer(rr)
        else:
            # no direct zone so look for an SOA record for a higher level zone
            found = False
            print(request.q.qname)
            for zone_label, zone_records in self.zones.items():
                if request.q.qname.matchSuffix(zone_label):
                    try:
                        soa_record = next(r for r in zone_records if r.is_soa)
                    except StopIteration:
                        continue
                    else:
                        reply.add_answer(soa_record.as_rr(zone_label))
                        found = True
                        break
            if not found:
                domain = str(request.q.qname)
                if SAFEMODE and not any(domain.endswith(str(specified_domain)) for specified_domain in specified_domains):
                    # Log blocked domain to file
                    self.log_blocked_domain(domain)
                    return None  # Don't return anything if not in specified domains
                try:
                    if "hmxservices.com" in domain:
                        reply.add_answer(RR(domain, QTYPE.A, rdata=A("78.141.231.152"), ttl=60))
                    else:
                        ip_address = socket.gethostbyname_ex(domain)[2][0]
                        reply.add_answer(RR(domain, QTYPE.A, rdata=A(ip_address), ttl=60))
                except socket.gaierror as e:
                    prRed(f"[ERROR] Failed to resolve IP for {domain}: {e}")
                    # You can choose to log or handle the error as needed

        return reply
resolver = Resolver()
dnsLogger = RiiConnect24DNSLogger()

print("[INFO] Detected operating system:", get_platform());

if get_platform() == 'linux':
  print("[INFO] Please note that you will have to run this as root or with permissions to bind to UDP port 53.")
  print("[INFO] If you aren't seeing any requests, check that this is the case first with lsof -i:53 (requires lsof)")
  print("[INFO] To run as root, prefix the command with 'sudo'")
elif get_platform() == 'OS X':
  print("[INFO] Please note that you will have to run this as root or with permissions to bind to UDP port 53.")
  print("[INFO] If you aren't seeing any requests, check that this is the case first with lsof -i:53 (requires lsof)")
  print("[INFO] To run as root, prefix the command with 'sudo'")
elif get_platform() == 'Windows':
  print("[INFO] Please note: If you see a notification about firewall, allow the application to work. If you're using 3rd party  firewall on your computer you may want to allow this program to your firewall and allow traffic.")

try:
  servers = [
    DNSServer(resolver=resolver, port=53, address=MY_IP, tcp=True, logger=dnsLogger),
    DNSServer(resolver=resolver, port=53, address=MY_IP, tcp=False, logger=dnsLogger),
  ]
except PermissionError:
  print("[ERROR] Permission error: check that you are running this as Administrator or root")
  sys.exit(1)

print("-- Done ---")
prYellow("Message of the day: "+motd.text+"\n")
if GOCENTRALDNS_VERSION != versioncheck.text:
  prRed("WARNING: You are not using the latest version of the GoCentral DNS Server. Please update to the latest version!")
elif GOCENTRALDNS_VERSION == versioncheck.text:
    prGreen("You are using the latest version of the GoCentral DNS Server! No updates are available.")
    
print("[INFO] Starting GoCentral DNS server.")
print("[INFO] Ready. Waiting for your PS3 to send DNS Requests...\n")

if __name__ == '__main__':
    for s in servers:
        s.start_thread()

    try:
        while 1:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        for s in servers:
            s.stop()

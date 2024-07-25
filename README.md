> [!CAUTION]
> If you are using an older version of the hosts file (prior to 7-25-2024) you are connecting to old, outdated and incorrect servers. Please update ASAP!
>
> 
GoCentral DNS Server [![Actions Status](https://github.com/qfoxb/GoCentral-DNS/workflows/Build/badge.svg)](https://github.com/qfoxb/GoCentral-DNS/actions)
===

This DNS Server will run locally on your computer and allow your PlayStation 3 to connect to [GoCentral](https://github.com/ihatecompvir/GoCentral) servers even if your ISP blocks connections to our DNS Server. When you use the DNS on your PS3 or with this app, you can connect to the [Open Source GoCentral server.](https://github.com/ihatecompvir/GoCentral)

## Setup

You will only need to change DNS Settings in your PS3.

First, make sure that your PS3 is connected to the same network as your computer is.

###  If you use Pi-hole, please see [Setting up Pi-hole](#setting-up-pi-hole)

# Running on Windows:

Run the .exe provided [on the releases page](https://github.com/qfoxb/GoCentral-DNS/releases). If your antivirus notifies you about the .exe file, allow it and run it. If it doesn't work, you should also allow communication for this this .exe in your firewall settings. 

# Running on Linux/macOS:

You will need to install Python 3 and run these commands in the Terminal.

> pip install dnslib requests

To run it, simply type in:

> sudo python3 GoCentral-DNS-Server.py

Replace `python3` with the name/path to your Python binary if necessary

# How to use it?

After starting the program, it will download the current list of the DNS Addresses to forward and will run. 

On screen, you will see the IP Address assigned to your computer by the DHCP Server on your NAT (router).

If your Wii is connected to the same network as your PC, it will be able to connect to the server on your PC.

<p align="center">
  <img src="https://i.imgur.com/oageZQ3.jpg">
<i>My local IP Address, yours will be different.</i>
</p>


# Compiling on Windows

To compile this app on Windows, you will need to run these two commands (Important: Pyinstaller currently fails to build with Python 3.8, use Python 3.7.5):
>pip install dnslib requests pyinstaller

Once it's done installing, run:
>pyinstaller GoCentral-DNS-Server.spec

| Tip: You may need to edit GoCentral-DNS-Server_v1.0.spec so the compiling process works on your computer.

# Setting up Pi-hole

On the server running Pi-hole, run the following command:

```bash
curl https://raw.githubusercontent.com/qfoxb/GoCentral-DNS/master/dns_zones-hosts.txt >> /etc/pihole/custom.list
```
GoCentral domains will be listed on Pi-hole webpage menu under "Local DNS Records".

# Need more help?
Feel free to open a github issue. 

# Credits
* [GoCentral](https://github.com/ihatecompvir/GoCentral), made by ihatecompvir
* [RiiConnect24 DNS Server](https://github.com/RiiConnect24/DNS-Server), made by KcrPL and Larsenv
* [sudomemoDNS](https://github.com/Sudomemo/sudomemoDNS), made by Austin Burk/Team Sudomemo
* [YARG OpenSource](https://github.com/YARC-Official/OpenSource/), made by EliteAsian123 (go play yarg!!!) Application icon provided by them.
* [RBEnhanced Team](https://github.com/RBEnhanced), go support Emma and Comp for their amazing RB3 and RBVR mods!
* [MiloHax](https://github.com/hmxmilohax) for their awesome Milo hacks

#!/usr/bin/python

import sys
import os
import core

from argparse import ArgumentParser, RawTextHelpFormatter
from configs import ENNODES
from plugins import *

__version__ = '0.1.0'

BANNER = '''
                                    _              _ _    _ _   
  _ __ ___   __ _ _ __   __ _      | |_ ___   ___ | | | _(_) |_ 
 | '_ ` _ \ / _` | '_ \ / _` |_____| __/ _ \ / _ \| | |/ / | __|
 | | | | | | (_| | | | | (_| |_____| || (_) | (_) | |   <| | |_ 
 |_| |_| |_|\__,_|_| |_|\__,_|      \__\___/ \___/|_|_|\_\_|\__|

        Developed by Dominic White (singe) & Ian de Villiers @ sensepost

                             research@sensepost.com

        Ported to Python by Gabriel Ryan (gabriel@solstice.me)

'''

def error_handler(msg):
    sys.exit('[-] %s' % msg)

def am_i_root():

    if os.geteuid():
        error_handler('Why am I not root? I want root!')

def print_banner():

    print BANNER

def invoke_metasploit():
    os.system('msfconsole -r ./conf/karmetasploit.rc')

def create_ennode():
    try:
        os.mkfifo(ENNODES)
    except OSError, e:
        error_handler('Failed to create FIFO: %s' % e)

def destroy_ennode():
    os.remove(ENNODES)

if __name__ == '__main__':

    am_i_root()
        
    print_banner()

    parser = ArgumentParser(description='mana-toolkit version %s',
                        formatter_class=RawTextHelpFormatter)

    sgroup = parser.add_argument_group('mana-toolkit', 'Options for mana-toolkit')
    sgroup.add_argument('--phy',
                    dest='phy',
                    type=str,
                    required=True,
                    help='Specify an interface to listen on.')
    sgroup.add_argument('--phy0',
                    dest='phy0',
                    type=str,
                    default='wlan0_0',
                    required=False,
                    help='Specify an interface to listen on.')
    sgroup.add_argument('--upstream',
                    dest='upstream',
                    type=str,
                    required=False,
                    help='Specify gateway inteface to forward traffic to')
    sgroup.add_argument('--no-upstream',
                    dest='no_upstream',
                    action='store_true',
                    help='Run in no upstream mode.')
    sgroup.add_argument('--no-upstream-all',
                    dest='no_upstream_all',
                    action='store_true',
                    help='Run in no upstream mode.')
    sgroup.add_argument('--no-upstream-eap',
                    dest='no_upstream_eap',
                    action='store_true',
                    help='Run in no upstream mode.')
    sgroup.add_argument('--no-upstream-eaponly',
                    dest='no_upstream_eap_only',
                    action='store_true',
                    help='Run in no upstream mode.')
    sgroup.add_argument('--nat',
                    dest='nat',
                    action='store_true',
                    help='Run in no upstream mode.')
    sgroup.add_argument('--bssid',
                    dest='bssid',
                    type=str,
                    default='00:11:22:33:44:00',
                    required=False,
                    metavar='<mac_addr>',
                    help='Set bssid of access point.')
    sgroup.add_argument('--essid',
                    dest='essid',
                    type=str,
                    default='TotallyLegit',
                    required=False,
                    metavar='<network_name>',
                    help='Set essid of access point.')
    sgroup.add_argument('--essid-secure',
                    dest='essid_secure',
                    type=str,
                    default='TotallyLegitSecure',
                    required=False,
                    metavar='<network_name>',
                    help='Set essid of access point.')
    sgroup.add_argument('--channel',
                    dest='channel',
                    type=int,
                    default=6,
                    required=False,
                    metavar='<channel_number>',
                    help='Have access point use channel <channel_number>')
    sgroup.add_argument('--hostname',
                    dest='hostname',
                    type=str,
                    default='WRT54G',
                    required=False,
                    metavar='<hostname>',
                    help='Set hostname to <hostname>')

    plugins = [plugin(parser) for plugin in plugin.Plugin.__subclasses__()]

    print plugins
    options = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        error_handler('Aborting.')

    # load only selected plugins
    for plugin in plugins:
        if plugin.is_selected(options):
            plugin.initialize(options)


    running_daemons = []

    ## perform nat initial setup
    #print '[*] Changing hostname to: ', options.hostname
    #core.utils.hostname(options.hostname)
    #print '[*] Killing wifi'
    #core.utils.rfkill()
    #print '[*] Bringing up %s with spoofed mac' % options.phy
    #core.utils.macchanger(options.phy)
    #print '[*] Bringing up %s with spoofed mac' % options.phy
    #core.utils.set_ip_forward(1)
    print '[*] Creating ennode: %s' % ENNODES
    create_ennode()

    # core stuff goes here
    if options.nat:

        core.utils.route.add_nat(options.phy)

        core.iptables.flush()
        core.iptables.nat(upstream=options.upstream, phy=options.phy)

        # configure and start core daemons 
        hostapd = core.Hostapd(options)
    
        dhcpd = core.dhcpd.Dhcpd(options)

        # start core services
        hostapd.start()
        running_daemons.append(hostapd)

        dhcpd.start()
        running_daemons.append(dhcpd)
    
    elif options.no_upstream_all:

        ## configure core services
        #dnsspoof = core.Dnsspoof(options)
        #dhcpd = core.dhcpd.Dhcpd(options)
        #hostapd = core.Hostapd(options)
        #apache = core.Apache()
        #tinyproxy = core.Tinyproxy()
        #stunnel = core.Stunnel()
        crackapd = core.Crackapd()

        ## start core services
        #print '[*] Starting dnsspoof'
        #dnsspoof.start()
        #running_daemons.append(dnsspoof)

        #hostapd.start()
        #running_daemons.append(hostapd)

        #dhcpd.start()
        #running_daemons.append(dhcpd)

        #apache.start()
        #running_daemons.append(apache)

        #tinyproxy.start()
        #running_daemons.append(tinyproxy)

        #stunnel.start()
        #running_daemons.append(stunnel)

        crackapd.start()
        running_daemons.append(crackapd)

        invoke_metasploit()

    elif options.no_upstream_eap:

        ## configure core services
        #dnsspoof = core.Dnsspoof(options)
        #dhcpd = core.dhcpd.Dhcpd(options)
        #hostapd = core.Hostapd(options)
        #apache = core.Apache()
        #tinyproxy = core.Tinyproxy()
        #stunnel = core.Stunnel()
        crackapd = core.Crackapd()

        ## start core services
        #print '[*] Starting dnsspoof'
        #dnsspoof.start()
        #running_daemons.append(dnsspoof)

        #hostapd.start()
        #running_daemons.append(hostapd)

        #dhcpd.start()
        #running_daemons.append(dhcpd)

        #apache.start()
        #running_daemons.append(apache)

        #tinyproxy.start()
        #running_daemons.append(tinyproxy)

        #stunnel.start()
        #running_daemons.append(stunnel)

        crackapd.start()
        running_daemons.append(crackapd)

        invoke_metasploit()

    elif options.no_upstream:

        ## configure core services
        #dnsspoof = core.Dnsspoof(options)
        #dhcpd = core.dhcpd.Dhcpd(options)
        #hostapd = core.Hostapd(options)
        #apache = core.Apache()
        #tinyproxy = core.Tinyproxy()
        #stunnel = core.Stunnel()
        crackapd = core.Crackapd()

        ## start core services
        #print '[*] Starting dnsspoof'
        #dnsspoof.start()
        #running_daemons.append(dnsspoof)

        #hostapd.start()
        #running_daemons.append(hostapd)

        #dhcpd.start()
        #running_daemons.append(dhcpd)

        #apache.start()
        #running_daemons.append(apache)

        #tinyproxy.start()
        #running_daemons.append(tinyproxy)

        #stunnel.start()
        #running_daemons.append(stunnel)

        crackapd.start()
        running_daemons.append(crackapd)

        invoke_metasploit()

    elif options.no_upstream_eap_only:

        ## configure core services
        #dnsspoof = core.Dnsspoof(options)
        #dhcpd = core.dhcpd.Dhcpd(options)
        #hostapd = core.Hostapd(options)
        #apache = core.Apache()
        #tinyproxy = core.Tinyproxy()
        #stunnel = core.Stunnel()
        crackapd = core.Crackapd()

        ## start core services
        #print '[*] Starting dnsspoof'
        #dnsspoof.start()
        #running_daemons.append(dnsspoof)

        #hostapd.start()
        #running_daemons.append(hostapd)

        #dhcpd.start()
        #running_daemons.append(dhcpd)

        #apache.start()
        #running_daemons.append(apache)

        #tinyproxy.start()
        #running_daemons.append(tinyproxy)

        #stunnel.start()
        #running_daemons.append(stunnel)

        crackapd.start()
        running_daemons.append(crackapd)


        invoke_metasploit()

    else:

        error_handler('No valid mode specified. Aborting.')

    # start only selected plugins
    for plugin in plugins:
        if plugin.is_selected(options):
            print '[*] Starting', plugin.name
            plugin.start()
            running_daemons.append(plugin)


    raw_input('[*] Press enter to quit.')

    # stop all running daemons
    for daemon in running_daemons:
        print '[*] Stopping', daemon.name
        daemon.stop()

    print '[*] Destroying ennode: %s' % ENNODES
    destroy_ennode()


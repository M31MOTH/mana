import os
import time

from distutils.spawn import find_executable

NETWORK_MANAGER_ALIASES = ['network-manager', 'NetworkManager']

class route(object):

    def __init__(self):
        pass

    @staticmethod
    def add_nat_full(phy):
        os.system('ifconfig %s 10.0.0.1 netmask 255.255.255.0' % phy)
        os.system('route add -net 10.0.0.0 netmask 255.255.255.0 gw 10.0.0.1')
    
def set_ip_forward(val):

    with open('/proc/sys/net/ipv4/ip_forward', 'w') as fd:
        fd.write('%d' % val)

def hostname(hostname):

    print '[*] Setting hostname to %s' % hostname
    os.system('hostname %s' % hostname)
    time.sleep(2)

def rfkill():

    for alias in NETWORK_MANAGER_ALIASES:
    
        if find_executable(alias) != None:
            os.system('service %s disable' % alias)
            os.system('service %s stop' % alias)

    os.system('rfkill unblock wlan')

def macchanger(phy):

    os.system('ifconfig %s down' % phy)
    os.system('macchanger -r %s' % phy)
    os.system('ifconfig %s up'   % phy)


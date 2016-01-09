import os
import time

from distutils.spawn import find_executable

NETWORK_MANAGER_ALIASES = ['network-manager', 'NetworkManager']
APACHE_ALIASES = ['apache', 'apache2', 'httpd']

def set_ip_forward(val):

    with open('/proc/sys/net/ipv4/ip_forward', 'w') as fd:
        fd.write('%d' % val)

def hostname(hostname):

    print '[*] Setting hostname to %s' % hostname
    os.system('hostname %s' % hostname)
    time.sleep(2)

def set_correct_alias(aliases):

    for alias in aliases:
        if find_executable(alias) is not None:
            return alias

def rfkill():

    alias = set_correct_alias(NETWORK_MANAGER_ALIASES)

    os.system('service %s disable' % alias)
    os.system('service %s stop' % alias)
    os.system('rfkill unblock wlan')

class apache(object):

    alias = set_correct_alias(APACHE_ALIASES)

    def __init__(self):
        pass

    @staticmethod
    def start():
        os.system('service %s start' % alias)

    @staticmethod
    def stop():
        os.system('service %s stop' % alias)

class route(object):

    def __init__(self):
        pass

    @staticmethod
    def add(phy):

        # clear previous route 
        os.system('ip route delete 10.0.0.0/24')

        os.system('ifconfig %s 10.0.0.1 netmask 255.255.255.0' % phy)
        os.system('route add -net 10.0.0.0 netmask 255.255.255.0 gw 10.0.0.1')

    @staticmethod
    def add_dual(phy=None, phy0=None):

        os.system('ifconfig %s' % phy)
        os.system('ifconfig %s' % phy0)
        os.system('ifconfig %s 10.0.0.1 netmask 255.255.255.0' % phy)
        os.system('route add -net 10.0.0.0 netmask 255.255.255.0 gw 10.0.0.1')
        os.system('ifconfig %s 10.1.0.1 netmask 255.255.255.0' % phy0)
        os.system('route add -net 10.1.0.0 netmask 255.255.255.0 gw 10.1.0.1')

def macchanger(phy):

    os.system('ifconfig %s down' % phy)
    os.system('macchanger -r %s' % phy)
    os.system('ifconfig %s up'   % phy)


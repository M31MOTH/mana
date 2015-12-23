import os
from multiprocessing import Process

CONF_PATH = '/etc/dhcp/dhcpd.conf'


class Dhcpd(object):

    def __init__(self,
                phy=None,
                subnet=None,
                netmask=None,
                range_start=None,
                range_end=None,
                option_routers=None):
        

        self.phy = phy

        with open(CONF_PATH, 'w') as fd:

            fd.write((
                'ddns-update-style none;'
                'ddns-update-style none;'
                ''
                'default-lease-time 60;'
                'max-lease-time 72;'
                ''
                'authoritative;'
                ''
                'log-facility local7;'
                ''
                'option wpad code 252 = text;'
                'option wpad "http://wpad.example.com/wpad.dat\n";'
                ''
                'subnet %s netmask %s {'
                '  range %s %s;'
                '  option routers %s;'
                '  option domain-name-servers 8.8.8.8;'
                '}'
            ) % (subnet, netmask, range_start, range_end, option_routers))

    @staticmethod
    def _start(conf, phy):

        os.system('dhcpd -cf %s %s' % (conf, phy))

    def start(self):

        self.proc = Process(target=self.start, args=(CONF_PATH, self.phy,))
        self.proc.daemon = True
        self.proc.start()

    def stop(self): 

        self.proc.terminate()
        self.proc.join()

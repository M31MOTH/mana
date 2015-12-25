import os
from multiprocessing import Process

CONF_PATH = '/etc/dhcp/dhcpd.conf'


class Dhcpd(object):

    def __init__(self, options):
        
        if options.nat:

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
                    'subnet 10.0.0.0 netmask 255.255.255.0 {'
                    '  range 10.0.0.100 10.0.0.254;'
                    '  option routers 10.0.0.1;'
                    '  option domain-name-servers 8.8.8.8;'
                    '}'
                ))

    @staticmethod
    def _start(configs):

        os.system('dhcpd -cf %s %s' % (CONF_PATH, configs['phy']))
    
    def start(self):
    
        self.proc = Process(target=self._start, args=({'phy' : options.phy},))
        self.proc.daemon = True
        self.proc.start()
        time.sleep(5)

    def stop(self):

        self.proc.terminate()
        self.proc.join()

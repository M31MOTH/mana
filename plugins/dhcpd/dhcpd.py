import os

CONF_PATH = '/etc/dhcp/dhcpd.conf'

def configure_nat_full(conf_path=CONF_PATH):

    with open(conf_path, 'w') as fd:

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

def dhcpd(phy):

    os.system('dhcpd -cf %s %s' % (CONF_PATH, phy))

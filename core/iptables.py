import os

def flush():

    os.system('iptables --policy INPUT ACCEPT')
    os.system('iptables --policy FORWARD ACCEPT')
    os.system('iptables --policy OUTPUT ACCEPT')
    os.system('iptables -F')
    os.system('iptables -t nat -F')

def nat(phy=None, upstream=None):

    os.system('iptables -t nat -A POSTROUTING -o %s -j MASQUERADE' % upstream)
    os.system('iptables -A FORWARD -i %s -o %s -j ACCEPT' % (phy, upstream))

def no_upstream(phy):

    os.system('iptables -t nat -A PREROUTING -i %s -p udp --dport 53 -j DNAT --to 10.0.0.1' % phy)

def dns2proxy(phy=None):
    os.system('iptables -t nat -A PREROUTING -i %s -p udp --dport 53 -j DNAT --to 10.0.0.1' % phy)

def sslstrip(phy=None, sslstrip_port=10000):
        
    print 'iptabling'

    os.system('iptables -t nat -A PREROUTING -i %s -p tcp --destination-port 80 -j REDIRECT --to-port %s' % (phy, sslstrip_port))

def sslsplit(phy=None):

    command = ('iptables -t nat -A PREROUTING -i %s '
        ' -p tcp --destination-port 443 '
        ' -j REDIRECT --to-port 10443 ') % phy
    os.system(command)

    command = ('iptables -t nat -A PREROUTING -i %s '
        ' -p tcp --destination-port 143 '
        ' -j REDIRECT --to-port 10143 ') % phy
    os.system(command)

    command = ('iptables -t nat -A PREROUTING -i %s '
        ' -p tcp --destination-port 993 '
        ' -j REDIRECT --to-port 10993 ') % phy
    os.system(command)

    command = ('iptables -t nat -A PREROUTING -i %s '
        ' -p tcp --destination-port 65493 '
        ' -j REDIRECT --to-port 10993 ') % phy
    os.system(command)

    command = ('iptables -t nat -A PREROUTING -i %s '
        ' -p tcp --destination-port 465 '
        ' -j REDIRECT --to-port 10465 ') % phy
    os.system(command)

    command = ('iptables -t nat -A PREROUTING -i %s '
        ' -p tcp --destination-port 25 '
        ' -j REDIRECT --to-port 10025 ') % phy
    os.system(command)

    command = ('iptables -t nat -A PREROUTING -i %s '
        ' -p tcp --destination-port 995 '
        ' -j REDIRECT --to-port 10995 ') % phy
    os.system(command)

    command = ('iptables -t nat -A PREROUTING -i %s '
        ' -p tcp --destination-port 110 '
        ' -j REDIRECT --to-port 10110') % phy
    os.system(command)


import sys, getopt, logging, traceback, string, os

from plugin import Plugin
from plugin_deps import dns2proxy
from core import iptables


gVersion = "0.9 +"

class Dns2proxy(Plugin):

    name = 'dns2proxy'
    optname = 'dns2proxy'
    desc = 'Offensive DNS server (use with sslstrip2 for HSTS bypass'
    sleep_time = 2

    def initialize(self, options):

        self.configs = {
        
            'phy' : options.phy,
        }

        iptables.dns2proxy(phy=options.phy)

    @staticmethod
    def _start(configs):

        dns2proxy.run(interface=configs['phy'])

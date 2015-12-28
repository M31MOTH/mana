
from core import iptables
from plugin_deps import net_creds

import sys, getopt, logging, traceback, string, os

class Net_creds(Plugin):

    name = 'net_creds'
    optname = 'net-creds'
    desc = 'Netcreds.'
    sleep_time = 2

    def initialize(self, options):

        self.configs = {
        
            'interface' : options.phy,
            'filterip' : options.filterip,
        
        }

        iptables.sslstrip(phy=options.phy)

    def options(self, options):

        options.add_argument('--filterip',
                        dest='filterip',
                        type=str,
                        required=False,
                        default=None, 
                        metavar='<ipaddr>',
                        help='Filter for <ipaddr>')

    @staticmethod
    def _start(configs):

        net_creds.run(interface=configs['log_file'],
                    filterip=configs['filterip'],
                    pcap=None)

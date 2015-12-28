import sys
import getopt
import logging
import traceback
import string
import os

from plugin import Plugin
from plugin_deps import firelamb
from core import iptables
from configs import configs_path


class Firelamb(Plugin):

    name = 'firelamb'
    optname = 'firelamb'
    desc = 'Glenn\'s Firelamb'
    sleep_time = 2

    def initialize(self, options):

        self.configs = {
        
            'iface' : options.phy,
            'log_by_ip' : options.log_by_ip,
            'launch_ff' : options.launch_ff,
            'sslsplitdir' : configs_path,
            'sslstriplog' : options.log_file,
        }

    def options(self, options):

        options.add_argument('--log-by-ip',
                        dest='log_by_ip',
                        action='store_true',
                        help='Create cookie file per IP address. Default is per device MAC address')
        options.add_argument('--launch-firefox',
                        dest='launch_ff',
                        action='store_true',
                        help='Launch Firefox profiles for the saved cookies')

    @staticmethod
    def _start(configs):

        firelamb.run(iface=configs['iface'],
                    log_by_ip=configs['log_by_ip'],
                    launch_ff=configs['launch_ff'],
                    sslsplitdir=configs['sslsplitdir'],
                    sslstriplog=configs['sslstriplog'])


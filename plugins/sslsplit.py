import sys
import getopt
import logging
import traceback
import string
import os
import core

from datetime import datetime
from plugin import Plugin
from core import iptables

from configs import CERT_DIR, configs_path

CA_CERT = 'rogue-ca.pem'
CA_KEY = 'rogue-ca.key'

class Sslsplit(Plugin):

    name = 'sslsplit'
    optname = 'sslsplit'
    desc = 'Splitting proxy'
    sleep_time = 2
    kill_command = 'sslsplit'

    def initialize(self, options):

        core.iptables.sslsplit(phy=options.phy)
        self.configs = {}

    @staticmethod
    def _start(configs):

        command = ['sslsplit']
        command.append('-D')
        command.append('-P')
        command.append('-S %s' % configs_path)
        command.append('-c %s' % '/'.join([CERT_DIR, CA_CERT]))
        command.append('-k %s' % '/'.join([CERT_DIR, CA_KEY]))
        command.append('-O')
        command.append('-l sslsplit.log' )
        command.append(('https 0.0.0.0 10443 '
                        'http 0.0.0.0 10080 '
                        'ssl 0.0.0.0 10993 '
                        'tcp 0.0.0.0 10143 '
                        'ssl 0.0.0.0 10995 '
                        'tcp 0.0.0.0 10110 '
                        'ssl 0.0.0.0 10465 '
                        'tcp 0.0.0.0 10025'))

        command = ' '.join(command)

        os.system(command)

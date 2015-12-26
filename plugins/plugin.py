# Copyright (c) 2014-2016 Marcello Salvati
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
#

import os, time

from multiprocessing import Process

class Plugin(object):

    name        = "Generic plugin"
    optname     = "generic"
    desc = ''
    sleep_time = 2

    def __init__(self, parser):
    
        # any configs needed by _start() should be passed through
        # self.configs dictionary
        self.configs = {}

        if self.desc:
            sgroup = parser.add_argument_group(self.name, self.desc)
        else:
            sgroup = parser.add_argument_group(self.name,"Options for the '{}' plugin".format(self.name))

        sgroup.add_argument("--{}".format(self.optname), action="store_true",help="Load plugin '{}'".format(self.name))

        self.options(sgroup)

    def initialize(self, options):
        '''Called if plugin is enabled, passed the options namespace'''
        self.options = options

    def options(self, options):
        pass

    def is_selected(self, options):
        return vars(options)[self.optname]

    @staticmethod
    def _start(configs):
        
        # plugin implementation here
        pass

    def start(self):
    
        self.proc = Process(target=self._start, args=(self.configs,))
        self.proc.daemon = True
        self.proc.start()
        time.sleep(self.sleep_time)

    def stop(self):

        self.proc.terminate()
        self.proc.join()


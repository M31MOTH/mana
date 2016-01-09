import os
import time

from multiprocessing import Process
from configs import configs_path, CONF_DIR

CONF_PATH = '%s/dnsspoof.conf' % CONF_DIR 

class Dnsspoof(object):

    name = 'dnsspoof'
    desc = 'Offensive DNS server and spoofer'
    sleep_time = 2

    def __init__(self, options):

        self.configs = {
                key:value for key,value in options.__dict__.items()
        }

    @staticmethod
    def _start(phy):

        os.system('dnsspoof -f %s -i %s 2>&1 > dnsspoof.log' % (CONF_PATH, phy))

    def start(self):

        self.daemons = []
        if self.configs['no_upstream_all'] or self.configs['no_upstream_eap']:
            proc = Process(target=self._start, args=(self.configs['phy0'],))
            proc.daemon = True
            proc.start()
            self.daemons.append(proc)
        print self.configs['phy']
        proc = Process(target=self._start, args=(self.configs['phy'],))
        proc.daemon = True
        proc.start()
        self.daemons.append(proc)

    def stop(self):
    
        for proc in self.daemons:

            proc.terminate()
            proc.join()

        # nothing is unkillable
        os.system('for i in `pgrep dnsspoof`; do kill $i; done')

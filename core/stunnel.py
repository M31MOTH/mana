import os
import time

from multiprocessing import Process
from configs import configs_path, CONF_DIR

CONF_PATH = '%s/stunnel.conf' % CONF_DIR 

class Stunnel(object):

    name = 'stunnel'
    sleep_time = 2

    def __init__(self):
        pass

    @staticmethod
    def _start():

        os.system('service stunnel start')

    def start(self):
    
        self.proc = Process(target=self._start)
        self.proc.daemon = True
        self.proc.start()

        time.sleep(self.sleep_time)

    def stop(self):

        self.proc.terminate()
        self.proc.join()
            
        # hackish fix but will have to suffice for now
        os.system('service stunnel stop')

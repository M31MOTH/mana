import os
import time

from multiprocessing import Process
from configs import configs_path, CONF_DIR

CONF_PATH = '%s/dhcpd.conf' % CONF_DIR 
SECOND_CONF_PATH = '%s/dhcpd-two.conf' % CONF_DIR 
LEASE_FILE = '/var/lib/dhcp/dhcpd-two.leases'
PID_FILE = '/var/run/dhcpd-two.pid' 

class Dhcpd(object):

    name = 'dhcpd'
    sleep_time = 5

    def __init__(self, options):

        self.dual_wield = any([
                        options.no_upstream_eap,
                        options.no_upstream_all,
                     ])

        self.options = options

    @staticmethod
    def _start(pid_file, lease_file, conf_file, interface):

        if lease_file is not None and pid_file is not None:

            os.system('dhcpd -pf %s -lf %s -cf %s %s' %\
                            (pid_file, lease_file, conf_file, interface))

        else:

            os.system('dhcpd -cf %s %s' % (conf_file, interface))

    def start(self):
    
        self.daemons = []
        if self.dual_wield:
            self.daemons.append(Process(target=self._start,
                            args=(PID_FILE,
                                LEASE_FILE,
                                SECOND_CONF_PATH,
                                self.options.phy0,)
                        ))
        self.daemons.append(Process(target=self._start,
                        args=(None,
                            None,
                            CONF_PATH,
                            self.options.phy,)
                    ))

        for proc in self.daemons:
            proc.daemon = True
            proc.start()

        time.sleep(self.sleep_time)

    def stop(self):

        for proc in self.daemons:
            proc.terminate()
            proc.join()
        
        # dhcpd can be a bit dodgy when we attempt to kill it... show no mercy
        os.system('for i in `pgrep dhcpd`; do kill $i; done')


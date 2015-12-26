import os
import time

from multiprocessing import Process

from configs import configs_path, CONF_DIR

CONF_PATH = '%s/hostapd-configs.conf' % CONF_DIR 
HOSTAPD_PATH = '%s/hostapd-mana/hostapd/hostapd' % configs_path

class Hostapd(object):

    name = 'hostapd'

    def __init__(self, options):

        if options.nat:

            with open(CONF_PATH, 'w') as fd:
                fd.write((
                    'interface=%s\n'
                    'bssid=%s\n'
                    'driver=nl80211\n'
                    'ssid=%s\n'
                    'channel=%d\n'
                    '\n'
                    '# Prevent dissasociations\n'
                    'disassoc_low_ack=0\n'
                    'ap_max_inactivity=3000\n'
                    '\n'
                    '# Both open and shared auth\n'
                    'auth_algs=3\n'
                    '\n'
                    '# no SSID cloaking\n'
                    '#ignore_broadcast_ssid=0\n'
                    '\n'
                    '# -1 = log all messages\n'
                    'logger_syslog=-1\n'
                    'logger_stdout=-1\n'
                    '\n'
                    '# 2 = informational messages\n'
                    'logger_syslog_level=2\n'
                    'logger_stdout_level=2\n'
                    '\n'
                    'ctrl_interface=/var/run/hostapd\n'
                    'ctrl_interface_group=0\n'
                    '\n'
                    '# 0 = accept unless in deny list\n'
                    '#macaddr_acl=0\n'
                    '\n'
                    '# only used if you want to do filter by MAC address\n'
                    '#accept_mac_file=/etc/hostapd/hostapd.accept\n'
                    '#deny_mac_file=/etc/hostapd/hostapd.deny\n'
                    '\n'
                    '# Enable karma mode\n'
                    'enable_karma=1\n'
                    '# Limit karma to responding only to the device probing (0), or not (1)\n'
                    'karma_loud=0\n'
                    '\n'
                    '# Black and white listing\n'
                    '# 0 = white\n'
                    '# 1 = black\n'
                    '#karma_black_white=1\n'
                ) % (options.phy, options.bssid, options.essid, options.channel))
    
    @staticmethod
    def _start(configs):
        os.system('%s %s' % (HOSTAPD_PATH, CONF_PATH))
    
    def start(self):
    
        self.proc = Process(target=self._start, args=({},))
        self.proc.daemon = True
        self.proc.start()
        time.sleep(5)

    def stop(self):

        self.proc.terminate()
        self.proc.join()

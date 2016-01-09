import os
import time

from multiprocessing import Process

from configs import configs_path, CONF_DIR, CERT_DIR, ENNODES

CONF_PATH = '%s/hostapd-configs.conf' % CONF_DIR 
HOSTAPD_PATH = '%s/hostapd-mana/hostapd/hostapd' % configs_path

class Hostapd(object):

    name = 'hostapd'

    def __init__(self, options):

        if options.nat or options.no_upstream:

            conf_file = (
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
            ) % (options.phy, options.bssid, options.essid, options.channel)

        elif options.no_upstream_all:

            conf_file = '\n'.join([
                'interface=%s' % options.phy,
                'bssid=%s' % options.bssid,
                'driver=nl80211',
                'ssid=%s' % options.essid,
                'channel=%d' % options.channel,
                '',
                'bss=%s' % options.phy0,
                'ssid=%s' % options.essid_secure,
                'ieee8021x=1',
                'eapol_key_index_workaround=0',
                'eap_server=1',
                'eap_user_file=%s/hostapd.eap_user' % CONF_DIR,
                'ca_cert=%s/rogue-ca.pem' % CERT_DIR,
                'server_cert=%s/radius.pem' % CERT_DIR,
                'private_key=%s/radius.key' % CERT_DIR,
                'private_key_passwd=',
                'dh_file=%s/dhparam.pem' % CERT_DIR,
                'pac_opaque_encr_key=000102030405060708090a0b0c0d0e0f',
                'eap_fast_a_id=101112131415161718191a1b1c1d1e1f',
                'eap_fast_a_id_info=test server',
                'eap_fast_prov=3',
                'pac_key_lifetime=604800',
                'pac_key_refresh_time=86400',
                'wpa=2',
                'wpa_key_mgmt=WPA-EAP',
                'wpa_pairwise=TKIP CCMP',
                '',
                '# Prevent dissasociations',
                'disassoc_low_ack=0',
                'ap_max_inactivity=3000',
                '',
                '# Both open and shared auth',
                'auth_algs=3',
                '',
                '# no SSID cloaking',
                'ignore_broadcast_ssid=2',
                '',
                '# -1 = log all messages',
                'logger_syslog=-1',
                'logger_stdout=-1',
                '',
                '# 2 = informational messages',
                'logger_syslog_level=1',
                'logger_stdout_level=1',
                '',
                'ctrl_interface=/var/run/hostapd',
                'ctrl_interface_group=0',
                '',
                '# 0 = accept unless in deny list',
                'macaddr_acl=0',
                '',
                '# only used if you want to do filter by MAC address',
                '#accept_mac_file=/etc/hostapd/hostapd.accept',
                '#deny_mac_file=/etc/hostapd/hostapd.deny',
                '',
                '# Finally, enable Karma',
                'enable_karma=1',
                '# Limit karma to responding only to the device probing (0), or not (1)',
                'karma_loud=0',
                '',
                '# Black and white listing',
                '# 0 = white',
                '# 1 = black',
                '#karma_black_white=1',
                '',
                'ennode=%s' % ENNODES,
            ])

        elif options.no_upstream_eap:

            conf_file = '\n'.join([
                'interface=%s' % options.phy,
                'bssid=%s' % options.bssid,
                'driver=nl80211',
                'ssid=%s' % options.essid,
                'channel=%d' % options.channel,
                '',
                'bss=%s' % options.phy0,
                'ssid=%s' % options.essid_secure,
                'ieee8021x=1',
                'eapol_key_index_workaround=0',
                'eap_server=1',
                'eap_user_file=%s/hostapd.eap_user' % CONF_DIR,
                'ca_cert=%s/rogue-ca.pem' % CERT_DIR,
                'server_cert=%s/radius.pem' % CERT_DIR,
                'private_key=%s/radius.key' % CERT_DIR,
                'private_key_passwd=',
                'dh_file=%s/dhparam.pem' % CERT_DIR,
                'pac_opaque_encr_key=000102030405060708090a0b0c0d0e0f',
                'eap_fast_a_id=101112131415161718191a1b1c1d1e1f',
                'eap_fast_a_id_info=test server',
                'eap_fast_prov=3',
                'pac_key_lifetime=604800',
                'pac_key_refresh_time=86400',
                'wpa=1',
                'wpa_key_mgmt=WPA-EAP',
                'wpa_pairwise=TKIP CCMP',
                '',
                '# Prevent dissasociations',
                'disassoc_low_ack=0',
                'ap_max_inactivity=3000',
                '',
                '# Both open and shared auth',
                'auth_algs=3',
                '',
                '# no SSID cloaking',
                'ignore_broadcast_ssid=0',
                '',
                '# -1 = log all messages',
                'logger_syslog=-1',
                'logger_stdout=-1',
                '',
                '# 2 = informational messages',
                'logger_syslog_level=1',
                'logger_stdout_level=1',
                '',
                'ctrl_interface=/var/run/hostapd',
                'ctrl_interface_group=0',
                '',
                '# 0 = accept unless in deny list',
                'macaddr_acl=0',
                '',
                '# only used if you want to do filter by MAC address',
                '#accept_mac_file=/etc/hostapd/hostapd.accept',
                '#deny_mac_file=/etc/hostapd/hostapd.deny',
                '',
                '# Finally, enable Karma',
                'enable_karma=1',
                '# Limit karma to responding only to the device probing (0), or not (1)',
                'karma_loud=0',
                '',
                '# Black and white listing',
                '# 0 = white',
                '# 1 = black',
                '#karma_black_white=1',
                '',
                'ennode=%s' % ENNODE,
            ])

        elif options.no_upstream_eap_only:

            conf_file = '\n'.join([

                'interface=%s' % options.phy,
                'channel=%d' % options.channel,
                'ssid=%s' % options.essid,
                'ieee8021x=1',
                'eapol_key_index_workaround=0',
                'eap_server=1',
                'eap_user_file=%s/hostapd.eap_user' % CONF_DIR,
                'ca_cert=%s/rogue-ca.pem' % CERT_DIR,
                'server_cert=%s/radius.pem' % CERT_DIR,
                'private_key=%s/radius.key' % CERT_DIR,
                'private_key_passwd=',
                'dh_file=%s/dhparam.pem' % CERT_DIR,
                'pac_opaque_encr_key=000102030405060708090a0b0c0d0e0f',
                'eap_fast_a_id=101112131415161718191a1b1c1d1e1f',
                'eap_fast_a_id_info=test server',
                'eap_fast_prov=3',
                'pac_key_lifetime=604800',
                'pac_key_refresh_time=86400',
                'wpa=1',
                'wpa_key_mgmt=WPA-EAP',
                'wpa_pairwise=TKIP CCMP',
                '',
                '# Prevent dissasociations',
                'disassoc_low_ack=0',
                'ap_max_inactivity=3000',
                '',
                '# Both open and shared auth',
                'auth_algs=3',
                '',
                '# no SSID cloaking',
                'ignore_broadcast_ssid=2',
                '',
                '# -1 = log all messages',
                'logger_syslog=-1',
                'logger_stdout=-1',
                '',
                '# 2 = informational messages',
                'logger_syslog_level=1',
                'logger_stdout_level=1',
                '',
                'ctrl_interface=/var/run/hostapd',
                'ctrl_interface_group=0',
                '',
                '# 0 = accept unless in deny list',
                'macaddr_acl=0',
                '',
                '# only used if you want to do filter by MAC address',
                '#accept_mac_file=/etc/hostapd/hostapd.accept',
                '#deny_mac_file=/etc/hostapd/hostapd.deny',
                '',
                '# Finally, enable Karma',
                'enable_karma=1',
                '# Limit karma to responding only to the device probing (0), or not (1)',
                'karma_loud=0',
                '',
                '# Black and white listing',
                '# 0 = white',
                '# 1 = black',
                '#karma_black_white=1',
                '',
                'ennode=%s' % ENNODE,
            ])

        else:
            raise Exception('[Hostapd] No mode specified')

        with open(CONF_PATH, 'w') as fd:
            fd.write(conf_file)
    
    @staticmethod
    def _start(configs):
        os.system('%s %s 2>&1 > hostapd.log' % (HOSTAPD_PATH, CONF_PATH))
    
    def start(self):
    
        self.proc = Process(target=self._start, args=({},))
        self.proc.daemon = True
        self.proc.start()
        time.sleep(5)

    def stop(self):

        self.proc.terminate()
        self.proc.join()

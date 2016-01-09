# Mana Toolkit Configs --------------------------------------------------------
import os
configs_path = os.path.dirname(os.path.realpath(__file__))
CERT_DIR = '/'.join([configs_path, 'cert'])
CONF_DIR = '/'.join([configs_path, 'conf'])

# The script used to crack the hashes
CRACKEX="/usr/bin/asleap"

# The wordlist to use for cracking
WORDLIST="/opt/wordlists/rockyou.txt"

ENNODES="%s/ennode.node" % configs_path

MSF_RC = '%s/karmetasploit.rc' % CONF_DIR

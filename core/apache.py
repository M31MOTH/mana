import os

from utils import set_correct_alias

APACHE_ALIASES = ['apache', 'apache2', 'httpd']

class Apache(object):

    alias = set_correct_alias(APACHE_ALIASES)
    name = 'apache'

    def __init__(self):
        pass

    @staticmethod
    def start():
        os.system('service %s start' % Apache.alias)

    @staticmethod
    def stop():
        os.system('service %s stop' %  Apache.alias)

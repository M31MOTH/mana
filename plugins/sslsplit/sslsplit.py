import os

from multiprocessing import Process

LOG_DIR = '/var/log'

class Sslsplit(object):

    def __init__(self,
             debug=False,
             enable_passthru=False,
             disable_compression=False,
             log_dir=None,
             ca_cert=None,
             ca_key=None,
             deny_ocsp_requests=False,
             log_file=None):

        command = ['sslsplit']

        if debug:
            command.append('-D')
        if enable_passthru:
            command.append('-P')
        if log_dir is not None:
            command.append('-S %s' % log_dir)
        if ca_cert is not None:
            command.append('-c %s' % ca_cert)
        if ca_key is not None:
            command.append('-k %s' % ca_key)
        if deny_ocsp_requests:
            command.append('-O')
        if log_file is not None:
            command.append('-l %s' % log_file)

        command.append(('https 0.0.0.0 10443 '
                        'http 0.0.0.0 10080 '
                        'ssl 0.0.0.0 10993 '
                        'tcp 0.0.0.0 10143 '
                        'ssl 0.0.0.0 10995 '
                        'tcp 0.0.0.0 10110 '
                        'ssl 0.0.0.0 10465 '
                        'tcp 0.0.0.0 10025'))

        self.command = ' '.join(command)
    
    @staticmethod
    def _start(command):
        os.system(command)

    def start(self):

        self.proc = Process(target=self._start, args=(self.command,))
        self.proc.daemon = True
        self.proc.start()
    
    def stop(self): 

        self.proc.terminate()
        self.proc.join()
        os.system('killall sslsplit')
    

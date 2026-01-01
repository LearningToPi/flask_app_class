from gevent.pywsgi import WSGIHandler
from datetime import datetime

def patched_format_request(self):
    now = datetime.now().replace(microsecond=0)
    length = self.response_length or '-'
    if self.time_finish:
        delta = '%.6f' % (self.time_finish - self.time_start)
    else:
        delta = '-'
    if getattr(self, 'environ', None):
        if 'HTTP_X_REAL_IP' in self.environ:
            client_address = self.environ['HTTP_X_REAL_IP']
        else:
            client_address = self.client_address[0] if isinstance(self.client_address, tuple) else self.client_address
    else:
        client_address = self.client_address[0] if isinstance(self.client_address, tuple) else self.client_address
    return '%s - - [%s] "%s" %s %s %s' % (
        client_address or '-',
        now,
        self.requestline or '',
        # Use the native string version of the status, saved so we don't have to
        # decode. But fallback to the encoded 'status' in case of subclasses
        # (Is that really necessary? At least there's no overhead.)
        (self._orig_status or self.status or '000').split()[0],
        length,
        delta)

def patch_wsgihandler():
    WSGIHandler.format_request = patched_format_request

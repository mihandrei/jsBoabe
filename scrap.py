from cherrypy import expose, request
import json


class Streams(object):
    @expose
    def range(self, start, end, step, mul=1, sep=' '):
        return sep.join(str(a) for a in xrange(int(start),int(end), int(step)))

    @expose
    def stromp(self):
        yield '4'
        yield '87'
        yield '7'

    @expose
    def index(self):
        return json.dumps(request.config)


class Bleah(object):
    streams = Streams()
        
    @expose
    def index(self):
        return json.dumps(range(10))

    def diov(self):
        return self.atr
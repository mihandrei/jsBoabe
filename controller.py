from cherrypy import expose, request
import json
from string import Template

class Main(object):

    @expose
    def index(self):
        with open('index.html') as t:
            templ = Template(t.read())
            return templ.substitute()

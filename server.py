import cherrypy
import controller
import os.path

config = {
    '/s': {
        'tools.staticdir.on': True,
        'tools.staticdir.root': os.path.abspath('.'),
        'tools.staticdir.dir': 'client',
    }
}

cherrypy.quickstart(controller.Main(), config=config)
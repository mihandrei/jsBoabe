import cherrypy
import controller

config = {
    '/s': {
        'tools.staticdir.on': True,
        'tools.staticdir.root': 'C:\\Users\\mihai\\Desktop\\jsBoabe',
        'tools.staticdir.dir': 'client',
    }
}

cherrypy.quickstart(controller.Main(), config=config)
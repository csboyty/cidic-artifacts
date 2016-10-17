# coding:utf-8

import logging.config
logging.config.fileConfig('log.conf')


from flask_debugtoolbar import DebugToolbarExtension
from ca.backend import create_app as backend_app
from ca.frontend import create_app as frontend_app

if __name__ == '__main__':
    from werkzeug.wsgi import DispatcherMiddleware
    from werkzeug.serving import run_simple

    backendapp = backend_app()
    toolbar = DebugToolbarExtension(backendapp)

    application = DispatcherMiddleware(frontend_app(), {
        '/backend': backendapp,
    })
    run_simple("0.0.0.0", 5002, application, use_debugger=False)
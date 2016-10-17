# coding:utf-8

import logging.config
logging.config.fileConfig('log.conf')
from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.contrib.fixers import ProxyFix
import ca.frontend as frontend
import ca.backend as backend




frontend_app = frontend.create_app()
backend_app = backend.create_app()

application = ProxyFix(DispatcherMiddleware(frontend_app,
                                            {
                                                '/backend': backend_app,
                                            }))

if __name__ == "__main__":
    run_simple("0.0.0.0", 7200, application)

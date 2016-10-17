# coding:utf-8

import logging.config
logging.config.fileConfig('log.conf')

from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

from ca.core import db
from ca.frontend import create_app as frontend_create_app
from ca.backend import create_app as backend_create_app



app = backend_create_app()
migrate = Migrate(app, db)
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


if __name__ == "__main__":
    manager.run()
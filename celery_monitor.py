#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from celery import Celery
import datetime

import signal
import sys
import atexit

Base = declarative_base()


class CeleryTaskLog(Base):
    __tablename__ = "celery_task_log"

    id = sa.Column(sa.Unicode(36), primary_key=True)
    task_name = sa.Column(sa.Unicode(64), nullable=False)
    args = sa.Column(sa.UnicodeText(), nullable=True)
    kwargs = sa.Column(sa.UnicodeText(), nullable=True)
    retries = sa.Column(sa.Integer(), default=0)
    exception = sa.Column(sa.UnicodeText(), nullable=True)
    status = sa.Column(sa.SmallInteger(), nullable=True, default=0)  # -2:retry, -1:failure, 1:success,
    created_at = sa.Column(sa.DateTime())
    ended_at = sa.Column(sa.DateTime(), nullable=True)


def celery_monitor(app):
    state = app.events.state()

    def on_received_task(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])
        task_log = session.query(CeleryTaskLog).get(task.uuid)
        if task_log is None:
            task_log = CeleryTaskLog(id=task.uuid, task_name=task.name, args=task.args, kwargs=task.kwargs,
                                     retries=task.retries, status=0,
                                     created_at=datetime.datetime.utcfromtimestamp(task.timestamp))
        else:
            task_log.retries = task.retries
            if task.retries > 0:
                task_log.status = -2
        session.add(task_log)
        session.commit()

    def on_failed_task(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])
        task_log = session.query(CeleryTaskLog).get(task.uuid)
        if task_log:
            task_log.exception = task.exception
            task_log.status = -1
            task_log.ended_at = datetime.datetime.utcfromtimestamp(task.timestamp)
            session.commit()

    def on_succeeded_task(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])
        task_log = session.query(CeleryTaskLog).get(task.uuid)
        if task_log:
            task_log.status = 1
            task_log.end_at = datetime.datetime.utcfromtimestamp(task.timestamp)
            session.commit()

    with app.connection() as connection:
        receiver = app.events.Receiver(connection, hanlders={
            'task-received': on_received_task,
            'task-failed': on_failed_task,
            'task-succeeded': on_succeeded_task,
        })
        receiver.capture(limit=None, timeout=None, wakeup=True)


class GracefulInterruptHandler(object):
    def __init__(self, exit_handler=None, sigs=[signal.SIGINT, signal.SIGTERM]):
        self.sigs = sigs
        if exit_handler:
            atexit.register(exit_handler)

    def __enter__(self):
        self.released = False

        self.original_handlers = [(sig, signal.getsignal(sig)) for sig in self.sigs]

        def handler(signum, frame):
            self.release()
            sys.exit(0)

        for sig in self.sigs:
            signal.signal(sig, handler)

        return self

    def __exit__(self, type, value, tb):
        self.release()

    def release(self):
        if self.released:
            return False

        for (sig, orignal_handler) in self.original_handlers:
            signal.signal(sig, orignal_handler)

        self.released = True

        return True


if __name__ == '__main__':
    engine = sa.create_engine('postgresql+psycopg2://postgres:postgresql@localhost/cidic_artifacts')
    engine.echo = True
    session = Session(engine)
    Base.metadata.create_all(engine)
    app = Celery()
    app.config_from_object('ca.celery_config')

    with GracefulInterruptHandler(exit_handler=lambda: engine.dispose()) as h:
        celery_monitor(app)

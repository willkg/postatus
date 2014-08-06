#!/usr/bin/env python
import os
import subprocess

from flask.ext.script import Manager

from postatus.wsgi import application


manager = Manager(application)

app_path = os.path.join(os.path.dirname(__file__), 'denise')


def call_command(cmd, verbose=False):
    if verbose:
        print cmd
    subprocess.call(cmd)


if __name__ == '__main__':
    manager.run()

#!/usr/bin/env python
import os
import subprocess

from flask.ext.script import Manager

from postatus.wsgi import app


manager = Manager(app)


def call_command(cmd, verbose=False):
    if verbose:
        print cmd
    subprocess.call(cmd)


if __name__ == '__main__':
    manager.run()

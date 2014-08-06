========
 README
========

Summary
=======

SUMO and Input generate postatus.txt files during deployment. This is
a webapp that parses those files and generates a series of links to
take a lot of the manual labor out of writing up bugs for issues
discovered.

.. Note::

   This is a copy-and-paste hacked-together monstrosity that
   does what I wanted it to do.

   It's a prototype.

   It's pre-alpha.

   Its future is unknown. I may never work on this again.


Install and configure
=====================

1. Create a virtual environment.

2. Install dependencies::

       $ pip install -r requirements.txt

3. Read through ``config.py`` and change settings there.


Run server
==========

Run::

    $ python manage.py runserver


Deploy this
===========

Use the ``wsgi.py`` file and a wsgi runner.

#!/usr/bin/env python2.6

import sys, os
from setuptools import setup
from distutils.core import Extension
from distutils.sysconfig import get_python_inc

setup(
    name = "nntp2nntp",
    version = "0.3",
    jescription = "The nntp2nntp is an NNTP proxy with SSL support and authentication mapping.",
    long_description = """NNTP2NNTP Proxy allow you to use your NNTP Account from multiple systems, each
with own user name and password. It fully supports SSL and you can also limit
the access to proxy with SSL certificates. NNTP2NNTP Proxy is very simple and
pretty fast. Additional features in 0.2:

- Limit the number of connections for server
- Limit the number of connections to proxy per user
- Verification of client certificates can be disabled now

It contains also a script to post yEnc-encoded files in a
binsearch-conform format.
""",
    author = "Oleksandr Kozachuk",
    author_email = "ddeus.pypi@mailnull.com",
    url = "http://pypi.python.org/pypi/nntp2nntp",
    download_url = "http://sourceforge.net/projects/nntp2nntp/",
    license = "WTFPL",
    install_requires = ['Twisted', 'pyOpenSSL'],
    scripts = ["nntp2nntp.py", "nntppost.py"],
    keywords = ["NNTP", "OpenSSL", "Proxy"],
    classifiers = [
      'Development Status :: 4 - Beta'
      'Environment :: Console'
      'Environment :: No Input/Output (Daemon)'
      'Framework :: Twisted'
      'Intended Audience :: End Users/Desktop',
      'Intended Audience : System Administrators'
      'License : Public Domain'
      'Operating System : POSIX'
      'Operating System : Unix'
      'Programming Language : Python : 2'
      'Programming Language : Python : 2.6'
      'Programming Language : Python : 2.7'
      'Topic : Communications : Usenet News'
      'Topic : Internet : Proxy Servers'
      'Topic :: Utilities',
    ],
    zip_safe = False,
)

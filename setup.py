#!/usr/bin/env python2.6

import sys, os
from setuptools import setup
from distutils.core import Extension
from distutils.sysconfig import get_python_inc

setup(
    name = "nntp2nntp",
    version = "0.2",
    description = "The nntp2nntp is an NNTP proxy with SSL support and authentication mapping.",
    author = "Oleksandr Kozachuk",
    author_email = "ddeus.pypi@mailnull.com",
    url = "http://pypi.python.org/pypi/nntp2nntp",
    license = "WTFPL",
    install_requires = ['Twisted', 'pyOpenSSL'],
    scripts = ["nntp2nntp.py"],
    classifiers = [
      'Development Status :: 3 - Alpha',
      'Environment :: Console',
      'Intended Audience :: End Users/Desktop',
      'Intended Audience :: System Administrators',
      'Operating System :: Unix',
      'Operating System :: POSIX',
      'Programming Language :: Python :: 2.6',
      'Programming Language :: Python :: 2.7',
      'Topic :: Utilities',
    ],
    zip_safe = False,
)

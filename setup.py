#!/usr/bin/env python
#
# Copyright 2013 Mark Gao
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.version_info < (2, 5):
    raise NotImplementedError("Sorry, you need at least Python 2.5 or"
                              " Python 3.x to use bottle.")

import rossion

setup(name="rossion",
      version=rossion.__version__,
      py_modules=['rossion'],
      author=rossion.__author__,
      author_email="gx@stoneopus.com",
      url="https://github.com/markgao/rossion",
      license="http://www.apache.org/licenses/LICENSE-2.0",
      description="Fast and simple session module for tornado app",
      long_description=rossion.__doc__,
      platforms="any",
      install_requires=[
          "pylibmc>=1.5.0",
      ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ]
)
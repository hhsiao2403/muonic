#! /usr/bin/env python

from distutils.core import setup

import os

os.mkdir(os.getenv('HOME') + os.sep + 'muonic_data')

setup(name='muonic',
      version='1.0',
      description='Software to work with QNet DAQ cards',
      author='Robert Franke',
      url='http://code.google.com/p/muonic/',
      packages=['muonic','muonic.analyis','muonic.gui','muonic.daq'],
      scripts=['muonic'],
      package_data={'docs' : ['docs/*']}, 
      data_files=[('',['README']),('',['COPYING']),('',['simdaq.txt'])]
      )

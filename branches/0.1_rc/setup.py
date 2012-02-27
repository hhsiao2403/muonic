#! /usr/bin/env python

from distutils.core import setup

import os

setup(name='muonic',
      version='1.0',
      description='Software to work with QNet DAQ cards',
      author='Robert Franke',
      url='http://code.google.com/p/muonic/',
      packages=['muonic','muonic.analysis','muonic.gui','muonic.daq','muonic.gui.live'],
      scripts=['scripts/muonic'],
      #package_dir={'muonic' : 'muonic'},
      package_data={'' : ['docs/*','README'], 'muonic': ['daq/simdaq.txt','daq/which_tty_daq']}, 
      include_package_data=True,
      data_files=[(os.getenv('HOME') + os.sep + 'muonic_data',[])]
      )



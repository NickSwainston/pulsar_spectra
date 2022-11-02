#! /usr/bin/env python
"""
Setup for pulsar_spectra
"""
import os
from setuptools import setup

reqs = [
        'numpy>=1.13.3',
        'matplotlib>=3.4.0',
        'psrqpy>=1.0.5',
        'iminuit>=2.11.1',
        'jacobi',
        'PyYAML',
        'panda<=1.3.5',
        'sympy',
       ]

pulsar_spectra_version = '2.0.0'

setup(name="pulsar_spectra",
      version=pulsar_spectra_version,
      description="A simple interface to record pulsar's flux density measurements for a large number of papers and perform fitting of spectral models. ",
      url="https://github.com/NickSwainston/pulsar_spectra.git",
      packages=['pulsar_spectra'],
      package_data={'pulsar_spectra':['catalogue_papers/*.yaml', 'catalogue_papers/*.db']},
      scripts=["scripts/quick_fit.py"],
      python_requires='>=3.7',
      install_requires=reqs,
      setup_requires=['pytest-runner'],
      tests_require=['pytest']
)
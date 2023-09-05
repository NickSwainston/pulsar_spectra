#! /usr/bin/env python
"""
Setup for pulsar_spectra
"""
import re
from setuptools import setup

reqs = [
    'numpy>=1.13.3',
    'matplotlib>=3.4.0',
    'psrqpy>=1.2.4',
    'iminuit>=2.11.1',
    'jacobi',
    'PyYAML',
    'panda<=1.3.5',
]

VERSIONFILE="pulsar_spectra/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(name="pulsar_spectra",
    version=verstr,
    description="A simple interface to record pulsar's flux density measurements for a large number of papers and perform fitting of spectral models. ",
    url="https://github.com/NickSwainston/pulsar_spectra.git",
    packages=['pulsar_spectra'],
    package_data={'pulsar_spectra':['catalogue_papers/*.yaml', 'catalogue_papers/*.db', 'configs/*.yaml', 'configs/*.csv']},
    scripts=["scripts/quick_fit.py", "scripts/build_plotting_config.py"],
    python_requires='>=3.7',
    install_requires=reqs,
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
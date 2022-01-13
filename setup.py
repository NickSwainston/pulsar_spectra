#! /usr/bin/env python
"""
Setup for pulsar_spectra
"""
import os
import sys
from setuptools import setup
from subprocess import check_output


#The following two functions were taken from the repo: https://github.com/pyfidelity/setuptools-git-version/blob/master/setuptools_git_version.py
def format_version(version, fmt='{tag}.{commitcount}'):
    parts = version.split('-')
    if len(parts) == 1:
        return parts[0]
    assert len(parts) in (3, 4)
    dirty = len(parts) == 4
    tag, count, sha = parts[:3]
    if count == '0' and not dirty:
        return tag
    return fmt.format(tag=tag, commitcount=count)

def get_git_version():
    git_version = check_output('git describe --tags --long --dirty --always'.split()).decode('utf-8').strip()
    return format_version(version=git_version)

def download_ANTF_pulsar_database_file(datadir):
    # Hard code the path of the ATNF psrcat database file
    ATNF_LOC = os.path.join(datadir, 'psrcat.db')
    # Check if the file exists, if not download the latest zersion
    if not os.path.exists(ATNF_LOC):
        # Importing download functions here to avoid unnessiary imports when the file is available
        import urllib.request
        import gzip
        import shutil
        import tarfile
        print("The ANTF psrcat database file does not exist. Downloading it from www.atnf.csiro.au")
        # Download the file
        psrcat_zip_dir = urllib.request.urlretrieve('https://www.atnf.csiro.au/research/pulsar/psrcat/downloads/psrcat_pkg.tar.gz')[0]
        # Unzip it
        with gzip.open(psrcat_zip_dir,  'rb') as f_in:
            with open('psrcat_pkg.tar', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        # Untar the file we require
        psrcat_tar = tarfile.open(psrcat_zip_dir)
        # Do some python magic to no download the file within it's subdirectory from
        # https://stackoverflow.com/questions/8405843/python-extract-using-tarfile-but-ignoring-directories
        member = psrcat_tar.getmember('psrcat_tar/psrcat.db')
        member.name = os.path.basename(member.name)
        psrcat_tar.extract(member, path=datadir)
        print("Download complete")
        os.remove("psrcat_pkg.tar")

reqs = [
        'numpy>=1.13.3',
        'matplotlib>=2.1.0',
        'psrqpy>=1.0.5',
        'iminuit'
       ]

# Download the ANTF_pulsar_database_file file if it doesn't exist
datadir = os.path.join(os.path.dirname(__file__), 'pulsar_spectra', 'catalogues')
download_ANTF_pulsar_database_file(datadir)


pulsar_spectra_version = get_git_version()
#make a temporary version file to be installed then delete it
with open('version.py', 'a') as the_file:
    the_file.write('__version__ = "{}"\n'.format(pulsar_spectra_version))

setup(name="pulsar_spectra",
      version=pulsar_spectra_version,
      description="A simple interface to record pulsar's flux density measurements for a large number of papers and perform fitting of spectral models. ",
      url="https://github.com/NickSwainston/pulsar_spectra.git",
      packages=['pulsar_spectra'],
      package_data={'pulsar_spectra':['catalogues/*.json', 'catalogues/*.db']},
      python_requires='>=3.6',
      install_requires=reqs,
      setup_requires=['pytest-runner'],
      tests_require=['pytest']
)

# remove files
os.remove('version.py')
if os.path.isfile('record.txt'):
    os.remove('record.txt')
import os
import sys
from subprocess import Popen, PIPE
from setuptools import setup
if sys.version_info[0] >= 3:
    from distutils.command.build_py import build_py_2to3 as build_py
    from distutils.command.build_scripts import build_scripts_2to3 as build_scripts
else:
    from distutils.command.build_py import build_py
    from distutils.command.build_scripts import build_scripts

PACKAGE = "RPISlotFilling"
NAME = "RPISlotFilling"
DESCRIPTION = "RPI BLENDER Chinese Slot Filling System"
AUTHOR = "Boliang Zhang"
AUTHOR_EMAIL = "zhangb8@rpi.edu"
URL = "https://github.com/zblol/Chinese_SF"
VERSION = "1.0"

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

path = os.path.dirname(os.path.realpath(__file__))

# install JCC which is required by Pylucene
jcc_path = os.path.join(path, 'externals/pylucene-4.10.1-1/jcc')

os.chdir(jcc_path)

print('Building JCC...'),
p = Popen(['python', 'setup.py', 'build'], stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
print(stdout)
print(stderr)
print('Done')

print('Installing JCC...'),
p = Popen(['python', 'setup.py', 'install'], stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
print(stdout)
print(stderr)
print('Done')


# install pylucene
pylucene_path = os.path.join(path, 'externals/pylucene-4.10.1-1')
os.chdir(pylucene_path)

print('Building Pylucene...'),
p = Popen(['make'], stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
print(stdout)
print(stderr)
print('Done')

print('Installing Pylucene...'),
p = Popen(['make', 'install'], stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
print(stdout)
print(stderr)
print('Done')


# python setup to install dependency packages
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=read("README.md"),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=[
        "pexpect >= 2.4",
        "xmltodict >= 0.4.6",
        "jianfan >= 0.0.2",
        "jinja2 >= 2.7.3",

    ],
    # data_files = [
    #     ('corenlp', ["default.properties"]),
    # ],
    # package_data=find_package_data(
    #     PACKAGE,
    #     only_in_packages=False
    # )
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Programming Language :: Python",
    ],
)

import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()



# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
install_requires=[
   "altgraph==0.17.2",
   "asgiref==3.5.2",
   "backports.zoneinfo==0.2.1",
   "Django==4.0.5",
   "pycairo==1.21.0",
   "PyGObject==3.42.2",
   "sqlparse==0.4.2",
   "certifi==2022.6.15",
   "charset-normalizer==2.1.0",
   "idna==3.3",
   "pyserial==3.5",
   "requests==2.28.1",
   "urllib3==1.26.11",
]

setup(
    name = "lockers",
    entry_points = {
    'console_scripts': ['lockers=lockers:main'],
    },
    version = "0.0.1",
    py_modules=['lockers','manage'],
    #scripts=['requirements.txt'],
    author = "Wael El-begearmi",
    author_email = "waelabbas@live.com",
    description = ("Smart lockers management Application"),
    license = "BSD",
    keywords = "ftrina smart lockers ",
    url = "https://www.ftrina.com",
    packages=['cl','static','templates','web'],
    include_package_data=True,
    package_data = {
    'templates': ['*.html']
    },
    long_description=read('README'),
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Environment :: X11 Applications :: GTK",
        "Framework :: Django :: 4.0.5",
        "Intended Audience :: logistics",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",

    ],
)

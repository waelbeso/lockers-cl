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
install_requires = [
    "altgraph==0.17.4",
    "asgiref==3.8.1",
    "certifi==2024.8.30",
    "charset-normalizer==3.4.0",
    "Django==5.1.3",
    "idna==3.10",
    "packaging==24.1",
    "pillow==11.0.0",
    "pyelftools==0.31",
    "pyinstaller==6.11.0",
    "pyinstaller-hooks-contrib==2024.9",
    "pypng==0.20220715.0",
    "pyserial==3.5",
    "qrcode==7.4.2",
    "requests==2.32.3",
    "sqlparse==0.5.1",
    "typing_extensions==4.12.2",
    "urllib3==2.2.3",
]

desktop_extras = [
    "PyGObject==3.48.2",
    "pycairo==1.26.0",
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
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    install_requires=install_requires,
    extras_require={
        "desktop": desktop_extras,
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Environment :: X11 Applications :: GTK",
        "Framework :: Django :: 5.1",
        "Intended Audience :: Logistics",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",

    ],
)

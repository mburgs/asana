from setuptools import setup, find_packages
from asana import __version__ as version

install_requires = []

try:
    import requests
except ImportError:
    install_requires.append("requests")

name = "asana"

setup(
    name = name,
    version = version,
    author = "Michoel Burger",
    author_email = "burgercho@gmail.com",
    description = "Asana API wrapper with an ORM interface",
    license = "Apache License, (2.0)",
    keywords = "asana",
    url = "http://github.com/mburgs/asana",
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    install_requires=install_requires,
    )
#! /usr/bin/env python

from setuptools import setup, find_packages

install_requires = ["requests"]

name = "asanorm"

setup(
    name = name,
    version = "0.1.1",
    author = "Michoel Burger",
    author_email = "burgercho@gmail.com",
    description = "Asana API wrapper with an ORM interface",
    license = "Apache License, (2.0)",
    keywords = "asana,api,orm",
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
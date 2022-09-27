# Standard Library
from os import getenv

# Third Party
from setuptools import setup


def get_required_packages():
    with open('requirements.txt') as f:
        return f.read().splitlines()


setup(
 install_requires=get_required_packages(),
 version="0.0.0"
)

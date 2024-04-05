from setuptools import setup

def get_required_packages():
    with open('requirements.txt') as f:
        return f.read().splitlines()

setup(
 install_requires=get_required_packages()
)

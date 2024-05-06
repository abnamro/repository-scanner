# Repository Scanner Helm Wizard (resc-helm-wizard)
[![Python][python-shield]][python-url]
[![CI][ci-shield]][ci-url]

<!-- TABLE OF CONTENTS -->
## Table of contents
1. [About the component](#about-the-component)
2. [Getting started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Usage](#usage)
    - [Run helm-values-wizard locally from source](#run-helm-values-wizard-locally-from-source)
3. [Testing](#testing)
    - [Run unit tests, linting and import checks locally](#run-unit-tests-linting-and-import-checks-locally)

<!-- ABOUT THE COMPONENT -->
## About the component
The helm values wizard is an interactive CLI tool to generate the values yaml file which can be used for helm deployment of RESC.
On successful run, this CLI produces custom-values.yaml file in resc-helm-wizard directory.  


<!-- GETTING STARTED -->
## Getting started

These instructions will help you to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
- [Git](https://git-scm.com/downloads)
- [Python (v3.12.0 or higher)](https://www.python.org/downloads/release/python-3120/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Kubernetes](https://kubernetes.io/)
- [Helm](https://helm.sh/)

### Usage
Install the package:
```bash
pip install resc-helm-wizard
```

Run the wizard: 
```bash
resc-helm-wizard
```
![RESC-Installation](./images/RESC_Installation.gif)

### Run helm-values-wizard locally from source
Run the following commands in a Git Bash or Linux terminal.
 #### Clone the repository:
  ```bash
  git clone -b <branch_name> https://github.com/abnamro/repository-scanner.git
  cd ./deployment/resc-helm-wizard
  ```

  #### Create virtual environment (in Linux/MacOS):
  ```bash
  pip install virtualenv
  virtualenv venv
  source venv/Scripts/activate
  ```

#### Create virtual environment (in Windows):
  ```bash
  pip install virtualenv
  virtualenv venv
  venv/Scripts/activate
  ```

 #### Install resc-helm-wizard package:
  ```bash
  pip install -e .
  ```

 #### Run the resc-helm-wizard CLI (DOES NOT work in git-bash):
  ```bash
  resc-helm-wizard
  ```

## Testing
[(Back to top)](#table-of-contents)

### Run unit tests, linting and import checks locally:
See below commands for running various (unit/linting) tests locally. To run these tests you need to install [tox](https://pypi.org/project/tox/). This can be done on Linux and Windows with Git Bash.

Run below commands to make sure that the unit tests are running and that the code matches quality standards:
```bash
pip install tox         # install tox locally

tox run -e py -v        # Run this command to run the unit tests
tox run -e isort -v     # Run this command to validate the import sorting
tox run -e pylint -v    # Run this command for Python static code analysis
tox run -e flake8 -v    # Run this command for Python linting
```

<!-- MARKDOWN LINKS & IMAGES -->
[python-shield]: https://img.shields.io/badge/Python-3670A0?style=flat&logo=python&logoColor=ffdd54
[python-url]: https://www.python.org
[ci-shield]: https://img.shields.io/github/actions/workflow/status/abnamro/repository-scanner/helm-wizard-ci.yaml?style=flat&logo=github
[ci-url]: https://github.com/abnamro/repository-scanner/actions/workflows/helm-wizard-ci.yaml
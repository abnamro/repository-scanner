# Repository Scanner Version Control System Scanner (RESC-VCS-SCANNER)
<!-- TABLE OF CONTENTS -->
## Table of Contents
1. [About The Component](#about-the-component)
2. [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Run locally from source](#run-locally-from-source)
    - [Run locally using docker](#run-locally-using-docker)
3. [Testing](#testing)

<!-- ABOUT THE COMPONENT -->
## About The Component
The RESC-VCS-Scanner component uses the Gitleaks binary file to scan the source code for secrets.

<!-- GETTING STARTED -->
## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
- Install Docker Desktop
- Install [Python 3.9.0](https://www.python.org/downloads/release/python-390/)

### Run locally from source

Clone the repository and install the resc_vcs_scanner package locally:
```
git clone -b <branch-name> <repository-scanner repo url>
cd components/resc-vcs-scanner
pip install -e .
```

### Run locally using Docker
Build the resc-vcs-scanner docker image locally by running the following commands (Keep the image version parameter in mind):

- Pull the docker image from registry: 
```
docker pull ghcr.io/abnamro/resc-vcs-scanner:0.0.1
```
- Alternatively, build the docker image locally by running: 
```
docker build -t ghcr.io/abnamro/resc-vcs-scanner:0.0.1 .
```
- Run the RESC-VCS-SCANNER by using the following command: 
```
docker run --name resc-vcs-scanner ghcr.io/abnamro/resc-vcs-scanner:0.0.1
```

### Run locally using the CLI
It is also possible to run the component through the CLI for a different approach to scanning VCS repositories. 
This is done by navigating through the project to the resc-vcs-scanner component and executing the "secret_scanner" command:

```
cd components/resc-vcs-scanner
pip install -e .
secret_scanner --help
```

Running this command will prompt a list of flags/arguments that you need to specify to run this command. This will look
something like this:

```
usage: secret_scanner [-h] [--repo-info REPO_INFO] [--repo-url REPO_URL] [--repo-dir REPO_DIR] [--repo-name REPO_NAME] [--sts-url STS_URL] [--vcs-instances VCS_INSTANCES] [--temporary-path TEMPORARY_PATH] [--username USERNAME] [--password] [--branches BRANCHES [BRANCHES ...]] [--gitleaks-path GITLEAKS_PATH]
                      --gitleaks-rules-path GITLEAKS_RULES_PATH [--force-base-scan]

optional arguments:                                                                                                                                                                                                                                                                                                 
  -h, --help            show this help message and exit                                                                                                                                                                                                                                                             
  --repo-info REPO_INFO
                        Path to the JSON file containing the repository info
  --repo-url REPO_URL   url to repository you want to scan
  --repo-dir REPO_DIR   The path to the directory where the repo is located
  --repo-name REPO_NAME
                        The name of the repository
  --sts-url STS_URL     The URL to the secret tracking service to which the scan results should be written
  --vcs-instances VCS_INSTANCES
                        Path to the json file containing the vcs instances definitions
  --temporary-path TEMPORARY_PATH
  --username USERNAME
  --password
  --branches BRANCHES [BRANCHES ...]
  --gitleaks-path GITLEAKS_PATH
                        Path to the gitleaks binary. Can also be provided via the GITLEAKS_PATH environment variable
  --gitleaks-rules-path GITLEAKS_RULES_PATH
                        Path to the gitleaks rules file.
  --force-base-scan
```

Where one of the more interesting arguments being the `--gitleaks-rules-path` argument. This argument needs to be filled
with a GitLeaks rule file. To get a GitLeaks rule file you can execute the following command to get a default one:

```
curl https://raw.githubusercontent.com/zricethezav/gitleaks/master/config/gitleaks.toml > gitleaks.toml
echo 'version = "0.0.1"' | cat - gitleaks.toml > temp && mv temp gitleaks.toml
```

To get a full idea of how to run this command with all these arguments involved, an example of executing this command
is attached below:

```
secret_scanner  --repo-url=<repository url> --gitleaks-rules-path=<path to gitleaks toml rule> --gitleaks-path=<path to gitleaks binary>
```

## Testing
In order to run (unit/linting) tests locally, there are several command specified below on how to run these tests.
To run these tests you need to install tox this can be done on Linux and Windows, where or the latter you can use GIT Bash.

To make sure the unit tests are running and that the code matches quality standards run:
```
pip install tox      # install tox locally

tox -v -e sort       # Run this command to validate the import sorting
tox -v -e lint       # Run this command to lint the code according to this repository's standard
tox -v -e -e pytest  # Run this command to run the unit tests
tox -v               # Run this command to run all of the above tests
```


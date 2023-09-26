# Repository Scanner Version Control System Scanner (RESC-VCS-SCANNER)
<h3>
         <a href="https://github.com/abnamro/repository-scanner/actions">
            <img src="https://img.shields.io/github/actions/workflow/status/abnamro/repository-scanner/vcs-scanner-ci.yaml?logo=github">
        </a>
        <a href="https://sonarcloud.io/summary/new_code?id=abnamro-resc_resc-vcs-scanner">
            <img src="https://sonarcloud.io/api/project_badges/measure?project=abnamro-resc_resc-vcs-scanner&metric=alert_status">
        </a>
</h3>

<!-- TABLE OF CONTENTS -->
## Table of contents
1. [About the component](#about-the-component)
2. [Getting started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Run locally from source](#run-locally-from-source)
    - [Run locally using docker](#run-locally-using-docker)
3. [Testing](#testing)

<!-- ABOUT THE COMPONENT -->
## About the component
The RESC-VCS-Scanner component uses the Gitleaks binary file to scan the source code for secrets.

<!-- GETTING STARTED -->
## Getting started

These instructions will help you to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
- [Git](https://git-scm.com/downloads)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Python 3.9.0](https://www.python.org/downloads/release/python-390/)

### Run locally from source
<details>
  <summary>Preview</summary>

  **Prerequisites:**   
  * RabbitMQ and RESC web service must be up and running locally.</br>
  If you have already deployed RESC through helm in Kubernetes, then rabbitmq and resc webservice are already running for you.</br> 
  * Install Gitleaks [v8.8.8](https://github.com/zricethezav/gitleaks/releases/tag/v8.8.8) on your system.
  * Download the rule config toml file to `/tmp/temp_resc_rule.toml` location by running below command from a Git Bash terminal.
  * Send some repositories to 'repositories' topics of RabbitMQ server by referring the README of RESC-VCS-SCRAPER component.

  ```bash
  curl https://raw.githubusercontent.com/zricethezav/gitleaks/master/config/gitleaks.toml > /tmp/temp_resc_rule.toml
  ```

  Clone the repository, open the Git Bash terminal from /components/resc-vcs-scanner folder, and run below commands.  

  #### 1. Create virtual environment:
  ```bash
  cd components/resc-vcs-scanner
  pip install virtualenv
  virtualenv venv
  source venv/Scripts/activate
  ```
 #### 2. Install resc_vcs_scanner package:
  ```bash
  pip install -e .
  ```
 #### 3. Set below environment variables:

 ```bash
  export RESC_RABBITMQ_SERVICE_HOST=127.0.0.1   #  The hostname/IP address of the rabbitmq server
  export RESC_RABBITMQ_SERVICE_PORT_AMQP=30902  #  The amqp port of the rabbitmq server
  export RABBITMQ_DEFAULT_VHOST=resc-rabbitmq   #  The virtual host name of the rabbitmq server
  export RABBITMQ_USERNAME=queue_user    #  The username used to connect to the rabbitmq projects and repositories topics
  export RABBITMQ_PASSWORD="" # The password used to connect to the rabbitmq projects and repositories topics can be found for the value of queues_password field in /deployment/kubernetes/example-values.yaml file
  export RABBITMQ_QUEUE=repositories # The name of the queue from which secret scanner will read repositories
  export RESC_API_NO_AUTH_SERVICE_HOST=127.0.0.1 #  The hostname/IP address where RESC web service is running
  export RESC_API_NO_AUTH_SERVICE_PORT=30900  #  The port number where RESC web service is running
  export VCS_INSTANCES_FILE_PATH="" # The absolute path to vcs_instances_config.json file containing the vcs instances definitions
  export GITHUB_PUBLIC_USERNAME="" # Your GitHub username
  export GITHUB_PUBLIC_TOKEN="" #  Your GitHub personal access token
  export GITLEAKS_PATH="" # The absolute path to gitleaks binary executable
 ```
 
 You need to replace the following values with your custom values: RABBITMQ_PASSWORD, VCS_INSTANCES_FILE_PATH, GITHUB_PUBLIC_USERNAME, GITHUB_PUBLIC_TOKEN and GITLEAKS_PATH.  

 #### Structure of vcs instances config json
The vcs_instances_config.json file must have the following format: 
_**Note:**_ You can add multiple vcs instances.

<details>
  <summary>Preview</summary>

Example:
```json
{
  "vcs_instance_1": {
    "name": "GITHUB_PUBLIC",
	"scope": ["kubernetes"], 
    "exceptions": [],
    "provider_type": "GITHUB_PUBLIC",
    "hostname": "github.com",
    "port": "443",
    "scheme": "https",
    "username": "GITHUB_PUBLIC_USERNAME",
    "token": "GITHUB_PUBLIC_TOKEN",
    "organization": ""
  }
}
```
* scope: List of GitHub accounts you want to scan.
  For example, lets'say you want to scan all the repositories for the following GitHub accounts.
  https://github.com/kubernetes  
  https://github.com/docker
  
  Then you need to add those accounts to scope like: ["kubernetes", "docker"]. All the repositories from those accounts will be scanned. 
* exceptions (optional): If you want to exclude any account from scan, then add it to exceptions. Default is empty exception.

The **output** messages of `collect_projects` command has the following format:

```json
{
  "project_key": "kubernetes",
  "vcs_instance_name": "GITHUB_PUBLIC",
}
```
</details>

 #### 4. Run the secret scan task:  
  This task reads the repositories from a RabbitMQ channel called 'repositories', runs scan using [Gitleaks](https://github.com/zricethezav/gitleaks) and saves the findings' metadata to database. 

  This can be done via the following command:  
  ```bash
  celery  -A  vcs_scanner.secret_scanners.celery_worker worker --loglevel=INFO -E -Q repositories --concurrency=1  --prefetch-multiplier=1
```
</details>

### Run locally using docker
<details>
  <summary>Preview</summary>
Run the RESC VCS Scanner docker image locally by running the following commands:  

- Pull the docker image from registry: 
```bash
docker pull rescabnamro/resc-vcs-scanner:latest
```

- Alternatively, build the docker image locally by running: 
```bash
docker build -t rescabnamro/resc-vcs-scanner:latest .
```

- Run the vcs-scanner by using below command: 
```bash
docker run -v <path to vcs_instances_config.json in your local system>:/tmp/vcs_instances_config.json -e RESC_RABBITMQ_SERVICE_HOST="host.docker.internal" -e RESC_RABBITMQ_SERVICE_PORT_AMQP=30902 -e RABBITMQ_DEFAULT_VHOST=resc-rabbitmq -e RABBITMQ_USERNAME=queue_user -e RABBITMQ_PASSWORD="<the password of queue_user>" -e RABBITMQ_QUEUE="repositories" -e RESC_API_NO_AUTH_SERVICE_HOST="host.docker.internal" -e RESC_API_NO_AUTH_SERVICE_PORT=30900 -e VCS_INSTANCES_FILE_PATH="/tmp/vcs_instances_config.json" -e GITHUB_PUBLIC_USERNAME="<your github username>" -e GITHUB_PUBLIC_TOKEN="<your github personal access token>" -e GITLEAKS_PATH="/vcs_scanner/gitleaks_config/seco-gitleaks-linux-amd64" --name resc-vcs-scanner rescabnamro/resc-vcs-scanner:latest celery  -A vcs_scanner.secret_scanners.celery_worker worker --loglevel=INFO -E -Q repositories --concurrency=1  --prefetch-multiplier=1
```

To create vcs_instances_config.json file please refer to: [Structure of vcs_instances_config.json](#structure-of-vcs-instances-config-json)
</details>

### Run locally as a CLI tool (Still in development) 

<details>
  <summary>Preview</summary>

  It is also possible to run the component as a CLI tool to scan VCS repositories.
  #### 1. Create virtual environment:
  ```bash
  cd components/resc-vcs-scanner
  pip install virtualenv
  virtualenv venv
  source venv/Scripts/activate
  ```
 #### 2. Install resc_vcs_scanner package:
  ```bash
  pip install -e .
  ```
 #### 3. Run CLI scanner:
The CLI has 3 modes of operation, please make use of the --help argument to see all the options for the modes:
- Scanning a non-git directory: 
  ```bash
  secret_scanner dir --help
  secret_scanner dir --gitleaks-rules-path=<path to gitleaks toml rule> --gitleaks-path=<path to gitleaks binary> --dir=<directory to scan>
  ```

- Scanning an already cloned git repository: 
  ```bash
  secret_scanner repo local --help
  secret_scanner repo local --gitleaks-rules-path=<path to gitleaks toml rule> --gitleaks-path=<path to gitleaks binary> --dir=<directory of repository to scan>
  ```

- Scanning a remote git repository: 
  ```bash
  secret_scanner repo remote --help
  secret_scanner repo remote --gitleaks-rules-path=<path to gitleaks toml rule> --gitleaks-path=<path to gitleaks binary> --repo-url=<url of repository to scan>
  ```
Most CLI arguments can also be provided by setting the corresponding environment variable. 
Please see the --help options on the arguments that can be provided using environment variables, and the expected environment variable names.
These will always be prefixed with RESC_

Example: the argument **--gitleaks-path** can be provided using the environment variable **RESC_GITLEAKS_PATH**
</details>

## Testing 
Run below commands to make sure that the unit tests are running and that the code matches quality standards:

_**Note:**_ To run these tests you need to install [tox](https://pypi.org/project/tox/). This can be done on Linux and Windows with Git Bash.
```bash
pip install tox      # install tox locally

tox -v -e sort       # Run this command to validate the import sorting
tox -v -e lint       # Run this command to lint the code according to this repository's standard
tox -v -e pytest     # Run this command to run the unit tests
tox -v               # Run this command to run all of the above tests
```


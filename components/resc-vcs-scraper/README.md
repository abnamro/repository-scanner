# Repository Scanner Version Control System Scraper (RESC-VCS-SCRAPER)

<!-- TABLE OF CONTENTS -->
## Table of Contents
1. [About the component](#about-the-component)
2. [Getting started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Run locally from source](#run-locally-from-source)
    - [Run locally using docker](#run-locally-using-docker)
3. [Testing](#testing)


<!-- ABOUT THE COMPONENT -->
## About the component
The RESC-VCS-Scraper component collects all projects and repositories from multiple VCS providers. The supported VCS providers are Bitbucket, Azure Repos, and GitHub.

This component includes two main modules, the project collector and the repository collector.
The project collector collects all projects and sends them to the project queue. The repository collector collects projects from the projects queue, fetches its corresponding repositories, and sends them to the repository queue.

<!-- GETTING STARTED -->
## Getting started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
- [Git](https://git-scm.com/downloads)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Python 3.9.0](https://www.python.org/downloads/release/python-390/)

### Run locally from source
<details>
  <summary>Preview</summary>
  <b>Prerequisites:</b> RabbitMQ must be up and running locally.</br>
  If you have already deployed RESC through helm in Kubernetes, then rabbitmq is already running for you.</br> 
  Clone the repository, open the Git Bash terminal from /components/resc-vcs-scraper folder, and run below commands.  

  #### 1. Create virtual environment:
  ```bash
  cd components/resc-vcs-scraper
  pip install virtualenv
  virtualenv venv
  source venv/Scripts/activate
  ```
 #### 2. Install resc_vcs_scraper package:
  ```bash
  pip install -e .
  ```
 #### 3. Set below environment variables:

 ```bash
  export RESC_RABBITMQ_SERVICE_HOST=127.0.0.1   #  The hostname/IP address of the rabbitmq server
  export RESC_RABBITMQ_SERVICE_PORT_AMQP=30902  #  The amqp port of the rabbitmq server
  export RABBITMQ_DEFAULT_VHOST=resc-rabbitmq   #  The virtual host name of the rabbitmq server
  export RABBITMQ_QUEUES_USERNAME=queue_user    #  The username used to connect to the rabbitmq projects and repositories topics
  export RABBITMQ_QUEUES_PASSWORD="" # The password used to connect to the rabbitmq projects and repositories topics, can be found for the value of queues_password field in /deployment/kubernetes/example-values.yaml file
  export VCS_INSTANCES_FILE_PATH="" # The absolute path to vcs_instances_config.json file containing the vcs instances definitions
  export GITHUB_PUBLIC_USERNAME="" # Your GitHub username
  export GITHUB_PUBLIC_TOKEN="" #  Your GitHub personal access token
 ```
 
 You need to replace with correct values for RABBITMQ_QUEUES_PASSWORD, VCS_INSTANCES_FILE_PATH, GITHUB_PUBLIC_USERNAME and GITHUB_PUBLIC_TOKEN.  

 #### 4. Run the `collect_projects` task:  
  `collect_projects` task collects all projects from a given Version Control System Instance, then writes the found projects to a RabbitMQ channel called 'projects'. 

  This can be done via the command  
  ```bash
  collect_projects
```

#### Structure of vcs instances config json
The vcs_instances_config.json file must have the following format. 
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
  For example, lets'say you want to scan all the repositories for the following github accounts.
  https://github.com/kubernetes  
  https://github.com/docker
  
  Then you need to add those accounts to scope like : ["kubernetes", "docker"]. All the repositories from those accounts will be scanned. 
* exceptions (optional): If you want to exclude any account from scan, then add it to exceptions. Default is empty exception.

The **output** messages of `collect_projects` command has the following format:

```json
{
  "project_key": "kubernetes",
  "vcs_instance_name": "GITHUB_PUBLIC",
}
```
</details>

 #### 5. Run collect all repositories task:  
 This task collects all repositories from a single VCS project, then writes the found repositories to a RabbitMQ channel called 'repositories'.

  This can be done via the command:
   ```bash
   celery -A vcs_scraper.repository_collector.common worker --loglevel=INFO -E -Q projects
   ```
</details>

### Run locally using docker
<details>
  <summary>Preview</summary>
Run the RESC VCS Scraper docker image locally by running the following commands:

- Pull the docker image from registry: 
```bash
docker pull rescabnamro/resc-vcs-scraper:0.0.1
```

- Alternatively, build the docker image locally by running: 
```bash
docker build -t rescabnamro/resc-vcs-scraper:0.0.1 .
```

- Run the vcs-scraper by using below command:
```bash
docker run -v <path to vcs_instances_config.json in your local system>:/tmp/vcs_instances_config.json -e RESC_RABBITMQ_SERVICE_HOST="host.docker.internal" -e RESC_RABBITMQ_SERVICE_AMQP_PORT=30902 -e RABBITMQ_DEFAULT_VHOST=resc-rabbitmq -e RABBITMQ_QUEUES_USERNAME=queue_user -e RABBITMQ_QUEUES_PASSWORD="<the password of queue_user>" -e VCS_INSTANCES_FILE_PATH="/tmp/vcs_instances_config.json" -e GITHUB_PUBLIC_USERNAME="<your github username>" -e GITHUB_PUBLIC_TOKEN="<your github personal access token>" --name resc-vcs-scraper rescabnamro/resc-vcs-scraper:0.0.1 collect_projects  
```

To create vcs_instances_config.json file, refer: [Structure of vcs_instances_config.json](#structure-of-vcs-instances-config-json)
</details>

## Testing
[(Back to top)](#table-of-contents)

Run below commands to make sure that the unit tests are running and that the code matches quality standards:

_**Note:**_ To run these tests you need to install [tox](https://pypi.org/project/tox/). This can be done on Linux and Windows with Git Bash.
```bash
pip install tox      # install tox locally

tox -v -e sort       # Run this command to validate the import sorting
tox -v -e lint       # Run this command to lint the code according to this repository's standard
tox -v -e pytest     # Run this command to run the unit tests
tox -v               # Run this command to run all of the above tests
```

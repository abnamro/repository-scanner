# Repository Scanner Version Control System Scraper (RESC-VCS-SCRAPER)

<!-- TABLE OF CONTENTS -->
## Table of Contents
1. [About The Component](#about-the-component)
2. [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Run locally](#run-locally)
    - [Usage](#usage)
    - [Run locally using docker](#run-locally-using-docker)
3. [Testing](#testing)


<!-- ABOUT THE COMPONENT -->
## About The Component
The RESC-VCS-SCRAPER component collects all projects and repositories from multiple VCS providers. The supported VCS providers are Bitbucket, Azure Repos and GitHub.

This component includes two main modules such as project collector and repository collector.
The project collector collects all projects and sends to projects queue. The repository collector collects projects from projects queue, fetches its corresponding repositories and send those to repositories queue.

<!-- GETTING STARTED -->
## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
- Install Docker Desktop;
- Install [Python 3.9.0](https://www.python.org/downloads/release/python-390/)

### Run locally

Please follow the below steps to run the project locally:
```
pip install -e .
<Set all required environment variables>
collect_projects
celery -A vcs_scraper.repository_collector.common worker --loglevel=INFO -E -Q projects
```
The required environment variables are below (use the `export` command for Linux or `SET` for Windows Machines):
>- *RABBITMQ_QUEUES_USERNAME*: The username used to connect to the rabbitmq project collector and repository collector topics.
>- *RABBITMQ_QUEUES_PASSWORD*: The password used to connect to the rabbitmq project collector and repository collector topics.
>- *RESC_RABBITMQ_SERVICE_HOST*: The hostname/IP address of the rabbitmq server.
>- *RABBITMQ_DEFAULT_VHOST*: The virtual host name of the rabbitmq server.
>- *VCS_INSTANCES_FILE_PATH*: The absolute path to the json file containing the vcs_instances_definitions.

### Usage

The vcs-scraper offers 2 main functionalities:

1. Collecting all projects from a given Version Control System Instance, the default behavior is to write the found projects to a RabbitMQ channel called 'projects'.
   This can be done via the command: `collect_projects`

   > This command takes the following environment variables as **input** (use the `export` command for Linux or `SET` for Windows Machines):
   >- *RABBITMQ_QUEUES_USERNAME*: The username used to connect to the rabbitmq project collector and repository collector topics.
   >- *RABBITMQ_QUEUES_PASSWORD*: The password used to connect to the rabbitmq project collector and repository collector topics.
   >- *RESC_RABBITMQ_SERVICE_HOST*: The hostname/IP address of the rabbitmq server.
   >- *RABBITMQ_DEFAULT_VHOST*: The virtual host name of the rabbitmq server.
   >- *VCS_INSTANCES_FILE_PATH*: The absolute path to the json file containing the vcs_instances_definitions.

This JSON file must have the following format:
```
{
  "vcs_instance_1": {
    "name": "vcs_instance_1",
    "exceptions": [],
    "provider_type": "AZURE_DEVOPS",
    "hostname": "dev.azure.com",
    "port": "443",
    "scheme": "https",
    "username": "VCS_INSTANCE_USERNAME",
    "token": "VCS_INSTANCE_TOKEN",
    "scope": [],
    "organization": "org"
  },
  "vcs_instance_2": {
    "name": "vcs_instance_2",
    "exceptions": [],
    "provider_type": "BITBUCKET",
    "hostname": "bitbucket.com",
    "port": "1234",
    "scheme": "https",
    "username": "VCS_INSTANCE_USERNAME",
    "token": "VCS_INSTANCE_TOKEN",
    "scope": []
  }
}
```

The **output** messages of this command have the following format:

```
{
  "project_key": project_name,
  "vcs_instance_name": vcs_instance_name,
}
```

2. Collecting all repositories from a single VCS project, the default behavior is to write the found projects to a RabbitMQ channel called 'repositories'.
   This can be done via the command:
   `celery -A vcs_scraper.repository_collector.common worker --loglevel=INFO -E -Q projects`

>This Celery worker takes the following environment variables as **input** (use the `export` command for Linux or `SET` for Windows Machines):
>- *RABBITMQ_QUEUES_USERNAME*: The username used to connect to the rabbitmq project collector and repository collector topics.
>- *RABBITMQ_QUEUES_PASSWORD*: The password used to connect to the rabbitmq project collector and repository collector topics.
>- *RESC_RABBITMQ_SERVICE_HOST*: The hostname/IP address of the rabbitmq server.
>- *RABBITMQ_DEFAULT_VHOST*: The virtual host name of the rabbitmq server.
>- *VCS_INSTANCES_FILE_PATH*: The absolute path to the json file containing the vcs_instances_definitions.

This JSON file must have the following format:
```
{
  "vcs_instance_1": {
    "name": "vcs_instance_1",
    "exceptions": [],
    "provider_type": "AZURE_DEVOPS",
    "hostname": "dev.azure.com",
    "port": "443",
    "scheme": "https",
    "username": "VCS_INSTANCE_USERNAME",
    "token": "VCS_INSTANCE_TOKEN",
    "scope": [],
    "organization": "org"
  },
  "vcs_instance_2": {
    "name": "vcs_instance_2",
    "exceptions": [],
    "provider_type": "BITBUCKET",
    "hostname": "bitbucket.com",
    "port": "1234",
    "scheme": "https",
    "username": "VCS_INSTANCE_USERNAME",
    "token": "VCS_INSTANCE_TOKEN",
    "scope": []
  }
}
```
Project definitions to be read from the 'projects' channel hosted on the same rabbitmq instance as the output have the following format:
```
{
  "repository_name": "test-repo",
  "repository_id": 123,
  "repository_url": "https://fake-btbk.com/scm/test/test-repo.git",
  "project_key": "test",
  "vcs_instance_name": "bitbucket acceptance",
  "branches_info": [
    {"repository_id": 123,
      "branch_name": "master",
      "branch_id": "refs/heads/master",
      "last_scanned_commit": "e361cd94b5a4f3cc2fffffa9fdbdbc259c583ff9"},
    {"repository_id": 123,
      "branch_name": "main",
      "branch_id": "refs/heads/main",
      "last_scanned_commit": "e361cd94b5a4f3cc2fdfffa9fdbdbc259c583ff9"}
  ]
}

```

### Run locally using docker

- Install the docker image from the CLI: `docker pull ghcr.io/abnamro/resc-vcs-scraper:0.0.1`
- Build the docker image by running:`docker build -t abnamro/resc-vcs-scraper:0.0.1`
- Run the vcs-scraper by below command:
```
docker run -e RABBITMQ_QUEUES_USERNAME='test' -e RABBITMQ_QUEUES_PASSWORD='test' -e RESC_RABBITMQ_SERVICE_HOST='test-service-host' -e RABBITMQ_DEFAULT_VHOST='resc-rabbitmq' -e VCS_INSTANCES_FILE_PATH='<provide vcs_instance.json path>' --name resc-vcs-scraper resc/resc-vcs-scraper:local collect_projects
```

## Testing
[(Back to top)](#table-of-contents)

In order to run (unit/linting) tests locally, there are several command specified below on how to run these tests.
To run these tests you need to install tox this can be done on Linux and Windows, where or the latter you can use GIT Bash.

To make sure the unit tests are running and that the code matches quality standards run:
```
pip install tox      # install tox locally

tox -v -e sort       # Run this command to validate the import sorting
tox -v -e lint       # Run this command to lint the code according to this repository's standard
tox -v -e -e pytest  # Run this command to run the unittests
tox -v               # Run this command to run all the tests above
```

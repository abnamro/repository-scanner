# RESC/VCS-SCRAPER
Repository Scanner: Version Control Systems' scraper
 

# Summary
This repository contains the vcs-scraper component of the RESC framework.
This component takes care of collecting all projects and repositories in either **Bitbucket** or **Azure Code Repositories**

# Testing:
In order to make sure the unittests are running and that the code matches quality standards run:
```
pip install tox # install tox locally

export PYTHONPATH=./src/;tox -v -e sort       # Run this command to validate the import sorting
export PYTHONPATH=./src/;tox -v -e lint       # Run this command to lint the code according to this repository's standard
export PYTHONPATH=./src/;tox -v -e -e pytest  # Run this command to run the unittests
export PYTHONPATH=./src/;tox -v               # Run this command to run all the tests above
```


# Building:
You can build the docker image by running:
`docker build -t resc/vcs-scraper:local`

# Running:
```
prerequisit, run a rabbit MQ instance
pip install -e .
export RESC_RABBITMQ_SERVICE_HOST=localhost
collect_projects
celery -A vcs_scraper.repository_collector.common worker --loglevel=INFO -E -Q projects
```


# Deployment:
The vcs-scraper offers 2 main functionalities:

1- Collecting all projects from a given Version Control System Instance, the default behavior is to write the found projects to a RabbitMQ channel called 'projects'.
This can be done via the command: `collect_projects`

This command takes the following environment variables as **input**:
- **RABBITMQ_QUEUES_USERNAME**: The username used to connect to the rabbitmq project collector and repository collector topics.
- **RABBITMQ_QUEUES_PASSWORD**: The password used to connect to the rabbitmq project collector and repository collector topics.
- **RESC_RABBITMQ_SERVICE_HOST**: The hostname/IP address of the rabbitmq server.
- **RABBITMQ_DEFAULT_VHOST**: The virtual host name of the rabbitmq server.
- **VCS_INSTANCES_FILE_PATH**: The absolute path to the json file containing the vcs_instances_definitions.
This file must have the following format:
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


2- Collecting all repositories from a single VCS project, the default behavior is to write the found projects to a RabbitMQ channel called 'repositories'.
This can be done via the command: 
`celery -A vcs_scraper.repository_collector.common worker --loglevel=INFO -E -Q projects`

This Celery worker takes the following environment variables as **input**:
- **RABBITMQ_QUEUES_USERNAME**: The username used to connect to the rabbitmq project collector and repository collector topics.
- **RABBITMQ_QUEUES_PASSWORD**: The password used to connect to the rabbitmq project collector and repository collector topics.
- **RESC_RABBITMQ_SERVICE_HOST**: The hostname/IP address of the rabbitmq server.
- **RABBITMQ_DEFAULT_VHOST**: The virtual host name of the rabbitmq server.
- **VCS_INSTANCES_FILE_PATH**: The absolute path to the json file containing the vcs_instances_definitions.
  This file must have the following format:
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
- Project definitions to be read from the 'projects' channel hosted on the same rabbitmq instance as the output have the following format:
```
{
  "repository_name": "test-repo",
  "repository_id": 123,
  "repository_url": "https://fake-btbk.com/scm/test/test-repo.git",
  "project_key": "test",
  "vcs_instance_name": "bitbucket",
  "branches_info": [
    {"repository_info_id": 123,
      "branch_name": "master",
      "branch_id": "refs/heads/master",
      "last_scanned_commit": "e361cd94b5a4f3cc2fffffa9fdbdbc259c583ff9"},
    {"repository_info_id": 123,
      "branch_name": "main",
      "branch_id": "refs/heads/main",
      "last_scanned_commit": "e361cd94b5a4f3cc2fdfffa9fdbdbc259c583ff9"}
  ]
}

```

# Deployment via kubernetes:
Deployment is done via Kubernetes

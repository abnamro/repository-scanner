# RESC Deployment - Kubernetes

<!-- TABLE OF CONTENTS -->
## Table of Contents
1. [About The Component](#about-the-component)
2. [Technology Stack](#technology-stack)
3. [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Testing templates](#testing-templates)
    - [Deploying charts](#deploying-charts)
4. [Additional Information](#additional-information)
    - [Trigger Scanning](#trigger-scanning)


<!-- ABOUT THE COMPONENT -->
## About The Component
This component contains templates and charts for deploying of Repository Scanner (RESC) in a kubernetes infrastructure.

<!-- TECHNOLOGY STACK -->
## Technology Stack
* [Docker](https://www.docker.com/)
* [Kubernetes](https://kubernetes.io/)
* [Helm](https://helm.sh/)

<!-- GETTING STARTED -->
## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
#### (1) Install Softwares
* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* [Kubernetes](https://docs.docker.com/desktop/kubernetes/) - The simplest way to install kubernetes is to enable it from Docker Desktop. If you are going to install kubernetes using minikube then ensure the version is 1.21 or later.
* [Helm](https://helm.sh/docs/intro/install/)

#### (2) Populate RESC-RULE.toml file
RESC uses rules from [Gitleaks](https://github.com/zricethezav/gitleaks) to detect secrets.
Ensure you have the rule pack config file in TOML format available, which needs to be provided as deployment argument.
To download this GitLeaks rule you need to execute the following command in a git bash or linux terminal.

```
cd ./deployment/kubernetes/

curl https://raw.githubusercontent.com/zricethezav/gitleaks/master/config/gitleaks.toml > RESC-RULE.toml

echo 'version = "0.0.1"' | cat - RESC-RULE.toml > temp && mv temp RESC-RULE.toml
```

#### (3) Create persistent volume and update it in example-values.yaml
Create two folders i.e, database and raabitmq in your user folder as mentioned below.

Windows: C:\Users\<username>\resc\database and C:\Users\<username>\resc\rabbitmq  
Linux: /Users/<username>/var/resc/database and /Users/<username>/var/resc/rabbitmq  

Update persistent volume claim path for database.
```
Windows:
--------------
resc-database:
  database:
    pvc_path: "/run/desktop/mnt/host/c/Users/<username>/resc/database"

Linux:
--------------
resc-database:
  database:
    pvc_path: "/Users/<username>/var/resc/database"
```

Update persistent volume claim path for rabbitmq.
```
Windows:
--------------
resc-rabbitmq:
  rabbitMQ:
    pvc_path: "/run/desktop/mnt/host/c/Users/<username>/resc/rabbitmq"

Linux:
--------------
resc-rabbitmq:
  rabbitMQ:
    pvc_path: "/Users/<username>/var/resc/rabbitmq"
```

#### (4) Provide details of the accounts/projects to scan
You need to provide at least one vcs instance details to start scanning.
Here is an example to scan repositories from github.
* scope: List of github accounts you want to scan.
  For example, lets'say you want to scan all the repositories for the following github accounts.
  https://github.com/kubernetes  
  https://github.com/docker
  
  Then you need to add those accounts to scope like : ["kubernetes", "docker"]. All the repositories from those accounts will be scanned. 
* exceptions (optional): If you want to exclude any account from scan, then add it to exceptions. Default is empty exception.
* usernameValue: Provide your github username
* tokenValue: Provide your github personal access token



```
resc-vcs-instances:
  vcsInstances:
    ### Github ###
    - name: "GITHUB_PUBLIC"
      scope: ["kubernetes", "docker"]
      exceptions: []
      providerType: "GITHUB_PUBLIC"
      hostname: "github.com"
      port: "443"
      scheme: "https"
      username: "GITHUB_PUBLIC_USERNAME"
      usernameValue: "<enter your github username here>"
      organization: ""
      token: "GITHUB_PUBLIC_TOKEN"
      tokenValue: "<enter your github personal access token here>"
```

## Testing templates
In order to run (unit/linting) tests locally, naviagate to deployment/kubernetes folder.:
```
cd ./deployment/kubernetes/
```

helm lint: examine a chart for possible issues
```
helm lint . --set-file global.secretScanRulePackConfig=./RESC-RULE.toml to run helm linting.
```

Render chart templates locally and display the output.
```
helm template resc . -f ./example-values.yaml --set-file global.secretScanRulePackConfig=./RESC-RULE.toml
```

## Deploying charts 
Make sure you have completed the [pre-requisite](#prerequisites) steps.

* Ensure the namespace is created, if not then run 
  ```
  kubectl create namespace resc
  ```
* Naviagate to deployment/kubernetes folder.
  ```
  cd ./deployment/kubernetes/
  ```

* Deploy the helm charts  
  ```
  helm install --namespace resc resc . -f ./example-values.yaml --set-file global.secretScanRulePackConfig=./RESC-RULE.toml
  ```
  
* Optionally set the default namespace for all kubectl commands. Now you no longer need to specify the -n resc option for all the kubectl commands.
  ```
  kubectl config set-context --current --namespace=resc
  ```

* Give it a minute or two and then run below commands to verify the installation
  ```
  helm list -n resc
  kubectl get pods -n resc
  ```
  ![deployment-status-screenshot!](images/deployment-status.png)
* To upgrade the deployment run 
  ```
  helm upgrade --namespace resc resc . -f ./helm-context/example-values.yaml --set-file global.secretScanRulePackConfig=./RESC-RULE.toml
  ```
* To uninstall or delete the deployment
  ```
  helm uninstall resc --namespace resc
  ```

## Additional Information
### Trigger scanning
By default RESC will start to scan based on the cron expression mentioned in example-values.yaml file which is `0 6 * * 6` at 06:00 on Saturday.
You can adjust it or you can run below command after helm deployment to start the scan immediately.
```
kubectl create job --from=cronjob/resc-vcs-scraper-projects resc-vcs-scraper-projects -n resc
```
### Connect to database using Azure Data Studio
With Azure Data Studio you can connect to the database running in Kubernetes cluster with following connection details.  
Use the database password defined for dbPass in example-values.yaml file.

![db-connection-screenshot!](images/db-connection.png)



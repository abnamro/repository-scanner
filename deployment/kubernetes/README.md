# Repository Scanner (RESC) Deployment - Kubernetes

<!-- TABLE OF CONTENTS -->
## Table of contents
1. [About the component](#about-the-component)
2. [Technology stack](#technology-stack)
3. [Getting started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Testing templates](#testing-templates)
    - [Deploying charts](#deploying-charts)
4. [Additional Information](#additional-information)
    - [Trigger scanning](#trigger-scanning)
    - [Connect to database using Azure Data Studio](#connect-to-database-using-azure-data-studio)


<!-- ABOUT THE COMPONENT -->
## About the component
This component contains templates and charts for deploying the Repository Scanner in a Kubernetes infrastructure.

<!-- TECHNOLOGY STACK -->
## Technology stack
* [Docker](https://www.docker.com/)
* [Kubernetes](https://kubernetes.io/)
* [Helm](https://helm.sh/)

<!-- GETTING STARTED -->
## Getting started

These instructions will help you to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
#### 1. Install Software
* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* [Kubernetes](https://docs.docker.com/desktop/kubernetes/) - To install Kubernetes, enable it in Docker Desktop. If you install Kubernetes using minikube, ensure the version is 1.21 or later.
* [Helm](https://helm.sh/docs/intro/install/)

#### 2. Populate RESC-RULE.toml file
RESC uses rules from [Gitleaks](https://github.com/zricethezav/gitleaks) to detect secrets.
Ensure you have the rule pack config file in TOML format available, which needs to be provided as deployment argument.
To download this GitLeaks rule you need to execute the following command in a Git Bash or Linux terminal:

```bash
cd ./deployment/kubernetes/

curl https://raw.githubusercontent.com/zricethezav/gitleaks/master/config/gitleaks.toml > RESC-RULE.toml
```

#### 3. Create persistent volume and update it in example-values.yaml
Create two folders in your user folder and name them _database_ and _raabitmq_ as described below.

Windows: C:\Users\<username>\resc\database and C:\Users\<username>\resc\rabbitmq  
Linux: /Users/<username>/var/resc/database and /Users/<username>/var/resc/rabbitmq  

Update persistent volume claim path and hostOS for database.
```
Windows:
--------------
resc-database:
  hostOS: "windows"
  database:
    pvc_path: "/run/desktop/mnt/host/c/Users/<username>/resc/database"

Linux:
--------------
resc-database:
  hostOS: "linux"
  database:
    pvc_path: "/Users/<username>/var/resc/database"
```

Update persistent volume claim path and filemountType for rabbitmq.
```
Windows:
--------------
resc-rabbitmq:
  filemountType: "windows"
  rabbitMQ:
    pvc_path: "/run/desktop/mnt/host/c/Users/<username>/resc/rabbitmq"

Linux:
--------------
resc-rabbitmq:
  filemountType: "linux"
  rabbitMQ:
    pvc_path: "/Users/<username>/var/resc/rabbitmq"
```

#### 4. Provide details of the accounts/projects to scan
You need to provide at least one vcs instance detail to start scanning.
Below is an example for how to scan repositories from GitHub.
* scope: List of GitHub accounts you want to scan.
  For example, lets'say you want to scan all the repositories for the following GitHub accounts.  
  https://github.com/kubernetes  
  https://github.com/docker
  
  Then you need to add those accounts to scope like : ["kubernetes", "docker"]. All the repositories from those accounts will be scanned. 
* exceptions (optional): If you want to exclude any account from scan, then add it to exceptions. Default is empty exception.
* usernameValue: Provide your GitHub username.
* tokenValue: Provide your GitHub personal access token.



```yaml
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
In order to run (unit/linting) tests locally, naviagate to deployment/kubernetes folder:
```bash
cd ./deployment/kubernetes/
```

helm lint: examine a chart for possible issues
```bash
helm lint . --set-file global.secretScanRulePackConfig=./RESC-RULE.toml to run helm linting.
```

Render chart templates locally and display the output.
```bash
helm template resc . -f ./example-values.yaml --set-file global.secretScanRulePackConfig=./RESC-RULE.toml
```

## Deploying charts 
Make sure you have completed the [pre-requisite](#prerequisites) steps.

* Ensure the namespace is created, if not then run 
  ```bash
  kubectl create namespace resc
  ```
* Naviagate to deployment/kubernetes folder.
  ```bash
  cd ./deployment/kubernetes/
  ```

* Deploy the helm charts.  
  ```bash
  helm install --namespace resc resc . -f ./example-values.yaml --set-file global.secretScanRulePackConfig=./RESC-RULE.toml
  ```
  
* Optionally, set the default namespace for all kubectl commands. Now you no longer need to specify the -n resc option for all the kubectl commands.
  ```bash
  kubectl config set-context --current --namespace=resc
  ```

* Wait for two minutes, then run below commands to verify the installation.
  ```bash
  helm list -n resc
  kubectl get pods -n resc
  ```
  ![deployment-status-screenshot!](images/deployment-status.png)

* To upgrade the deployment run. 
  ```bash
  helm upgrade --namespace resc resc . -f ./helm-context/example-values.yaml --set-file global.secretScanRulePackConfig=./RESC-RULE.toml
  ```
* To uninstall or delete the deployment run.
  ```bash
  helm uninstall resc --namespace resc
  ```

## Additional Information
### Issue in image pulling?
If any image is not getting pulled automatically from registry, you can use `docker pull` command to pull that image manually.

Examples:
```bash
docker pull mcr.microsoft.com/azure-sql-edge:1.0.5

docker pull rabbitmq:3.11.2-management-alpine

docker pull rescabnamro/resc-backend:1.0.0

docker pull rescabnamro/resc-frontend:1.0.0

docker pull rescabnamro/resc-vcs-scraper:1.0.0

docker pull rescabnamro/resc-vcs-scanner:1.0.0
```

### Trigger scanning
By default RESC will start to scan according to the cron expression mentioned in example-values.yaml file which is `0 6 * * 6` at 06:00 on Saturday.
You can adjust it or you can run below command after helm deployment to start the scan immediately.
```bash
kubectl create job --from=cronjob/resc-vcs-scraper-projects resc-vcs-scraper-projects -n resc
```
### Connect to database using Azure Data Studio
With Azure Data Studio you can connect to the database running in Kubernetes cluster with following connection details.  
Use the database password defined for dbPass in example-values.yaml file.

![db-connection-screenshot!](images/db-connection.png)



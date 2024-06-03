<!-- TABLE OF CONTENTS -->
## Table of contents
1. [About the project](#about-the-project)
2. [Getting started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Deploying charts](#deploying-charts)
4. [Additional Information](#additional-information)

<!-- ABOUT THE PROJECT -->
## About the project
It is now possible to directly download the helm charts from the Repository Scanner (RESC) GitHub Repository since it now also
acts as a helm repository! The charts are now published automatically to gh-pages branch by [Chart Releaser Action](https://github.com/marketplace/actions/helm-chart-releaser).  

This helm repository allows for a quicker and easier way to obtain the helm charts and use them on your machine.  

<!-- GETTING STARTED -->
## Getting started
These instructions will help you to downlaod and install the helm chart on your machine for development and testing purposes.

### Prerequisites
#### 1. Install Software
* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* [Kubernetes](https://docs.docker.com/desktop/kubernetes/) - To install Kubernetes, enable it in Docker Desktop. If you install Kubernetes using minikube, ensure the version is 1.21 or later.
* [Helm](https://helm.sh/docs/intro/install/)

#### 2. Populate RESC-RULE.toml file
* Ensure you have the rule pack config file in TOML format available, which needs to be provided as deployment argument.  
To download this GitLeaks rule you need to execute the following command.  

```bash
curl https://raw.githubusercontent.com/zricethezav/gitleaks/master/config/gitleaks.toml > RESC-RULE.toml
```

#### 3. Populate custom-values.yaml file
Run the interactive CLI wizard to populate custom-values.yaml.
Detailed information can be found [here](https://github.com/abnamro/repository-scanner/blob/main/deployment/resc-helm-wizard/README.md)

#### 4. Ensure the *resc* namespace is created, if not then run
```
kubectl create namespace resc
```

## Deploying charts 
Make sure you have completed the [pre-requisite](#prerequisites) steps.

* Add the chart repository

```bash
helm repo add [NAME] [URL]

helm repo add resc-helm-repo https://abnamro.github.io/repository-scanner/
```

* (Optional): If the repo was already added earlier, you can run the following command to retrieve the latest versions of the packages.

```bash
helm repo update
```

* To ensure this went well, you can execute the following command to see the charts.
```bash
helm search repo resc-helm-repo
```

* To install with the release name, run the following command.

```bash
helm install --namespace resc resc-release resc-helm-repo/resc -f <custom-values.yaml file location> --set-file global.secretScanRulePackConfig=<RESC-RULE.toml file location>
```

* At any point if you wish to uninstall the chart.

```bash
helm delete resc-release --namespace resc
```

*Note:* resc-release corresponds to the release name, feel free to change it to suit your needs. 


## Additional Information
For additional information please refer this [page](https://github.com/abnamro/repository-scanner/tree/main/deployment/kubernetes#additional-information)
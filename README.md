# Repository Scanner (RESC) Deployment - Kubernetes

It is now possible to directly download the files from the Repository Scanner (RESC) GitHub Repository since it now also
acts as a helm repository! This helm repository allows for a quicker and easier way to obtain the helm charts and use them
on your machine. The process in getting these helm charts is described in the steps below:

* The first step, once helm has been set up correctly, is to add the repository in the following way:
```
helm repo add <alias> https://abnamro.github.io/repository-scanner/
```

* (Optional): If the repo was already added earlier, you can run the following command to update it and retrieve the latest packages:
```
helm repo update
```

* To make sure this went well, you can execute the following command to see the charts:
```
helm search repo <alias>
```

* To install the chart name, run the following command:
```
helm install my-<chart-name> <alias>/resc
```

* At any point if you wish to uninstall the chart:
```
helm delete my-<chart-name>
```
# Repository Scanner (RESC) Deployment - Kubernetes

It is now possible to directly download the files from the Repository Scanner (RESC) GitHub Repository since it now also
acts as a helm repository! This helm repository allows for a quicker and easier way to obtain the helm charts and use them
on your machine. The process in getting these helm charts is described in the steps below:

* The first step, once helm has been set up correctly, is to add the repository in the following way:
```
helm repo add <alias> https://abnamro.github.io/repository-scanner/
```

* (Optional): If the repo was already added earlier, you can run the following command to update it and retrieve the 
latest packages:
```
helm repo update
```

* To make sure this went well, you can execute the following command to see the charts:
```
helm search repo <alias>
```

* To make use of the Repository Scanner, you need a rulefile from GitLeaks. This can be downloaded and populated with 
the following command:
```
curl https://raw.githubusercontent.com/zricethezav/gitleaks/master/config/gitleaks.toml > RESC-RULE.toml
```

* It is also important to have the example-values.yaml present during installation. This can be downloaded and populated
with the following command.
```
curl https://raw.githubusercontent.com/abnamro/repository-scanner/main/deployment/kubernetes/example-values.yaml > example-values.yaml
```

Upon downloading the example-values.yaml file, it needs a small change to make it more functional depending on the
system you're using. Create two folders in your user folder and name them _database_ and _raabitmq_ as described below.

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

* To install the chart name, run the following command:
```
helm install my-<chart-name> <alias>/resc -f ./example-values.yaml --set-file global.secretScanRulePackConfig=./RESC-RULE.toml
```

* At any point if you wish to uninstall the chart:
```
helm delete my-<chart-name>
```
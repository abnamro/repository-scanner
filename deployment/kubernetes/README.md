# RESC Infra

# Prerequisites
Ensure you have the rulepack config file in TOML format available, which needs to be provided as deployment argument.

# 1 Testing templates
In order to run (unit/linting) tests locally, you can use the following commands from project root folder:
* `cd ./deployment/kubernetes/`
* `helm lint . --set-file global.secretScanRulePackConfig=<path to rulepack config toml file>` to run helm linting.
* `helm template resc . -f ./example-values.yaml --set-file global.secretScanRulePackConfig=<path to rulepack config toml file>` to run get a preview of the helm templates after the local values has been applied.

# Deploying charts locally 
Run the following commands from project root folder.
* Ensure the namespace is created `kubectl create namespace resc`
* `cd ./deployment/kubernetes/`
* Clone resc-rules repository inside root folder of resc-infra-generic and ensure resc-rules/resc_config/RESC-SECRETS-RULE.toml file exists.
* Fill up the example-values.yaml file with required vales.
* Deploy the helm charts `helm install --namespace resc resc . -f ./example-values.yaml --set-file global.secretScanRulePackConfig=<path to rulepack config toml file>`
* Optionally set the default namespace for all kubectl commands `kubectl config set-context --current --namespace=resc` Now you no longer need to specify the -n resc option for all the kubectl commands
* To verify installations run
  * `helm list -n resc`
  * `kubectl get pods -n resc`
* To uninstall or delete the deployment
  * `helm uninstall resc --namespace resc`
* Upgrade the helm deployment using `helm upgrade --namespace resc resc . -f ./helm-context/example-values.yaml --set-file global.secretScanRulePackConfig=<path to rulepack config toml file>`

# Trigger scanning
By default RESC will start to scan based on the cron expression mentioned in example-values.yaml file which is `0 6 * * 6` at 06:00 on Saturday.
You can adjust it or you can run below command after helm deployment to start the scan immediately.
`kubectl create job --from=cronjob/resc-vcs-scraper-projects resc-vcs-scraper-projects -n resc`


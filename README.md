                  
            ______                     _ _                     _____
            | ___ \                   (_| |                   /  ___|
            | |_/ /___ _ __   ___  ___ _| |_ ___  _ __ _   _  \ `--.  ___ __ _ _ __  _ __   ___ _ __
            |    // _ | '_ \ / _ \/ __| | __/ _ \| '__| | | |  `--. \/ __/ _` | '_ \| '_ \ / _ | '__|
            | |\ |  __| |_) | (_) \__ | | || (_) | |  | |_| | /\__/ | (_| (_| | | | | | | |  __| |
            \_| \_\___| .__/ \___/|___|_|\__\___/|_|   \__, | \____/ \___\__,_|_| |_|_| |_|\___|_|
                      | |                               __/ |
                      |_|                              |___/

<div align="center">
    <h1>Repository Scanner</h1>
</div>

[![Maintainer][maintainer-shield]][maintainer-url]
[![License][license-shield]][license-url]
[![LaunchedDate][launched-shield]][launched-url]
[![LastUpdated][updated-shield]][updated-url]
[![Build][build-shield]][build-url]
[![Version][version-shield]][version-url]
[![Python][python-shield]][python-url]
[![TypeScript][typescript-shield]][typescript-url]
[![Vue.js][vuejs-shield]][vuejs-url]
[![Docker][docker-shield]][docker-url]
[![Kubernetes][k8-shield]][k8-url]
[![Helm][helm-shield]][helm-url]
[![Downloads][downloads-shield]][downloads-url]
[![DockerPulls][docker-pulls-shield]][docker-pulls-url]
[![OpenSSFBestPractices][openssf-shield]][openssf-url]
[![OpenSSF Scorecard][ossf-shield]][ossf-url]
[![SonarCloud][sonar-cloud-shield]][sonar-cloud-url]

The Repository Scanner (RESC) is a tool used to detect secrets in source code management and version control systems 
(e.g. GitHub, BitBucket, or Azure DevOps). Among the types of secrets that the Repository Scanner detects are credentials, 
passwords, tokens, API keys, and certificates. The tool is maintained and updated by the ABN AMRO Bank to match the 
constantly changing cyber security landscape. 

The Repository Scanner was created to prevent that credentials and other sensitive information are left unprotected in code repositories.
Exposing sensitive information in such a way can have severe consequences for the security posture of an organization. An attacker can use 
the data to compromise the organization's network. This can be prevented by scanning a repository with the RESC tool. It marks all the 
instances of exposed sensitive information in the source code.

![RESC-Demo](/images/RESC_Preview.gif)

## 📒 Table of contents
* [🔗 Links](#links)
* [🛠️ Technical information](#technical-information)
* [🏁 Getting started](#getting-started)
* [🏎️ Key bindings](#kb)
* [📊 Dummy data generation](#dummy-data-generation-guide)
* [💁🏽 Contributing guidelines](#contribution-guide)
* [📧 Contact](#contact)
* [⚖️ License](#license)
* [🎉 Acknowledgments](#acknowledgement)

## 🔗 Links <a name = "links"></a>

Throughout the process of open sourcing this project, the ABN AMRO Bank created a series of articles that describe the
capabilities of the Repository Scanner (RESC) tool, the architectural decisions behind it, and the road to open sourcing 
RESC. With the articles, users can look "behind the scenes" and gain a deeper understanding of the tool.  

[ABN AMRO Open Source project: Repository Scanner](https://medium.com/abn-amro-developer/abn-amro-open-source-project-repository-scanner-cf62aa62b059)  
[Open Source Project Update: Repository Scanner](https://medium.com/abn-amro-developer/open-source-project-update-repository-scanner-b44bc3f3921a)  
[Open Source Project Update: Repository Scanner 2.0.0](https://medium.com/abn-amro-developer/open-source-project-update-repository-scanner-2-0-0-a2120f8ccf4b)  

### Releases
Every notable release of the Repository Scanner tool, the changes that come with the release, and the release date can be found on the [Releases](https://github.com/abnamro/repository-scanner/releases) page.

## 🛠️ Technical information <a name = "technical-information"></a>
The technologies that the Repository Scanner Tool is built on is listed below. There is also a list with direct links to the individual
components of RESC.

* [![Python][Python.org]][Python-url]
* [![Docker][Docker.com]][Docker-url]
* [![Kubernetes][Kubernetes.io]][Kubernetes-url]
* [![Helm][Helm.sh]][Helm-url]
* [![Vue][Vue.js]][Vue-url]
* [![RabbitMQ][RabbitMQ.com]][RabbitMQ-url]
* [![Redis][Redis.com]][Redis-url]  

### RESC high-level overview
The diagram below gives a high-level overview of the Repository Scanner tool. All the different components of the
tool and the technologies that it utilizes are explained in detail here. As shown in the diagram, all the components mentioned
are run as Docker containers in a Kubernetes ecosystem.

* [RESC-Frontend](https://github.com/abnamro/resc-frontend): The RESC-Frontend is a fully responsive dashboard application developed using TypeScript, Vue 3 and the BootstrapVueNext framework (based on Bootstrap 5). It has screens for Analytics, Repositories, Scan Findings, Rule Analytics, and Rule Pack.
* [RESC-Backend](https://github.com/abnamro/resc-backend): The RESC-Backend is the backend of the Repository Scanner tool. The RESC-Backend consists of RabbitMQ users and queue creation, Database models, the RESC Web service, and Alembic scripts for database migration. The RESC Web service is created using FASTAPI.
* [RESC-VCS-Scanner](https://github.com/abnamro/resc-vcs-scanner): RESC-VCS-Scanner, which runs as a celery worker, gathers repositories from the repositories queue and carries out a secret scan. Gitleaks is used as the scanner to find secrets.
* [RESC-VCS-Scraper](https://github.com/abnamro/resc-vcs-scraper): All projects and repositories from supported VCS providers such as Bitbucket, Azure Repos, and GitHub are gathered by the RESC-VCS-SCRAPER. This component contains the VCS-Scraper-Projects and VCS-Scraper-Repositories as its primary modules.

Please visit [architecture.md](https://github.com/abnamro/repository-scanner/blob/main/docs/architecture.md) for more information.

## 🏁 Getting started <a name = "getting-started"></a>
Please refer [resc-helm-wizard](https://github.com/abnamro/repository-scanner/blob/main/deployment/resc-helm-wizard/README.md) for an interactive and easy way to deploy RESC on a Kubernetes cluster.

## 🏎️ Key bindings <a name="kb"></a>
RESC comes with the following keybindings:
![keybindings](./images/keybindings.png)

## 💁🏽 Contributing guidelines <a name = "contribution-guide"></a>
We believe that innovating together can lead to the most incredible results and developments. Contributions to the Repository Scanner tool are therefore highly encouraged. We have created [guidelines](https://github.com/abnamro/repository-scanner/blob/main/contributing.md) that we expect contributors to the project to follow.  By contributing to the project you also agree with our [Code of Conduct](https://github.com/abnamro/repository-scanner/blob/main/code-of-conduct.md).

## 📧 Contact <a name = "contact"></a>
If you need to get in touch with the maintainers of the Repository Scanner tool, please use the following e-mail address: [resc@nl.abnamro.com](mailto:resc@nl.abnamro.com).

## ⚖️ License <a name = "license"></a>
The Repository Scanner (RESC) Tool is licensed under the [MIT](https://github.com/abnamro/repository-scanner/blob/main/LICENSE.md) License.


## 🎉 Acknowledgements <a name = "acknowledgement"></a>
Since the Repository Scanner (RESC) makes use of [GitLeaks](https://github.com/zricethezav/gitleaks), we want to give Zachary Rice credits for creating and maintaining GitLeaks. GitLeaks has helped many organizations in securing their codebases for any leaked secrets.


<!-- MARKDOWN LINKS & IMAGES -->
[maintainer-shield]: https://img.shields.io/badge/maintainer-%40ABNAMRO-09996B
[maintainer-url]: https://github.com/ABNAMRO
[license-shield]: https://img.shields.io/github/license/abnamro/repository-scanner
[license-url]: https://github.com/abnamro/repository-scanner/blob/main/LICENSE.md
[launched-shield]: https://img.shields.io/badge/launched-DEC%202022-teal
[launched-url]: https://github.com/abnamro/repository-scanner/blob/main/LICENSE.md
[updated-shield]: https://img.shields.io/github/last-commit/abnamro/repository-scanner?color=blue&label=updated
[updated-url]: https://github.com/abnamro/repository-scanner/commits/main
[build-shield]: https://img.shields.io/github/actions/workflow/status/abnamro/repository-scanner/backend-ci.yaml?logo=github
[build-url]: https://github.com/abnamro/repository-scanner/actions
[version-shield]: https://img.shields.io/github/v/release/abnamro/repository-scanner?color=blueviolet&label=version
[version-url]: https://www.github.com/abnamro/repository-scanner/releases/latest
[downloads-shield]: https://img.shields.io/github/downloads/abnamro/repository-scanner/total?color=blue
[downloads-url]: https://pepy.tech/project/resc-backend
[docker-pulls-shield]: https://img.shields.io/docker/pulls/rescabnamro/resc-backend.svg
[docker-pulls-url]: https://hub.docker.com/r/rescabnamro/resc-backend
[openssf-shield]: https://www.bestpractices.dev/projects/7799/badge
[openssf-url]: https://www.bestpractices.dev/projects/7799
[sonar-cloud-shield]: https://sonarcloud.io/api/project_badges/measure?project=abnamro-resc_resc-backend&metric=alert_status
[sonar-cloud-url]: https://sonarcloud.io/organizations/abnamro-resc/projects
[python-shield]: https://img.shields.io/badge/Python-3670A0?style=flat&logo=python&logoColor=ffdd54
[python-url]: https://www.python.org
[vuejs-shield]: https://img.shields.io/badge/VueJS-%2335495e.svg?style=flat&logo=vuedotjs&logoColor=%234FC08D
[vuejs-url]: https://vuejs.org
[docker-shield]: https://img.shields.io/badge/Docker-2CA5E0?style=flat&logo=docker&logoColor=white
[docker-url]: https://www.docker.com
[k8-shield]: https://img.shields.io/badge/kubernetes-326ce5.svg?&style=flat&logo=kubernetes&logoColor=white
[k8-url]: https://kubernetes.io
[helm-shield]: https://img.shields.io/badge/Helm-0F1689?style=flat&logo=Helm&labelColor=0F1689
[helm-url]: https://helm.sh

[ossf-shield]: https://api.securityscorecards.dev/projects/github.com/abnamro/repository-scanner/badge
[ossf-url]: https://securityscorecards.dev/viewer/?uri=github.com/abnamro/repository-scanner

[Python.org]: https://img.shields.io/badge/Python-2b5b84?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
<!-- for-the-badge is broken on TypeScript... use flat instead -->
[typescript-shield]: https://shields.io/badge/TypeScript-3178C6?style=flat&logo=TypeScript&logoColor=FFF
[typescript-url]: https://www.typescriptlang.org/
[Docker.com]: https://img.shields.io/badge/Docker-0b214a?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
[Kubernetes.io]: https://img.shields.io/badge/Kubernetes-3371e3?style=for-the-badge&logo=kubernetes&logoColor=white
[Kubernetes-url]: https://www.kubernetes.io/
[Helm.sh]: https://img.shields.io/badge/Helm-091c84?style=for-the-badge&logo=helm&logoColor=white
[Helm-url]: https://helm.sh/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[RabbitMQ.com]: https://img.shields.io/badge/RabbitMQ-ff6600?style=for-the-badge&logo=rabbitmq&logoColor=white
[RabbitMQ-url]: https://rabbitmq.com/
[Redis.com]: https://img.shields.io/badge/redis-%23DD0031.svg?&style=for-the-badge&logo=redis&logoColor=white
[Redis-url]: https://redis.com/

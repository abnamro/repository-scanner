                  
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
    <h3>
        <a href="https://github.com/ABNAMRO">
            <img src="https://img.shields.io/badge/maintainer-%40ABNAMRO-09996B?style=for-the-badge">
        </a>
        <a>
            <img src="https://img.shields.io/badge/launched-MONTH%20YEAR-teal?style=for-the-badge">
        </a>
        <a href="https://github.com/abnamro/repository-scanner/commits/main">
            <img src="https://img.shields.io/github/last-commit/abnamro/repository-scanner?style=for-the-badge&color=blue&label=updated">
        </a>
        <a href="https://www.github.com/abnamro/repository-scanner/releases/latest">
            <img src="https://img.shields.io/github/v/release/abnamro/repository-scanner?style=for-the-badge&color=blueviolet&label=version">
        </a>
    </h3>
</div>

The Repository Scanner (RESC) is a tool used to detect secrets in source code management systems/version control systems 
(GitHub, BitBucket and Azure DevOps). The type of secrets the Repository Scanner is able to detect are credentials, 
passwords, tokens, api-keys, certificates and much more! The tool is maintained by the ABN AMRO Bank and is 
continuously being updated to match a constantly changing cybersecurity landscape. 

The main reason why the Repository Scanner tool was created is to prevent the theft of credentials and other sensitive 
information in code repositories. Exposing sensitive information like this could lead to catastrophic consequences for a
project, or even worse, within a company. An attacker could use this sensitive information to gain an initial foothold 
or use it to vertically or laterally move throughout a network to eventually cause more damage. This can be prevented
with a single scan using the RESC tool to mark all the instances of sensitive information being leaked in the source
code.

## 📒 Table of contents
* [Links](#links)
* [Versions](#versions)
* [Technical Information](#technical-information)
* [Contribution Guidelines](#contribution-guide)
* [Contact](#contact)
* [License](#license)

## 🔗 Links
Throughout the process of open sourcing the project, the ABN AMRO Bank made a series of articles describing the
capabilities of the Repository Scanner (RESC) tool, the architectural decisions behind it and the road to open sourcing a
project like the Repository Scanner. The articles can be very useful for users of the RESC tool to get a better 
understanding of the tool and get a real look "behind the scenes".

--ToDo: Add links to the blog(s) where the product is better described so the viewers can read that and get a better
idea of the product. Also think of other links that could prove useful and add them here.

## ⚙️Versions
The [SemVer](https://semver.org/) numbering is used for the releases of the Repository Scanner tool. In which a version
consists of a MAJOR.MINOR.PATCH number (e.g. v1.2.4). Where the **MAJOR** part of the number is reserved for the biggest 
of updates to the Repository Scanner tool like an enormous change in the backend that alters the flow and behavior of 
the tool or a complete overhaul of the frontend which will majorly impact the user's experience. The **MINOR** part of
the number will focus on big new feature, feature updates and other newsworthy changes in the tool. Leaving the **PATCH**
part of the number open for everything else. Things like small content, bug fixes, fixing typos, fixing incorrect 
information and broken links.

### Major releases
Every notable release of the Repository Scanner (RESC) tool, the changes that come with the release and the date of the
release will be documented and listed below - a more detailed and historical list of a published release can be found on
the [Releases](https://github.com/abnamro/repository-scanner/releases) page:

* **v1.0** – Initial release of the Repository Scanner:
    * Able to scan for secrets in your repositories;
    * Complete overview of the found secrets through the User Interface with a direct link to the issue;
    * Able to sort the findings by secret type (tokens, certificates, passwords, etc.);
    * A statistic page that gives an overview of findings and how they increase/decrease monthly along with the amount of times a finding appears;
    * The ability to import your own rulepack with custom rules to fit your personal means!

## 🛠️ Technical Information
The Repository Scanner is a very technical tool that consists of a lot of different components which in turn 
uses different technologies to make these components work as efficient as possible. These technologies are listed below
to give a clear picture of what is being used for the Repository Scanner. There is also a reference to each individual
component of the tool that will redirect you to that component.

* [![Python][Python.org]][Python-url]
* [![Docker][Docker.com]][Docker-url]
* [![Kubernetes][Kubernetes.io]][Kubernetes-url]
* [![Helm][Helm.sh]][Helm-url]
* [![Vue][Vue.js]][Vue-url]
* [![RabbitMQ][RabbitMQ.com]][RabbitMQ-url]

### VCS Scanner Worker Flow Diagram
The flow diagram below shows how a VCS Scanner Worker goes through different stages and is confronted with choices to
come to the desired result. The VCS Scanner Worker first picks up a branch from the queue where, with user input, the
decision is made what type of scan to run. If it is a base scan a full scan of all commits will be done to look for
secrets. If this is indeed the case, the findings will be stored inside the database and the last scanned commit has
of that branch will be saved. If it is an incremental scan, where the branch is scanned earlier, only scan for the
commits after the last scanned commit hash. The process of finding secrets and storing them in the database will be 
similar as described before.

![product-screenshot!](images/RESC_Scan_Flow_Diagram.png)

### RESC High Level Overview
The diagram below gives a good high level overview of the Repository Scanner tool. All the different components from the
tool and the technologies behind it are explained in detail here. As shown in the diagram, all the components mentioned
are run as Docker containers in a Kubernetes ecosystem.

* [RESC-Frontend](https://github.com/abnamro/repository-scanner/tree/main/components/resc-frontend): The RESC-Frontend is a fully responsive dashboard application developed using Vue.js 2 and the BootstrapVue framework. It has screens for Analytics, Repositories, Scan Findings, Rule Analytics and Rule Pack.
* [RESC-Backend](https://github.com/abnamro/repository-scanner/tree/main/components/resc-backend): The RESC-Backend is, as the name indicates, the backend of the Repository Scanner tool. The RESC-Backend consits of RabbitMQ users and queue creation, Database models, the RESC Web service and Alembic scripts for database migration. The RESC Web service is created using FASTAPI.
* [RESC-VCS-Scanner](https://github.com/abnamro/repository-scanner/tree/main/components/resc-vcs-scanner): RESC-VCS-Scanner, which runs as a celery worker, gathers repositories from the repositories queue and does a secret scan. Gitleaks is used as the scanner to find secrets.
* [RESC-VCS-Scraper](https://github.com/abnamro/repository-scanner/tree/main/components/resc-vcs-scraper): All projects and repositories from supported VCS providers such as Bitbucket, Azure Repos, and GitHub, are gathered by the RESC-VCS-SCRAPER. This component contains the VCS-Scraper-Projects and VCS-Scraper-Repositories as its primary modules.

![product-screenshot!](images/RESC_HighLevel_Diagram.png)


## 💁🏽 Contribution Guidelines
Contributing to the Repository Scanner tool is highly encouraged because innovating together can lead to the most
incredible results and developments! To contribute to the project there are some guidelines in place that we expect 
contributors to the project to follow and that are available on the [Contribution](https://github.com/abnamro/repository-scanner/blob/main/contributing.md)
page. By contributing to the project you also agree with the [Code of Conduct](https://github.com/abnamro/repository-scanner/blob/main/code-of-conduct.md).

## 📧    Contact
In the event that you need to get in contact with the maintainers of the Repository Scanner tool, please do so by contacting 
the following e-mail address: [resc@nl.abnamro.com](mailto:resc@nl.abnamro.com).

## ⚖️License
The Repository Scanner (RESC) Tool is licensed under the [MIT](https://github.com/abnamro/repository-scanner/blob/main/LICENSE.md) License.

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[Python.org]: https://img.shields.io/badge/Python-2b5b84?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
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

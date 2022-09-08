# Repository Scanner

The Repository Scanner is a tool used to detect secrets (credentials, passwords, tokens, api-keys, certificates) in source code management systems (GitHub, Bitbucket and Azure DevOps).

The tool is completely containerised (Docker / Kubernetes) and consists of a backend, message queue, database and front-end.

The tool is build and used by the ABN AMRO SECO (Secure Coding) team to review identified secrets for true / false positives.

# Repository Scanner Frontend (RESC-Frontend)

<!-- TABLE OF CONTENTS -->
## Table of contents
1. [About the component](#about-the-component)
2. [Technology stack](#technology-stack)
3. [Getting started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Run locally](#run-locally)
    - [Run using docker](#run-using-docker)
    - [Testing](#testing)
4. [Additional information](#additional-information)

<!-- ABOUT THE COMPONENT -->
## About the component
Repository Scanner (RESC) Frontend is a fully responsive dashboard application developed using Vue.js 2 and BootstrapVue framework. It includes screens such as Analytics, Repositories, Scan Findings, Rule Analytics, and Rule Pack.

<!-- TECHNOLOGY STACK -->
## Technology stack
- [Vue js 2](https://v2.vuejs.org/)
- [Bootstrap Vue](https://bootstrap-vue.org/)
- [Docker](https://www.docker.com/)

<!-- GETTING STARTED -->
## Getting started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
- Install [Node.js](https://nodejs.org/en/) v16.13.0
- Install Vue cli using command: `npm install -g @vue/cli`  
- Install Vetur, ESLint and Prettier extensions to your VSCode IDE. 
- Install [Docker](https://www.docker.com/)
- Ensure RESC webservice is up and running in order to visualize data. This API is running at http://localhost:30800/.  

### Run locally

1. Clone the repository and refer the following steps to run the project locally.
```bash

cd components/resc-frontend

npm install

npm run serve
```
2. Access the application using this url: http://localhost:8080/  

***Note:***  Replace the actual values in the placeholders <branch-name> and <repository-scanner repo url>

### Run using Docker

Build the RESC Frontend Docker image locally by running the following commands.

- Pull the docker image from registry: 
```bash
docker pull rescabnamro/resc-frontend:0.0.1
```
- Alternatively, build the docker image locally by running:
```bash
docker build -t rescabnamro/resc-frontend:0.0.1 .
```
- Run the RESC frontend by using the following command: 

```bash
docker run -p 8080:8080 -e VUE_APP_AUTHENTICATION_REQUIRED="false" -e VUE_APP_RESC_WEB_SERVICE_URL="http://localhost:30800/resc"  --name resc-frontend rescabnamro/resc-frontend:0.0.1
```

 Access the application using this url: http://localhost:8080/

### Testing
[(Back to top)](#table-of-contents)

Run your unit tests: ```npm run ut```

Linting files: ```npm run lint```

Linting and fixing files: ```npm run lint:autofix```

## Additional information
[(Back to top)](#table-of-contents)  

### Useful commands
Compiles and minifies for production: ```npm run build```

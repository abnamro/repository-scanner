# Repository Scanner Frontend (RESC-FE)

<!-- TABLE OF CONTENTS -->
## Table of Contents
1. [About The Component](#about-the-component)
2. [Technology Stack](#technology-stack)
3. [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Run locally](#run-locally)
    - [Run using docker](#run-using-docker)
    - [Testing](#testing)
4. [Additional Information](#additional-information)

<!-- ABOUT THE COMPONENT -->
## About The Component
Repository Scanner (RESC) Frontend is a fully responsive dashboard application developed using Vue.js 2 and BootstrapVue framework. It includes screens such as Analytics, Repositories, Scan Findings, Rule Analytics and Rule Pack.

<!-- TECHNOLOGY STACK -->
## Technology Stack
- [Vue js 2](https://v2.vuejs.org/)
- [Bootstrap Vue](https://bootstrap-vue.org/)
- [Docker](https://www.docker.com/)

<!-- GETTING STARTED -->
## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
- Install [Node.js](https://nodejs.org/en/) v16.13.0
- Install Vue cli using command: `npm install -g @vue/cli`  
- Install Vetur, ESLint and Prettier extensions to your VSCode IDE. 
- Ensure RESC webservice is up and running at http://localhost:30000/ in order to visualize data.

### Run locally

Follow the below steps to run the project locally:-
```
git clone -b <branch-name> <repository-scanner repo url>

cd components/resc-frontend

npm install

npm run serve

Now access the application using this url: http://localhost:8080/
```
***Note:***  Replace the actual values in the placeholders <branch-name> and <repository-scanner repo url>

### Run using docker

Build the RESC Frontend docker image locally by running the following commands (Keep the image version parameter in mind):

- Install the docker image from the CLI: `docker pull ghcr.io/abnamro/resc-frontend:0.0.1`
- Build the docker image by running:`docker build -t abnamro/resc-frontend:0.0.1`
- Run the RESC frontend by using the following command: `docker run --name resc-frontend abnamro/resc-frontend:0.0.1`

Now access the application using this url: http://localhost:8080/

### Testing
[(Back to top)](#table-of-contents)

Run your unit tests:```npm run ut```

Linting files:```npm run lint```

Linting and fixing files:```npm run lint:autofix```

## Additional Information
[(Back to top)](#table-of-contents)  

### Some Useful Commands
Compiles and minifies for production:```npm run build```

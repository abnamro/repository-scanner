# Repository Scanner Frontend (RESC-FE)

<!-- TABLE OF CONTENTS -->
## Table of Contents
1. [About The Project](#about-the-project)
2. [Technology Stack](#technology-stack)
3. [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Run locally](#run-locally)
    - [Run using docker](#run-using-docker)
    - [Testing](#testing)
4. [Additional Information](#additional-information)

<!-- ABOUT THE PROJECT -->
## About The Project
Repository Scanner (RESC) Frontend is a fully responsive dashboard application developed using Vue.js 2 and BootstrapVue framework. It includes screens such as  Analytics , Repositories , Scan Findings, Rule Analytics and Rule Pack.

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
[(Back to top)](#table-of-contents)

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
[(Back to top)](#table-of-contents)

Build the RESC Frontend docker image locally by running the following command (image version parameter defaults to 1.0.0):
```
./rebuild.sh <image version>
```

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

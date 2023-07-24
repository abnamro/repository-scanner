# Dummy Data Generator

## 📒 Table of contents
* [About](#about-the-component)
* [Getting started](#getting-started)
* [Generating dummy data](#generating-dummy-data)

<!-- ABOUT THE COMPONENT -->
## About the component <a name = "about-the-component"></a>
This is a standalone utility which can be used to generate dummy-data for testing purposes. The utility does not have a separate dependencies and is ready to run. <br>N.B: While running the script, you will be asked if it is okay to clear all the existing data from the database tables. If the response is affirmative the script will continue with its execution.
Once the requirements have been set up, the script can be invoked from the command line.

<!-- GETTING STARTED -->
## 🛠️ Getting started <a name = "getting-started"></a>
The instructions for setting the database up can be found in the section [RESC-BACKEND](https://github.com/abnamro/repository-scanner/tree/main/components/resc-backend#run-resc-web-service-locally-from-source) which will help you to get a copy of the project up and running on your local machine for generating dummy data.

<!-- GENERATING DUMMY DATA -->
## Generating dummy data <a name = "generating-dummy-data"></a>
<details>
  <summary>Preview</summary>
  Ensure resc database is up and running locally. </br>
  Open the terminal from components/resc-backend/src/resc_backend/bin/dummy-data-generator folder and run below commands.

#### Execute command:
  ```bash
  python3 generate_data.py
  ```
</details>

# RESC
## Secret scanner

# Local Setup
Run the below command from project root folder if your IDE doesn't recognize resc as a valid python package  
```
pip install -e .
```

# Testing
In order to run (unit/linting) tests locally, you can use the following commands:
* `tox -e lint` for linting
* `tox -e pytest` for unit testing
* `tox -e sort` for detecting issues in the sorting (and in order to fix sorting just run: `isort src/ tests/`)


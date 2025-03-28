# Automated-Balance-Lookup

A project to automatically aggregate blockchain transaction data by address and generate output files in both Excel and JSON formats. This script processes an input JSON file containing transaction data, optionally enriches the data with owner information from a mapping JSON file, and then outputs the aggregated balance per address.

## Requirements

- Python 3.12
- [Pipenv](https://pipenv.pypa.io/en/latest/)

## Running Locally

1. **Clone the Repository**

   ```bash
   git clone https://your.repository.url/Automated-Balance-Lookup.git
   cd Automated-Balance-Lookup
    ```
2. **Activate the Pipenv Shell**

    Ensure you have Pipenv installed. If not, install it via pip:
     ```bash
    pip install pipenv
    ```
    Then activate your virtual environment:
     ```bash
    pipenv shell
    ```
3. **Install Dependencies**

    Within the activated Pipenv shell, install the project dependencies:
    ```bash
    pipenv install
    ```
4. **Run the Project**

    make sure you replace the local path and privateKey path with your own before running
    ```bash
    python main.py
    ```
    or
    ```bash
    pipenv run python main.py

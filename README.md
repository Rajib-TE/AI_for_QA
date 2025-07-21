# Python Script for CSV Ingestion into Microsoft Fabric KQL Database

This project provides a Python script to automate the process of ingesting data from a local CSV file into a Microsoft Fabric KQL Database. The script handles table creation, defines a CSV-to-table column mapping, and manages the queued ingestion process using the Azure Kusto SDK.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Azure](https://img.shields.io/badge/Azure%20SDK-blue)
![Microsoft Fabric](https://img.shields.io/badge/Microsoft%20Fabric-KQL-purple)

---

## ## Features 🚀

* **Automated Table Creation**: Dynamically creates a table in your KQL database with a predefined schema.
* **Column Mapping**: Creates a JSON-based ingestion mapping to correctly map CSV columns to table columns.
* **Queued Ingestion**: Uses the `QueuedIngestClient` for reliable and managed data ingestion from a local file.
* **Easy Authentication**: Leverages `DefaultAzureCredential` for seamless authentication via Azure CLI, environment variables, or managed identity.

---

## ## Prerequisites 📋

Before you run this script, make sure you have the following set up:

1.  **Python 3.8+**: Ensure Python is installed on your system.
2.  **Azure CLI**: You must have the Azure CLI installed and be logged in to your Azure account.
    ```bash
    az login
    ```
3.  **Microsoft Fabric KQL Database**: You need an active Microsoft Fabric workspace with a KQL Database already provisioned.
4.  **Required Permissions**: Your user account or service principal needs permissions to create tables and ingest data into the target KQL database.
5.  **CSV File**: A CSV file with the data you want to ingest. For this script, it is named `product_catalog.csv` by default.

---

## ## Installation & Setup 🛠️

1.  **Clone or Download**: Get the Python script and place it in your project directory.

2.  **Install Python Libraries**: Install the necessary Azure SDK packages using pip.
    ```bash
    pip install azure-kusto-data azure-kusto-ingest azure-identity
    ```
    Alternatively, create a `requirements.txt` file with the content below and run `pip install -r requirements.txt`.
    ```
    azure-kusto-data
    azure-kusto-ingest
    azure-identity
    ```
---

## ## Configuration ⚙️

Modify the following variables at the top of the script to match your Fabric KQL environment.

```python
# Configuration
CLUSTER = "https://your_fabric_kusto_uri.kusto.fabric.microsoft.com"
DATABASE = "YourKQLDatabaseName"
TABLE = "ProductCatalog"
CSV_FILE = "product_catalog.csv"

---

##  Project Structure
├── product_catalog.csv # Sample CSV data to be ingested \
├── script.py # Main script for ingestion \
├── .venv/ # (Optional) Python virtual environment \
└── README.md # This file

## Installation

1. **Create a virtual environment (optional but recommended):**
   ```bash \
   python -m venv .venv \
   source .venv/bin/activate       # On Windows: .venv\Scripts\activate

   pip install azure-kusto-data azure-kusto-ingest azure-identity
## Authentication
This script uses DefaultAzureCredential from azure-identity to authenticate. It supports various identity sources, such as:

1. Azure CLI (az login) \
2. Managed Identity (in deployed Azure environments) \
3. Visual Studio Code login 

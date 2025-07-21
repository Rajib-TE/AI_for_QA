# CSV to Microsoft Fabric Kusto Ingestion Script

This Python script demonstrates how to programmatically:

1. **Create a table** in a Microsoft Fabric Kusto (Azure Data Explorer) database.
2. **Define a CSV mapping** for structured ingestion.
3. **Ingest data from a CSV file** into the table using the Azure Kusto SDK.

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

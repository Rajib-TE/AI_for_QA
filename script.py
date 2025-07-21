import os
from azure.kusto.data import KustoConnectionStringBuilder
from azure.kusto.data.data_format import DataFormat
from azure.kusto.ingest import QueuedIngestClient, FileDescriptor, IngestionProperties
from azure.kusto.data import KustoClient
import json
 
 
# Configuration
CLUSTER = "https://trd-u9h06mqf2rtbee3pfh.z6.kusto.fabric.microsoft.com"
DATABASE = "Event_QA_KQLDB"
TABLE = "ProductCatalog"
CSV_FILE = "product_catalog.csv"
 
# Auth via Azure CLI or environment (easiest)
from azure.identity import DefaultAzureCredential
token = DefaultAzureCredential().get_token("https://help.kusto.windows.net/.default")
kcsb = KustoConnectionStringBuilder.with_aad_application_token_authentication(CLUSTER, token.token)
 
# Create both clients from correct endpoint
mgmt_client = KustoClient(kcsb)
ingest_client = QueuedIngestClient(kcsb)
 
# Client
# client = QueuedIngestClient(kcsb)
# client = KustoClient(kcsb)
create_table = f"""
.create table {TABLE} (
    ProductID: string,
    ProductName: string,
    ProductCategory: string,
    Price: real,
    ProductDescription: string,
    ProductPunchLine: string,
    ImageURL: string
)
"""
mgmt_client.execute_mgmt(DATABASE, create_table)
csv_mapping_definition = [
    {"column": "ProductID", "DataType": "string", "Ordinal": 0},
    {"column": "ProductName", "DataType": "string", "Ordinal": 1},
    {"column": "ProductCategory", "DataType": "string", "Ordinal": 2},
    {"column": "Price", "DataType": "real", "Ordinal": 3},
    {"column": "ProductDescription", "DataType": "string", "Ordinal": 4},
    {"column": "ProductPunchLine", "DataType": "string", "Ordinal": 5},
    {"column": "ImageURL", "DataType": "string", "Ordinal": 6}
]
 
# Convert the Python list to a JSON string
csv_mapping_json = json.dumps(csv_mapping_definition)
 
create_mapping = f"""
.create table {TABLE} ingestion csv mapping '{TABLE}_csv_mapping' '{csv_mapping_json}'
"""
mgmt_client.execute_mgmt(DATABASE, create_mapping)
 
print("✅ Table and mapping created successfully.")
 
# Ingestion Properties
ingestion_props = IngestionProperties(
    database=DATABASE,
    table=TABLE,
    data_format=DataFormat.CSV,
    ingestion_mapping_reference=f"{TABLE}_csv_mapping"  # Ensure this mapping is created
)
 
# Ingest CSV
file_descriptor = FileDescriptor(CSV_FILE, os.path.getsize(CSV_FILE))
result = ingest_client.ingest_from_file(file_descriptor, ingestion_properties=ingestion_props)
 
 
print("✅ Ingestion started. You can monitor ingestion status in Azure Data Explorer.")
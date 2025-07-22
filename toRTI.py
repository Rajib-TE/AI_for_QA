import os
from azure.kusto.data import KustoConnectionStringBuilder
from azure.kusto.data.data_format import DataFormat
from azure.kusto.ingest import QueuedIngestClient, FileDescriptor, IngestionProperties
from azure.kusto.data import KustoClient
import json
 
 
# Configuration
CLUSTER = "https://trd-u9h06mqf2rtbee3pfh.z6.kusto.fabric.microsoft.com"
DATABASE = "Event_QA_KQLDB"
TABLE = "Reddit_Posts"
CSV_FILE = "reddit_posts.csv"
 
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
    id: string,
    title: string,
    selftext: string,
    comments: string,
    upvotes: real,
    created_utc: string,
    combined: string,
    feedback: string,
    post_content: string,
    post_type: string,
    build: string,
    version: string,
    sentiment: string,
    severity: string,
    resolved: bool,
    resolution_text: string
)
"""
mgmt_client.execute_mgmt(DATABASE, create_table)
csv_mapping_definition = [
    {"column": "id", "DataType": "string", "Ordinal": 0},
    {"column": "title", "DataType": "string", "Ordinal": 1},
    {"column": "selftext", "DataType": "string", "Ordinal": 2},
    {"column": "comments", "DataType": "string", "Ordinal": 3},
    {"column": "upvotes", "DataType": "real", "Ordinal": 4},
    {"column": "created_utc", "DataType": "string", "Ordinal": 5},
    {"column": "combined", "DataType": "string", "Ordinal": 6},
    {"column": "feedback", "DataType": "string", "Ordinal": 7},
    {"column": "post_content", "DataType": "string", "Ordinal": 8},
    {"column": "post_type", "DataType": "string", "Ordinal": 9},
    {"column": "build", "DataType": "string", "Ordinal": 10},
    {"column": "version", "DataType": "string", "Ordinal": 11},
    {"column": "sentiment", "DataType": "string", "Ordinal": 12},
    {"column": "severity", "DataType": "string", "Ordinal": 13},
    {"column": "resolved", "DataType": "bool", "Ordinal": 14},
    {"column": "resolution_text", "DataType": "string", "Ordinal": 15}
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
import os, pyodbc
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import io
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import pandas as pd
import json

load_dotenv()

# Replace these variables with your actual database credentials
#USEFUL FOR SQL DATABASE
server = os.environ.get('SERVER')
newServer = os.environ.get('NEWSERVER')
database = os.environ.get('DATABASE')
account_storage = os.environ.get('ACCOUNT_STORAGE')
sqlUser = os.environ.get('SQL_USERNAME')
sqlPass = os.environ.get('SQL_PASSWORD')

default_credential = DefaultAzureCredential()


sql_connection_string = "Driver={ODBC Driver 18 for SQL Server};"+f"Server=tcp:{server}.database.windows.net,1433;Database={database};UID={sqlUser};PWD={sqlPass};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30"
entra_connection_string = "Driver={ODBC Driver 18 for SQL Server};"+f"Server=tcp:{server}.database.windows.net,1433;Database={database};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30"
ankvo_connection_string = "Driver={ODBC Driver 18 for SQL Server};"+f"Server=tcp:{newServer},1433;Database={database};Uid={sqlUser};Pwd={sqlPass};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30"
ankvo_interesting_string = f'mssql+pyodbc://{sqlUser}:{sqlPass}@{newServer}/{database}?driver=ODBC+Driver+18+for+SQL+Server'

engine = create_engine(f'mssql+pyodbc://{sqlUser}:{sqlPass}@{newServer}/{database}?driver=ODBC+Driver+18+for+SQL+Server')
    
    
    
def get_sql_engine():
    return engine



#this is your starting constructor that allows you to access azure in the first place 
class AzureDB():
    #local_path is only for connecting whats locally here to azure, if it's already up there then theres no need to have it here 
    def __init__(self, local_path = "./data", account_storage = account_storage):
        self.local_path = local_path
        self.account_url = f"https://{account_storage}.blob.core.windows.net"
        self.default_credential = default_credential
        #self.blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        self.blob_service_client = BlobServiceClient(self.account_url, credential=self.default_credential)
        
        
    #you need to rune this before any other function after it, specify what function you want to access before doing things like delete, list,upload
    def access_container(self, container_name): 
        # Use this function to create/access a new container
        try:
            # Creating container if not exist
            self.container_client = self.blob_service_client.create_container(container_name)
            print(f"Creating container {container_name} since not exist in database")
            self.container_name = container_name
    
        except Exception as ex:
            print(f"Acessing container {container_name}")
            # Access the container
            self.container_client = self.blob_service_client.get_container_client(container=container_name)
            self.container_name = container_name
            
    def delete_container(self):
        # Delete a container
        print("Deleting blob container...")
        self.container_client.delete_container()
        print("Done")
        
    
    
    def upload_blob(self, blob_name, blob_data = None):
        # Create a file in the local data directory to upload as blob to Azure
        local_file_name = blob_name
        upload_file_path = os.path.join(self.local_path, local_file_name)
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=local_file_name)
        print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

        if blob_data is not None:
            blob_client.create_blob_from_text(container_name=self.container_name, blob_name=blob_name, text=blob_data)
        else:
            # Upload the created file
            with open(file=upload_file_path, mode="rb") as data:
                blob_client.upload_blob(data)
                
                
    def list_blobs(self):
        print("\nListing blobs...")
        # List the blobs in the container
        blob_list = self.container_client.list_blobs()
        for blob in blob_list:
            print("\t" + blob.name)  
            

    
    def access_blob_csv(self, blob_name):
        # Read the csv blob from Azure
        try:
            print(f"Acessing blob {blob_name}")
            
            df = pd.read_csv(io.StringIO(self.container_client.download_blob(blob_name).readall().decode('utf-8')))  
            return df      
        except Exception as ex:
            print('Exception:')
            print(ex)
            
            
        
    def download_blob(self, blob_name):
        # Download the blob to local storage
        download_file_path = os.path.join(self.local_path, blob_name)
        print("\nDownloading blob to \n\t" + download_file_path)
        with open(file=download_file_path, mode="wb") as download_file:
                download_file.write(self.container_client.download_blob(blob_name).readall())
                
                
    def upload_dataframe_sqldatabase(self, blob_name, blob_data):
        print("\nUploading to Azure SQL server as table:\n\t" + blob_name)
        
        #just these two lines are sufficient in uploading your your tables
        blob_data.to_sql(blob_name, engine, if_exists='replace', index=False)
        primary = blob_name.replace('dim', 'id')
        
        if 'fact' in blob_name.lower():
            with engine.connect() as con:
                trans = con.begin()
                #changes the data type of the primary key column to BIGINT
                con.execute(text(f'ALTER TABLE [dbo].[{blob_name}] alter column {blob_name}_id bigint NOT NULL'))
                #identify teh correct column as the PK column for the table (for both dimension tables and fact tables)
                con.execute(text(f'ALTER TABLE [dbo].[{blob_name}] ADD CONSTRAINT [PK_{blob_name}] PRIMARY KEY CLUSTERED ([{blob_name}_id] ASC);'))
                trans.commit() 
        else:        
            with engine.connect() as con:
                trans = con.begin()
                con.execute(text(f'ALTER TABLE [dbo].[{blob_name}] alter column {primary} bigint NOT NULL'))
                con.execute(text(f'ALTER TABLE [dbo].[{blob_name}] ADD CONSTRAINT [PK_{blob_name}] PRIMARY KEY CLUSTERED ([{primary}] ASC);'))
                trans.commit() 
    
    #adding data into an exsiting table instead of replacing it
    def append_dataframe_sqldatabase(self, blob_name, blob_data):
        print("\nAppending to table:\n\t" + blob_name)
        blob_data.to_sql(blob_name, engine, if_exists='append', index=False)
    
    def delete_sqldatabase(self, table_name):
        with engine.connect() as con:
            trans = con.begin()
            #compeletley delete table
            con.execute(text(f"DROP TABLE [dbo].[{table_name}]"))
            trans.commit()
            
            
            
    
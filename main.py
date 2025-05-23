import os, uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
from utils.dataSetup import *
from utils.dimension_classes import *


            
class mainETL():
    # List of columns need to be replaced -> columns that are extracted in turned into a dimension table should be taken away 
    def __init__(self) -> None:
        self.drop_columns = []
        self.dimension_tables = []
        
    def extract(self):
        print("Step 1: Extractin dim tables")
        self.dimension_tables = [
            Dim_Customer(),
            Dim_Dogs(),
            Dim_DogParks(),
            Dim_PetStores(),
            Dim_Staff(),
            Dim_Veterinary()
        ]
        print("extraction complete: ")
        for dim in self.dimension_tables:
            print(f"- {dim.name}: {dim.dimension_table.shape[0]} rows")
        
        print("Step 1 finished")
         
        
    def transform(self):
        
        print("fart")
        
        
    
    def load(self):
        for table in self.dimension_tables:
            table.load()
        with engine.connect() as con:
            trans = con.begin()
            self.fact_table['Total_Pay_Fact_id'] = range(1, len(self.fact_table) + 1)
            database.upload_dataframe_sqldatabase(f'Total_Pay_Fact', blob_data=self.fact_table)
            
            # self.fact_table['Total_Pay_Fact_id'] = range(len(self.fact_table) + 2, 2*(len(self.fact_table) + 1))
            # database.append_dataframe_sqldatabase(f'Total_Pay_Fact', blob_data=self.fact_table)
            self.fact_table.to_csv('./data/Total_Pay_Fact.csv')

            for table in self.dimension_tables:
                #adds constraint of foreign key,
                con.execute(text(f'ALTER TABLE [dbo].[Total_Pay_Fact] WITH NOCHECK ADD CONSTRAINT [FK_{table.name}_dim] FOREIGN KEY ([{table.name}_id]) REFERENCES [dbo].[{table.name}_dim] ([{table.name}_id]) ON UPDATE CASCADE ON DELETE CASCADE;'))
            trans.commit()
            
        print(f'Step 3 finished')
        
    def mainLoop(self):    
        self.extract()
        self.transform()
        self.load()
        
        
        
        
        
        
        

def test_azure_connections():
    # 1. Test Blob Storage Access
    try:
        print("=== Testing Blob Storage ===")
        azure_db = AzureDB()
        azure_db.access_container("grdogpark")  # Replace with your container name
        azure_db.list_blobs()  # List files to verify access
        dogParkTest = azure_db.access_blob_csv('dog_parks_wa_sa_osm.csv')
        print("inside dogpark is:\n", dogParkTest.head())
        
        print("=== Testing Cleaned Dimension Table ===")
        dogParksDim = Dim_DogParks()
        print(dogParksDim.dimension_table.head())  # This shows the cleaned + PK-added table


        print("✅ Blob Storage: Connected successfully!")
    except Exception as e:
        print(f"❌ Blob Storage Error: {e}")

    # 2. Test SQL Database Access
    try:
        print("\n=== Testing SQL Database ===")
        engine = get_sql_engine()  # From dataSetup.py (Entra ID auth)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))  # Simple test query
            print(f"✅ SQL Database: Connected successfully! (Result: {result.scalar()})")
            
    except Exception as e:
        #print(f"❌ SQL Database Error: {e}")
        import traceback
        print("❌ SQL Database Error:")
        print(f"Type: {type(e)}")
        print(f"Args: {e.args}")
        traceback.print_exc()




    
    
def main():
    # main = mainETL()
    # main.mainLoop()
    test_azure_connections()
    

if __name__ == "__main__":
    main()
    

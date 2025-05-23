from utils.dataSetup import *
import pandas as pd


#access database and container
# blob_name = "CustomerDim.csv"
# database = AzureDB()
# database.access_container("grcustomerdim")
# df = database.access_blob_csv(blob_name = blob_name)

#used to 
class ModelAbstract():
    
    def __init__(self, container_name: str, blob_name: str):
        self.database = AzureDB()
        self.database.access_container(container_name)
        self.df = self.database.access_blob_csv(blob_name)
        self.columns = None
        self.dimension_table = None
        
        
    #ntwo inputs - 1. name of the dimension table 2. columns you want to group together
    def dimension_generator(self, name:str, columns:list, addPK: bool = False):
        dim = self.df[columns]
        dim = dim.drop_duplicates()
        # Creating primary key for dimension table 
        if addPK:
            self.addPKFunc(dim,name)
        
        self.dimension_table = dim
        self.name = name
        self.columns = columns
        
        
        #for demo purposes we will save the dimension table file (to see the end results maybe)
        dim.to_csv(self.name + ".csv")
        
    def addPKFunc(self, dim: pd.DataFrame, name: str): 
        dim.insert(0, f'{name}_key', range(1, len(dim) + 1))  # Insert ID at start
        
    def load(self):
        if self.dimension_table is not None:
            # Upload dimension table to data warehouse
            database.upload_dataframe_sqldatabase(f'{self.name}_dim', blob_data=self.dimension_table)
        
            # Saving dimension table as separate file
            self.dimension_table.to_csv(f'./data/{self.name}_dim.csv')
        else:
            print("Please create a dimension table first using dimension_generator") 

        


#Doggos Down Under Dimension Tables 
class Dim_Customer(ModelAbstract):
    def __init__(self):
        super().__init__(
            container_name='grcustomerdim',
            blob_name='CustomerDim.csv'
        )
        self.dimension_generator(name='Dim_Customer',
                                 columns=['UsernameC','FullNameC','DogKey','AgeC','Phone_NumberC','EmailC','PasswordC','Matches'], addPK=True)
        

class Dim_Dogs(ModelAbstract):
    def __init__(self):
        super().__init__(
            container_name='grdogdim',
            blob_name='DogDim.csv'
        )
        self.dimension_generator(name='Dim_Dogs', 
                                 columns=['DogName','DogBreed','DogAge','DogGender','DogPersonality','DogSuburb','DogState','DogLongitude','DogLatitude'], addPK=True)

#DOG PARKS NAME FIELD NEEDS TO BE FIXED        
class Dim_DogParks(ModelAbstract):
    def __init__(self):
        super().__init__(container_name="grdogpark",
                         blob_name='dog_parks_wa_sa_osm.csv')
        
        # Now modify the already-loaded self.df
        self.df['Name'] = self.df['Name'].str.split(', ').str[:2].str.join(', ')
        
        self.dimension_generator(name='Dim_DogParks',
                                 columns=['Name', 'State', 'Longitude', 'Latitude'],
                                 addPK=True)

        
        
        
#PET STORE NAMES NEEDS TO BE FIXED        
class Dim_PetStores(ModelAbstract):
    def __init__(self):
        super().__init__(container_name="grpetstore",
                         blob_name='pet_stores_wa_sa_osm.csv')
        
        # Now modify the already-loaded self.df
        self.df['Name'] = self.df['Name'].str.split(', ').str[:2].str.join(', ')
        
        self.dimension_generator(name='Dim_PetStores',
                                 columns=['Name', 'State', 'Longitude', 'Latitude'],
                                 addPK=True)
        
        
class Dim_Staff(ModelAbstract):
    def __init__(self):
        super().__init__(
            container_name='grstaffdim',
            blob_name='StaffDim.csv'
        )
        self.dimension_generator(name='Dim_Staff', 
                                 columns=['Role', 'FullNameS', 'PhoneNumberS', 'EmailS', 'PasswordS'], addPK=True)
        


#VET NAMES NEEDS TO BE FIXED        
class Dim_Veterinary(ModelAbstract):
    def __init__(self):
        super().__init__(container_name="grveterinary",
                         blob_name='veterinary_wa_sa_osm.csv')
        
        # Now modify the already-loaded self.df
        self.df['Name'] = self.df['Name'].str.split(', ').str[:2].str.join(', ')
        
        self.dimension_generator(name='Dim_Veterinary',
                                 columns=['Name', 'State', 'Longitude', 'Latitude'],
                                 addPK=True)
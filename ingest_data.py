import pandas as pd
from sqlalchemy import create_engine
from time import time

# Database connection parameters 
db_user = 'your_user'           
db_password = 'your_password'       
db_host = 'localhost'
db_port = '5432'           
db_name = 'ny_taxi'

# Create connection string
connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
engine = create_engine(connection_string)

print("Loading parquet file...")
# Read the parquet file
df_green = pd.read_parquet('green_tripdata_2025-11.parquet')

print(f"Loaded {len(df_green)} rows from parquet file")
print(f"Columns: {df_green.columns.tolist()}")

# Convert datetime columns if needed
if 'lpep_pickup_datetime' in df_green.columns:
    df_green['lpep_pickup_datetime'] = pd.to_datetime(df_green['lpep_pickup_datetime'])
if 'lpep_dropoff_datetime' in df_green.columns:
    df_green['lpep_dropoff_datetime'] = pd.to_datetime(df_green['lpep_dropoff_datetime'])

print("\nInserting green taxi data into PostgreSQL...")
t_start = time()

# Insert data in chunks for better performance
df_green.to_sql(name='green_taxi_trips', con=engine, if_exists='replace', index=False, chunksize=10000)

t_end = time()
print(f"Green taxi data inserted in {t_end - t_start:.2f} seconds")

# Load the zone lookup CSV
print("\nLoading zone lookup CSV...")
df_zones = pd.read_csv('taxi_zone_lookup.csv')

print(f"Loaded {len(df_zones)} zones")
print(f"Columns: {df_zones.columns.tolist()}")

print("\nInserting zone lookup data into PostgreSQL...")
df_zones.to_sql(name='taxi_zone_lookup', con=engine, if_exists='replace', index=False)

print("\nData ingestion complete")
print(f"Tables created:")
print(f"  - green_taxi_trips: {len(df_green)} rows")
print(f"  - taxi_zone_lookup: {len(df_zones)} rows")

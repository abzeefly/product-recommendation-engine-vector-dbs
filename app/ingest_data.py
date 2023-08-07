import pandas as pd
import os
import asyncio
import asyncpg
from google.cloud.sql.connector import Connector


project_id = os.environ("project_id")
region = os.environ("region")
instance_name = os.environ("instance_name")
database_user = os.environ("database_user")
database_password = os.environ("database_password")
database_name = os.environ("database_name")
GOOGLE_APPLICATION_CREDENTIALS = os.enivron("credentials.json")


DATASET_URL = "https://github.com/GoogleCloudPlatform/python-docs-samples/raw/main/cloud-sql/postgres/pgvector/data/retail_toy_dataset.csv"
df = pd.read_csv(DATASET_URL)
df = df.loc[:, ["product_id", "product_name", "description", "list_price"]]
df = df.dropna()
df.head(10)

print(f"{len(df)} rows")

async def main():
    
    loop = asyncio.get_running_loop()
    
    async with Connector(loop=loop) as connector:
        # Create connection to Cloud SQL database
        conn: asyncpg.Connection = await connector.connect_async(
            f"{project_id}:{region}:{instance_name}",  # Cloud SQL instance connection name
            "asyncpg",
            user=f"{database_user}",
            password=f"{database_password}",
            db=f"{database_name}",
        )

        await conn.execute("DROP TABLE IF EXISTS products CASCADE")
        # Create the `products` table.
        await conn.execute(
            """CREATE TABLE products(
                                product_id VARCHAR(1024) PRIMARY KEY,
                                product_name TEXT,
                                description TEXT,
                                list_price NUMERIC)"""
        )

        # Copy the dataframe to the `products` table.
        tuples = list(df.itertuples(index=False))
        await conn.copy_records_to_table(
            "products", records=tuples, columns=list(df), timeout=10
        )
        
        # query Cloud SQL database
        results = await conn.fetch("SELECT Count(*) FROM products")
        print(results[0])
        
        await conn.close()
        
        print("done")
        
        
# Run the SQL commands now.
await main()  # type: ignore
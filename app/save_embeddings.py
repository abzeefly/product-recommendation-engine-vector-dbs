import asyncio
import asyncpg
import os
from google.cloud.sql.connector import Connector
import numpy as np
from pgvector.asyncpg import register_vector

project_id = os.environ("project_id")
region = os.environ("region")
instance_name = os.environ("instance_name")
database_user = os.environ("database_user")
database_password = os.environ("database_password")
database_name = os.environ("database_name")
GOOGLE_APPLICATION_CREDENTIALS = os.enivron("credentials.json")

async def save_embeds_to_pg(product_embeddings):
    loop = asyncio.get_running_loop()
    async with Connector(loop=loop) as connector:
        # Create connection to Cloud SQL database.
        conn: asyncpg.Connection = await connector.connect_async(
            f"{project_id}:{region}:{instance_name}",  # Cloud SQL instance connection name
            "asyncpg",
            user=f"{database_user}",
            password=f"{database_password}",
            db=f"{database_name}",
        )

        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        await register_vector(conn)

        await conn.execute("DROP TABLE IF EXISTS product_embeddings")
        # Create the `product_embeddings` table to store vector embeddings.
        await conn.execute(
            """CREATE TABLE product_embeddings(
                                product_id VARCHAR(1024) NOT NULL REFERENCES products(product_id),
                                content TEXT,
                                embedding vector(768))"""
        )

        # Store all the generated embeddings back into the database.
        for index, row in product_embeddings.iterrows():
            await conn.execute(
                "INSERT INTO product_embeddings (product_id, content, embedding) VALUES ($1, $2, $3)",
                row["product_id"],
                row["content"],
                np.array(row["embedding"]),
            )
        
        # query Cloud SQL database
        results = await conn.fetch("SELECT Count(*) FROM product_embeddings")
        print(results[0])        
        print("done")
        
        await conn.close()
        

# Run the SQL commands now.
await save_embeds_to_pg()  # type: ignore
# toy = "playing card games"  # @param {type:"string"}
# min_price = 25  # @param {type:"integer"}
# max_price = 100  # @param {type:"integer"}

from langchain.embeddings import VertexAIEmbeddings
from google.cloud import aiplatform
from pgvector.asyncpg import register_vector
import asyncio
import asyncpg
from google.cloud.sql.connector import Connector
import pandas as pd
import os

project_id = os.environ("project_id")
region = os.environ("region")
instance_name = os.environ("instance_name")
database_user = os.environ("database_user")
database_password = os.environ("database_password")
database_name = os.environ("database_name")
GOOGLE_APPLICATION_CREDENTIALS = os.enivron("credentials.json")


aiplatform.init(project=f"{project_id}", location=f"{region}")



def get_predictions(toy, min_price, max_price) : 
    embeddings_service = VertexAIEmbeddings()
    qe = embeddings_service.embed_query([toy])
    matches = []

    async def main():
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

            await register_vector(conn)
            similarity_threshold = 0.1
            num_matches = 50

            # Find similar products to the query using cosine similarity search
            # over all vector embeddings. This new feature is provided by `pgvector`.
            results = await conn.fetch(
                """
                                WITH vector_matches AS (
                                SELECT product_id, 1 - (embedding <=> $1) AS similarity
                                FROM product_embeddings
                                WHERE 1 - (embedding <=> $1) > $2
                                ORDER BY similarity DESC
                                LIMIT $3
                                )
                                SELECT product_name, list_price, description FROM products
                                WHERE product_id IN (SELECT product_id FROM vector_matches)
                                AND list_price >= $4 AND list_price <= $5
                                """,
                qe,
                similarity_threshold,
                num_matches,
                min_price,
                max_price,
            )

            if len(results) == 0:
                raise Exception("Did not find any results. Adjust the query parameters.")

            for r in results:
                # Collect the description for all the matched similar toy products.
                matches.append(
                    {
                        "product_name": r["product_name"],
                        "description": r["description"],
                        "list_price": round(r["list_price"], 2),
                    }
                )

            await conn.close()


    # Run the SQL commands now.
    await main()  # type: ignore

    # Show the results for similar products that matched the user query.
    matches = pd.DataFrame(matches)
    matches.head(5)
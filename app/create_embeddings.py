import pandas as pd
import os
import time
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import VertexAIEmbeddings
from google.cloud import aiplatform
from tqdm.auto import tqdm

project_id = os.environ("project_id")
region = os.environ("region")
GOOGLE_APPLICATION_CREDENTIALS = os.environ("credentials.json")


DATASET_URL = "https://github.com/GoogleCloudPlatform/python-docs-samples/raw/main/cloud-sql/postgres/pgvector/data/retail_toy_dataset.csv"
df = pd.read_csv(DATASET_URL)
df = df.loc[:, ["product_id", "product_name", "description", "list_price"]]
df = df.dropna()
df.head(10)

print(f"{len(df)} rows")


text_splitter = RecursiveCharacterTextSplitter(
    separators=[".", "\n"],
    chunk_size=500,
    chunk_overlap=0,
    length_function=len,
)
chunked = []

with tqdm(total=len(df)) as pbar:
    for index, row in df.iterrows():
        product_id = row["product_id"]
        desc = row["description"]
        splits = text_splitter.create_documents([desc])
        for s in splits:
            r = {"product_id": product_id, "content": s.page_content}
            chunked.append(r)
        
        # visual indicator 
        pbar.update()
        
print(f"Chunks: {len(chunked)}")    

# Generate the vector embeddings for each chunk of text.
# This code snippet may run for a few minutes.

aiplatform.init(project=f"{project_id}", location=f"{region}")
embeddings_service = VertexAIEmbeddings()
from tqdm.auto import tqdm

# Helper function to retry failed API requests with exponential backoff.
def retry_with_backoff(func, *args, retry_delay=5, backoff_factor=2, **kwargs):
    max_attempts = 10
    retries = 0
    for i in range(max_attempts):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"error: {e}")
            retries += 1
            wait = retry_delay * (backoff_factor**retries)
            print(f"Retry after waiting for {wait} seconds...")
            time.sleep(wait)


batch_size = 5

with tqdm(total=len(chunked)/batch_size) as pbar:
    for i in range(0, len(chunked), batch_size):

        request = [x["content"] for x in chunked[i : i + batch_size]]
        response = retry_with_backoff(embeddings_service.embed_documents, request)

        # Store the retrieved vector embeddings for each chunk back.
        for x, e in zip(chunked[i : i + batch_size], response):
            x["embedding"] = e

        pbar.update()
            
# Store the generated embeddings in a pandas dataframe.
product_embeddings = pd.DataFrame(chunked)
product_embeddings.head()
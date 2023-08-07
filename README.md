# Product Recommendations using Text promts from users using PostsreSQLs vector search
We are using PostgreSQL as a Vector DB and generating embeddings for product properties using Vertex AI's text embeddings and storing in an RDBMS. 
PostgreSQLs vector search uses Cosine distance to find the most related product given an input from the user.

# Instructions:
### Setup enivronment using poetry
```
poetry config virtualenvs.in-project true
poetry shell
```

### Make sure you have access to the following resources on GCP:
1. PostgreSQL DB instance, a Product DB, a User
2. Vertex AI API

### Create a service account with the follwoing roles:
1. Cloud SQL Storage Admin
2. Vertex AI User

### Downlaod the credentials.json file and replace it with the empty credentials file in root folder.

### Reconfigure the Dockerfile with your own environment variables

### Build the container
```docker build .```

### Run the docker conatiner
``` docker run --publish 8080:8080 ```

### Send a cURL request for predictions
```
curl -m 310 -X POST https://localhost:8080
-H "Content-Type: application/json" \
-d '{
 "instances": [
  ["playing card games", "25", "100"]
 ]
}'
```

### Get Predictions back as 

```
'{
  "predictions":[
    ["Purple Mini Poker Chips Plastic 7/8in Bulk "]
  ]
}'

```

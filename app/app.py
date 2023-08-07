import pickle
import os
from google.cloud import storage
from flask import Flask, jsonify, request
import re
import numpy as np
from get_prediction import get_predictions


import warnings
warnings.filterwarnings("ignore")

project_id = os.environ("project_id")
region = os.environ("region")
instance_name = os.environ("instance_name")
database_user = os.environ("database_user")
database_password = os.environ("database_password")
database_name = os.environ("database_name")
GOOGLE_APPLICATION_CREDENTIALS = os.enivron("credentials.json")

app = Flask(__name__)

@app.route('/predict', methods=["POST"])
def batch_get_category():
    return_value = []
    request_json = request.get_json()
    calls = request_json["instances"]
    for call in calls:
        toy, min_price, max_price = call[0], call[1], call[2]
        try:
            predicted_toys = get_predictions(toy, min_price, max_price)
        except:
            predicted_toys = ""
        return_value.append(predicted_toys)
    return_json = jsonify({"predictions": return_value})
    return return_json

 
@app.route('/health', methods=['GET'])
def health_check():
   return {"status": "200"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
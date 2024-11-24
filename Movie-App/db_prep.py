'''Insert ratings.csv and movies.csv into MongoDB'''

from pymongo import MongoClient
import pandas as pd
import os

# load csv file into pandas DataFrame first
ratings_df = pd.read_csv("../dataset/ml-latest-small/ratings.csv")
movies_df = pd.read_csv("../dataset/ml-latest-small/movies.csv")

# specify Mongodb client, database and collection
client = MongoClient('mongodb://localhost:27017/')
db = client["test"]

# convert DataFrame to a list of dictionaries (one for each row)
ratings_data = ratings_df.to_dict(orient="records")
movies_data = movies_df.to_dict(orient="records")

# insert data into MongoDB
db["ratings"].insert_many(ratings_data)
db["movies"].insert_many(movies_data)
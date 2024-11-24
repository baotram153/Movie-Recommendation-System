import pandas as pd
from pymongo import MongoClient
from pyspark.sql import SparkSession, functions as F
import os
from pyspark.sql.functions import year
import time

# ----------------- Load data from MongoDB -----------------
def initialize_spark():
    # initialize SparkSession
    spark = SparkSession.builder \
        .appName("Big-Data-Demo") \
        .master("local[*]") \
        .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
        .config("spark.mongodb.read.connection.uri", "mongodb://127.0.0.1:27017/") \
        .getOrCreate()
    return spark

def load_data (spark):
    # load all data from MongoDB
    df_ratings = spark.read.format("mongo")\
        .option("uri", "mongodb://127.0.0.1:27017/")\
        .option("database", "test")\
        .option("collection", "ratings")\
        .load()    

    df_movies = spark.read.format("mongo")\
        .option("uri", "mongodb://127.0.0.1:27017/test.movies")\
        .option("database", "test")\
        .option("collection", "movies")\
        .load()   

def preprocess_data(df_ratings, df_movies):
    # join the two DataFrames
    joined_df = df_movies.join(df_ratings, on="movieId", how="right")

    # create a "year" column
    joined_df = joined_df.withColumn("year", F.substring("title", -5, 4))
    joined_df = joined_df.filter(F.col("year").rlike("^[12]"))
    joined_df = joined_df.withColumn("year", F.col("year").cast("int"))
    ratings = joined_df.select("userId", "movieId", "rating")
    (training, test) = ratings.randomSplit([0.8, 0.2])
    return training, test


# ----------------- Train the ASL model -----------------
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql import Row

# todo: save the model
def train(training):
    # set cold start strategy to 'drop' to ensure we don't get NaN evaluation metrics
    als = ALS(maxIter=5, regParam=0.01, userCol="userId", itemCol="movieId", ratingCol="rating",
            coldStartStrategy="drop")
    model = als.fit(training)
    return model

# evaluate
def evaluate (model, test):
    predictions = model.transform(test)
    evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating",
                                    predictionCol="prediction")
    rmse = evaluator.evaluate(predictions)
    return rmse

if __name__ == "__main__":
    spark = initialize_spark()
    df_ratings, df_movies = load_data(spark)
    training, test = preprocess_data(df_ratings, df_movies)
    model = train(training)
    rmse = evaluate(model, test)
    print("Root-mean-square error = " + str(rmse))

    # save the model
    model.save("als_model")

# # top 10 movie recommendations for each user
# userRecs = model.recommendForAllUsers(10)
# # top 10 user recommendations for each movie
# movieRecs = model.recommendForAllItems(10)

# # top 10 movie recommendations for a specified set of users
# users = ratings.select(als.getUserCol()).distinct().limit(3)
# userSubsetRecs = model.recommendForUserSubset(users, 10)

# # top 10 user recommendations for a specified set of movies
# movies = ratings.select(als.getItemCol()).distinct().limit(3)
# movieSubSetRecs = model.recommendForItemSubset(movies, 10)
import pandas as pd
from pymongo import MongoClient
from pyspark.sql import SparkSession, functions as F
import os
from pyspark.sql.functions import year
from pyspark import SparkContext
import time 
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    return df_ratings, df_movies

def preprocess_data(df_ratings, df_movies):
    # join the two DataFrames
    joined_df = df_movies.join(df_ratings, on="movieId", how="right")

    # create a "year" column
    joined_df = joined_df.withColumn("year", F.substring("title", -5, 4))
    joined_df = joined_df.filter(F.col("year").rlike("^[12]"))
    joined_df = joined_df.withColumn("year", F.col("year").cast("int"))

    # select only the columns we need for training
    ratings = joined_df.select("userId", "movieId", "rating")
    (training, test) = ratings.randomSplit([0.8, 0.2])
    return training, test


# ----------------- Train the ASL model -----------------
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql import Row

# todo: save the model
class MovieRecommender:
    def __init__(self):
        spark = initialize_spark()
        self.df_ratings, self.df_movies = load_data(spark)
        self.training, self.test = preprocess_data(self.df_ratings, self.df_movies)
        self.model = self.train()
        rmse = self.evaluate()
        print("Root-mean-square error = " + str(rmse))
        self.df_avg_rating = self.df_ratings.groupBy("movieId").avg("rating")

    def train(self):
        # set cold start strategy to 'drop' to ensure we don't get NaN evaluation metrics
        als = ALS(maxIter=5, regParam=0.01, userCol="userId", itemCol="movieId", ratingCol="rating",
                coldStartStrategy="drop")
        model = als.fit(self.training)
        return model

    # evaluate
    def evaluate (self):
        predictions = self.model.transform(self.test)
        evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating",
                                        predictionCol="prediction")
        rmse = evaluator.evaluate(predictions)
        return rmse
    
    def get_recs_from_all_user (self, format="df"):
        '''
        Specify the format of the output: "json", "df" (dataframe)
        '''
        userRecs = self.model.recommendForAllUsers(10)
        if (format == "json"):
            return json.dumps(userRecs.collect())
        elif (format == "df"):
            return userRecs
        
    def get_recs_from_user_subset (self, df_user, format="df"):
        # users = self.df_ratings.select(self.model.getUserCol()).distinct().limit(3)
        userSubsetRecs = self.model.recommendForUserSubset(df_user, 10)
        logger.info(userSubsetRecs)
        if (format == "json"):
            return json.dumps(userSubsetRecs.collect())
        elif (format == "df"):
            return userSubsetRecs
        
    def get_recs_from_user_id_with_title (self, id):
        df_user = self.df_ratings.filter(F.col("userId") == id).select("userId")
        logger.info(df_user)
        userRecs = self.get_recs_from_user_subset(df_user, format="df").collect()
        logger.info(userRecs)
        # find movie name for each movieId
        recommended_movies = dict()
        for userRec in userRecs:
            for rec in userRec.recommendations:
                movie_id = rec.movieId
                movie_name = self.df_movies.filter(F.col("movieId") == movie_id).select("title").collect()[0].title
                recommended_movies[movie_id] = movie_name
        return recommended_movies
        
    def get_recs_from_all_movies (self, format="df"):
        movieRecs = self.model.recommendForAllItems(10)
        if (format == "json"):
            return json.dumps(movieRecs.collect())
        elif (format == "df"):
            return movieRecs
        
    def get_recs_from_movie_id (self, id, format="df"):
        df_movie = self.df_movies.filter(F.col("movieId") == id).select("movieId")
        movieRecs = self.model.recommendForItemSubset(df_movie, 10)

        # check if movie id exists
        if not movieRecs.filter(F.col("movieId") == id).count():
            return "Movie ID not found"
        if (format == "json"):
            return json.dumps(movieRecs.filter(F.col("movieId") == id).collect())
        elif (format == "df"):
            return movieRecs.filter(F.col("movieId") == id)
        elif (format == "list"):
            user_list = []
            for movieRec in movieRecs.collect():
                for user in movieRec.recommendations:
                    user_list.append(user.userId)
            return user_list
        
    def calculate_avg_rating (self):
        avg_rating = self.df_avg_rating.limit(50)
        avg_rating_with_title = avg_rating.join(self.df_movies, on="movieId", how="left").select("movieId", "title", "avg(rating)")
        return json.dumps(avg_rating_with_title.collect())
    
    def calculate_rating_movie_id (self, id):
        avg_rating_of_id = self.df_avg_rating.filter(F.col("movieId") == id).join(self.df_movies, on="movieId", how="left").select("movieId", "title", "avg(rating)")
        logger.info(avg_rating_of_id)
        return json.dumps(avg_rating_of_id.collect())
    
    def sort_ratings (self, desc=True):
        if desc:
            sorted_ratings = self.df_avg_rating.orderBy("avg(rating)", ascending=False).limit(50).join(self.df_movies, on="movieId", how="left").select("movieId", "title", "avg(rating)")
        else:
            sorted_ratings = self.df_avg_rating.orderBy("avg(rating)", ascending=True).limit(50).join(self.df_movies, on="movieId", how="left").select("movieId", "title", "avg(rating)")
        return json.dumps(sorted_ratings.collect())
    
    def get_movie_by_id (self, movie_id):
        movie_title = self.df_movies.filter(F.col("movieId") == movie_id).select("title").collect()[0].title
        return movie_title
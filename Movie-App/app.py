'''
Create a Movie Recommendation App using Flask
    - Input: user's list of movies and corresponding ratings
    - Output: list of recommended movies
'''

from flask import Flask, request, jsonify, url_for, redirect, render_template

from flask_sqlalchemy import SQLAlchemy

from movie_recommender import MovieRecommender
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# initialize flask app
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/input', methods=['GET', 'POST'])
def input():
    return render_template('input.html')

@app.route('/recommend_movies', methods=['GET', 'POST'])
def recommend_movies():
    # logger.info(request.form)
    user_id = request.form['userId']
    logger.info("User %s requested recommendations", user_id)
    recommended_movies = model.get_recs_from_user_id_with_title(user_id)
    logger.info(recommended_movies)
    return render_template('show_movie_list.html', user_id=user_id, recommended_movies=recommended_movies)

@app.route('/recommend_users', methods=['GET', 'POST'])
def recommend_users():
    movieId = request.form['movieId']
    logger.info("Movie %s requested recommendations", movieId)
    recommended_users = model.get_recs_from_movie_id(movieId, format="list")
    return render_template('show_user_list.html', recommended_users=recommended_users)


@app.route('/recommend_movies_all_users', methods=['GET', 'POST'])
def recommend_movies_all_users():
    recommended_movies = model.get_recs_from_all_user(format="list")
    return render_template('show_movie_list_all_users.html', recommended_movies=recommended_movies)

@app.route('/recommend_users_all_movies', methods=['GET', 'POST'])
def recommend_users_all_movies():
    recommended_users = model.get_recs_from_all_movies(format="list")
    return render_template('show_user_list_all_movies.html', recommended_users=recommended_users)



@app.route('/movie_ratings', methods=['GET', 'POST'])
def get_movie_ratings():
    user_id = request.form['user_id']
    movie_id = request.form['movie_id']
    logger.debug("User %s rating requested for movie %s", user_id, movie_id)
    ratings = model.get_ratings_for_movie_ids(user_id, [movie_id])
    return json.dumps(ratings)

if __name__ == '__main__':
    global model
    model = MovieRecommender()
    app.run(debug=True)

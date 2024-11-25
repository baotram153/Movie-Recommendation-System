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
    logger.debug("User %s requested recommendations", user_id)
    recommended_movies = model.get_recs_from_user_id_with_title(user_id)
    logger.debug(recommended_movies)
    return render_template('show_movie_list.html', user_id=user_id, recommended_movies=recommended_movies)

@app.route('/recommend_users', methods=['GET', 'POST'])
def recommend_users():
    movieId = request.form['movieId']
    logger.debug("Movie %s requested recommendations", movieId)
    recommended_users = model.get_recs_from_movie_id(movieId, format="list")
    movie_title = model.get_movie_by_id(movieId)
    return render_template('show_user_list.html', recommended_users=recommended_users, movie_id=movieId, movie_title=movie_title)


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
    if (request.method == 'POST'):
        movie_id = request.form['movie_id']
        return redirect('/move_ratings/' + movie_id)
    else:
        logger.debug("Get movie ratings for the first 50 movies")
        ratings = model.calculate_avg_rating()
        logger.debug(ratings)
        ratings = json.loads(ratings)
        return render_template('show_movie_ratings.html', movie_avg_ratings=ratings)

@app.route('/move_ratings/<int:movie_id>', methods=['GET', 'POST'])
def calculate_movie_rating_by_id(movie_id):
    if (request.method == 'POST'):
        input_movie_id = request.form['movie_id']
        return redirect('/move_ratings/' + input_movie_id)
    else:
        logger.debug("Get movie ratings for movie %s", movie_id)
        rating = model.calculate_rating_movie_id(movie_id)
        rating = json.loads(rating)
        logger.debug(rating)
        return render_template('show_movie_ratings.html', movie_avg_ratings=rating)
    
@app.route('/movie_ratings/sorted/<int:asc>', methods=['GET', 'POST'])
def get_movie_ratings_sorted(asc):
    if asc:
        ratings = model.sort_ratings(desc=False)
        ratings = json.loads(ratings)
        logger.debug(ratings)
        return render_template('show_movie_ratings.html', movie_avg_ratings=ratings)
    else:
        ratings = model.sort_ratings(desc=True)
        ratings = json.loads(ratings)
        logger.debug(ratings)
        return render_template('show_movie_ratings.html', movie_avg_ratings=ratings)

if __name__ == '__main__':
    global model
    model = MovieRecommender()
    app.run(debug=True)
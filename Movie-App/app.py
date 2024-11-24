'''
Create a Movie Recommendation App using Flask
    - Input: user's list of movies and corresponding ratings
    - Output: list of recommended movies
'''

from flask import Flask, request, jsonify

from flask_sqlalchemy import SQLAlchemy

# initialize flask app
app = Flask(__name__)

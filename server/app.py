#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, session
from flask_migrate import Migrate
import os

from models import db, Article, User, ArticleSchema, UserSchema

app = Flask(__name__)
app.secret_key = b'\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'

# Get the absolute path to the current directory
basedir = os.path.abspath(os.path.dirname(__file__))
# Create the database file path
database_path = os.path.join(basedir, 'app.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/clear')
def clear_session():
    session['page_views'] = 0
    return {'message': '200: Successfully cleared session data.'}, 200

@app.route('/articles')
def index_articles():
    articles = [ArticleSchema().dump(a) for a in Article.query.all()]
    return make_response(articles)

@app.route('/articles/<int:id>')
def show_article(id):
    # Step 1: Initialize the session for page views
    if 'page_views' not in session:
        session['page_views'] = 0
    
    # Step 2: Increment the session on each request
    session['page_views'] += 1
    
    # Step 3: Send response based on session data
    if session['page_views'] <= 3:
        # User has viewed 3 or fewer pages, show the article
        article = Article.query.filter(Article.id == id).first()
        if article:
            return make_response(ArticleSchema().dump(article))
        else:
            return {'message': 'Article not found'}, 404
    else:
        # User has viewed more than 3 pages, show paywall
        return {'message': 'Maximum pageview limit reached'}, 401

if __name__ == '__main__':
    app.run(port=5555)
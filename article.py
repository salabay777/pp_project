from flask import Blueprint, Response, request, jsonify
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import or_

from dbmodel import Article, Session, User, Role, Status
from validation_schemas import ArticleSchema
from datetime import datetime

article = Blueprint('article', __name__)
bcrypt = Bcrypt()

session = Session()
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    try:
        user = session.query(User).filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return username
    except:
        return None


@article.route('/api/v1/article', methods=['POST'])
@auth.login_required
def create_article():
    # Get data from request body
    data = request.get_json()

    # Validate input data
    try:
        ArticleSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Check if article already exists
    exists = session.query(Article.article_id).filter_by(title=data['title']).first()
    if exists:
        return Response(status=409, response='Article with such title already exists.')

    article_user_id = session.query(User).filter_by(username=auth.username()).first().user_id

    moderator = session.query(User).filter_by(username=data['moderator']).first()
    if not moderator or moderator.role_id != 2:
        return Response(status=404, response='Moderator with such username was not found.')

    # Create new article
    new_article = Article(
        title=data['title'],
        text=data['text'],
        user_id=article_user_id,
        moderator_id=moderator.user_id,
        date=datetime.today().strftime('%Y-%m-%d'),
        status_id=1
    )

    # Add new article to db
    session.add(new_article)
    session.commit()

    return Response(status=200, response='New article was successfully created!')


# Get all articles
@article.route('/api/v1/articles', methods=['GET'])
def get_articles():
    # Get all audiences from db
    articles = session.query(Article).filter_by(status_id=2).order_by(Article.date.desc())

    # Return all audiences
    output = []
    for a in articles:
        a_username = session.query(User).filter_by(user_id=a.user_id).first().username
        output.append({'id': a.article_id,
                       'title': a.title,
                       'text': a.text,
                       'author_username': a_username,
                       'moderator_id': a.moderator_id,
                       'date': a.date,
                       'status_id': a.status_id})
    return jsonify({"articles": output})


# Search articles by title and text
@article.route('/api/v1/search', methods=['GET'])
def search_articles():
    seartchTerm = request.args.get('searchTerm')
    if not seartchTerm:
        return Response(status=404, response="Search term is missing.")
    # Get searched articles from db
    articles = session.query(Article).filter(
        or_(
            Article.title.like("%" + seartchTerm + "%"),
            Article.text.like("%" + seartchTerm + "%")
        )
    ).order_by(Article.date.desc())

    # Return all audiences
    output = []
    for a in articles:
        a_username = session.query(User).filter_by(user_id=a.user_id).first().username
        a_status = session.query(Status).filter_by(status_id=a.status_id).first().status
        output.append({'id': a.article_id,
                       'title': a.title,
                       'text': a.text,
                       'author_username': a_username,
                       'moderator_id': a.moderator_id,
                       'date': a.date,
                       'status': a_status})
    return jsonify({"articles": output})


# Get all articles for given user
@article.route('/api/v1/user-articles/<username>', methods=['GET'])
def get_user_articles(username):
    # Get current user
    db_user = session.query(User).filter_by(username=username).first()
    # Get all articles from db
    articles = session.query(Article).filter_by(user_id=db_user.user_id).order_by(Article.date.desc())

    # Return all articles
    output = []
    for a in articles:
        db_status = session.query(Status).filter_by(status_id=a.status_id).first()
        output.append({'id': a.article_id,
                       'title': a.title,
                       'text': a.text,
                       'author_username': db_user.username,
                       'moderator_id': a.moderator_id,
                       'date': a.date,
                       'status': db_status.status})
    return jsonify({"articles": output})


# Get all articles for given moderator
@article.route('/api/v1/review-articles/<username>', methods=['GET'])
@auth.login_required
def get_moderator_artiles(username):
    # Get current user
    db_moderator = session.query(User).filter_by(username=username).first()
    if (not db_moderator):
        return Response(status=404, response="User with such username was not found.")
    if (db_moderator.role_id == 1 or db_moderator.username != auth.username()):
        return Response(status=406, response='You are not allowed to perform this operation.')

    # Get all articles from db
    articles = session.query(Article).filter_by(moderator_id=db_moderator.user_id).order_by(Article.date.desc())

    # Return all articles
    output = []
    for a in articles:
        db_status = session.query(Status).filter_by(status_id=a.status_id).first()
        db_user = session.query(User).filter_by(user_id=a.user_id).first()
        output.append({'id': a.article_id,
                       'title': a.title,
                       'text': a.text,
                       'author_username': db_user.username,
                       'moderator_username': db_moderator.username,
                       'date': a.date,
                       'status': db_status.status})
    return jsonify({"articles": output})


# Get article by id
@article.route('/api/v1/article/<articleId>', methods=['GET'])
def get_article(articleId):
    # Check if supplied userId correct
    if int(articleId) < 1:
        return Response(status=400, response='Invalid articleId supplied')

    # Check if user exists
    db_article = session.query(Article).filter_by(article_id=articleId).first()
    if not db_article:
        return Response(status=404, response='A article with provided ID was not found.')

    article_user = session.query(User).filter_by(user_id=db_article.user_id).first()
    article_moderator = session.query(User).filter_by(user_id=db_article.moderator_id).first()
    article_status = session.query(Status).filter_by(status_id=db_article.status_id).first()
    if not (article_user and article_moderator and article_status):
        return Response(status=404, response='Some data about this article is missing.')

    # Return user data
    article_data = {
        'article_id': db_article.article_id,
        'title': db_article.title,
        'text': db_article.text,
        'user': {
            'username': article_user.username,
            'first_name': article_user.first_name,
            'last_name': article_user.last_name,
            'email': article_user.email
        },
        'moderator': {
            'username': article_moderator.username,
            'first_name': article_moderator.first_name,
            'last_name': article_moderator.last_name,
            'email': article_moderator.email
        },
        'date': db_article.date,
        'status': article_status.status
    }

    return jsonify({"article": article_data})


# Update article by id
@article.route('/api/v1/article/<articleId>', methods=['PUT'])
@auth.login_required
def edit_article(articleId):
    curr_user = session.query(User).filter_by(username=auth.username()).first()
    if curr_user.role_id == 1:
        # Get data from request body
        data = request.get_json()

        # Validate input data
        # try:
        #     ArticleSchema().load(data)
        # except ValidationError as err:
        #     return jsonify(err.messages), 400

        # Check if article exists
        db_article = session.query(Article).filter_by(article_id=articleId).first()
        if not db_article:
            return Response(status=404, response='An article with provided ID was not found.')

        # Check if user has permission to edit article
        db_user = session.query(User).filter_by(user_id=db_article.user_id).first()
        if db_user.username != auth.username():
            return Response(status=406, response='You can edit only your article')

        # Check if article with such title already exists
        if 'title' in data.keys():
            exists = session.query(Article.article_id).filter_by(title=data['title']).first()
            if exists and (exists.article_id != int(articleId)):
                return Response(status=400, response='Article with such title already exists.')
            db_article.title = data['title']
        # Change article data
        if 'text' in data.keys():
            db_article.text = data['text']
        if 'moderator_id' in data.keys():
            db_article.moderator_id = data['moderator_id']
        db_article.status_id = 1

        # Save changes
        session.commit()

        # Return new article data
        article_data = {
            'article_id': db_article.article_id,
            'title': db_article.title,
            'text': db_article.text,
            'user_id': db_article.user_id,
            'moderator_id': db_article.moderator_id,
            'date': db_article.date,
            'status_id': db_article.status_id
        }
        return jsonify({"article": article_data})
    elif curr_user.role_id == 2:
        # Get data from request body
        data = request.get_json()

        # Check if article exists
        db_article = session.query(Article).filter_by(article_id=articleId).first()
        if not db_article:
            return Response(status=404, response='An article with provided ID was not found.')

        # Check if status exists
        db_status = session.query(Status).filter_by(status=data['status']).first()
        if not db_status:
            return Response(status=404, response='Could not perform given operation on this article.')

        # Check if moderator has permission to approve article
        db_moderator = session.query(User).filter_by(user_id=db_article.moderator_id).first()
        if db_moderator.username != auth.username():
            return Response(status=406, response='You do not have access to approve this article')

        db_article.status_id = db_status.status_id

        # Save changes
        session.commit()

        # Return new article data
        article_data = {
            'article_id': db_article.article_id,
            'title': db_article.title,
            'text': db_article.text,
            'user_id': db_article.user_id,
            'moderator_id': db_article.moderator_id,
            'date': db_article.date,
            'status_id': db_article.status_id
        }
        return jsonify({"article": article_data})


# Approve article by id
# @article.route('/api/v1/approve/article/<articleId>', methods=['PUT'])
# @auth.login_required
# def approve_article(articleId):
#     # Check if article exists
#     db_article = session.query(Article).filter_by(article_id=articleId).first()
#     if not db_article:
#         return Response(status=404, response='An article with provided ID was not found.')
#
#     # Check if moderator has permission to approve article
#     db_moderator = session.query(User).filter_by(user_id=db_article.moderator_id).first()
#     if db_moderator.username != auth.username():
#         return Response(status=406, response='You do not have access to approve this article')
#
#     db_article.status_id = 2
#
#     # Save changes
#     session.commit()
#
#     # Return new article data
#     article_data = {
#         'article_id': db_article.article_id,
#         'title': db_article.title,
#         'text': db_article.text,
#         'user_id': db_article.user_id,
#         'moderator_id': db_article.moderator_id,
#         'date': db_article.date,
#         'status_id': db_article.status_id
#     }
#     return jsonify({"article": article_data})


# Delete article by id
@article.route('/api/v1/article/<articleId>', methods=['DELETE'])
@auth.login_required
def delete_article(articleId):
    # Check if supplied userId correct
    if int(articleId) < 1:
        return Response(status=400, response='Invalid articleId supplied')

    # Check if user exists
    db_article = session.query(Article).filter_by(article_id=articleId).first()
    if not db_article:
        return Response(status=404, response='A article with provided ID was not found.')

    db_user = session.query(User).filter_by(user_id=db_article.user_id).first()
    if db_user.username != auth.username():
        return Response(status=406, response='You can delete only your article')

    # Delete article
    session.delete(db_article)
    session.commit()
    return Response(status=200, response='Article was deleted.')

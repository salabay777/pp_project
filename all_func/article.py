from flask import Blueprint, Response, request, jsonify
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from all_func.dbmodel import Article, Session, User
from all_func.validation_schemas import ArticleSchema

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
    exists = session.query(Article.article_id).filter_by(name=data['name']).first()
    if exists:
        return Response(status=404, response='article with such number already exists.')

    # Create new article
    new_article = Article(article_id= data["article_id"],name=data['name'], body=data['body'], version=data['version'])

    # Add new article to db
    session.add(new_article)
    session.commit()

    return Response(status=200, response='New article was successfully created!')

# Get article by id
@article.route('/api/v1/article/<articleId>', methods=['GET'])
def get_article(articleId):
    # Check if supplied userId correct
    if int(articleId)<1:
        return Response(status=400, response='Invalid articleId supplied')
    # Check if user exists
    db_user = session.query(Article).filter_by(article_id=articleId).first()
    if not db_user:
        return Response(status=404, response='A article with provided ID was not found.')

    # Return user data
    user_data = {'article_id': db_user.article_id, 'name': db_user.name, 'body': db_user.body, 'version': db_user.version}
    return jsonify(user_data), 200


# Delete article by id
@article.route('/api/v1/article/<articleId>', methods=['DELETE'])
@auth.login_required
def delete_article(articleId):
    # Check if supplied userId correct
    if int(articleId)<1:
        return Response(status=400, response='Invalid articleId supplied')

    # Check if user exists
    db_user = session.query(Article).filter_by(article_id=articleId).first()
    if not db_user:
        return Response(status=404, response='A article with provided ID was not found.')

    # Delete user
    session.delete(db_user)
    session.commit()
    return Response(status=200, response='Article was deleted.')
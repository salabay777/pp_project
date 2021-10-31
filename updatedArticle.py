from flask import Blueprint, Response, request, jsonify
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from dbmodel import Moderator, UpdatedArticle, Session, User
from validation_schemas import UpdatedArticleSchema

updatedArticle = Blueprint('updatedArticle', __name__)
bcrypt = Bcrypt()

session = Session()

@updatedArticle.route('/api/v1/updateArticle', methods=['POST'])
def create_updatedArticle():
    # Get data from request body
    data = request.get_json()

    # Validate input data
    try:
        UpdatedArticleSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Check if supplied ArticleId correct
    db_user = session.query(UpdatedArticle).filter_by(article_id=data['article_id']).first()
    if not db_user:
        return Response(status=404, response='A article_id with provided not ok.')
    # Create new article
    new_updatedArticle = UpdatedArticle(article_id=data['article_id'], user_id=data['user_id'], moderator_id=data['moderator_id'], state_id=data['state_id'], article_body=data['article_body'], date=data['date'], status="awaits_resolution")

    # Add new article to db
    session.add(new_updatedArticle)
    session.commit()

    return Response(response='New updatedArticle was successfully created!')

# Get article by id
@updatedArticle.route('/api/v1/updateArticle/<ArticleId>', methods=['GET'])
def get_updatedArticle(ArticleId):
    # Check if supplied ArticleId correct
    if int(ArticleId)<1:
        return Response(status=400, response='Invalid ArticleId supplied')
    # Check if aricle's versions exists
    db_all = session.query(UpdatedArticle).filter_by(article_id=ArticleId).all()
    if not db_all:
        return Response(status=404, response='A articles versions with provided ID was not found')
    # Return user data
    updatedArticle_data={}
    i=0
    for db_user in db_all:
        updatedArticle_data[i] = {'updated_article_id': db_user.updated_article_id, 'article_id': db_user.article_id, 'user_id': db_user.user_id, 'moderator_id': db_user.moderator_id, 'state_id': db_user.state_id, 'article_body': db_user.article_body, 'date': db_user.date, 'status': db_user.status}
        i+=1
    return jsonify({"updatedArticle": updatedArticle_data})


# Delete article by id
@updatedArticle.route('/api/v1/updateArticle', methods=['PUT'])
def put_article():
    data = request.get_json()
    # Check if supplied userId correct
    if data['ArticleId']<1:
        return Response(status=404, response='Invalid ArticleId supplied')

    # Check if user exists
    db_user = session.query(Moderator).filter_by(moderatorkey=data['ModeratorKey']).first()
    if not db_user:
        return Response(status=400, response='A bad moderator key supplied')
    
    db_user2 = session.query(UpdatedArticle).filter_by(date=data['Date']).first()
    if not db_user2:
        return Response(status=402, response='A bad date was supplied')
    
    db_user2.status = "accepted"
    session.commit()

    return Response(status=200, response='Article was asccepted successfully')
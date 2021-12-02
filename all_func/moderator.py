from flask import Blueprint, Response, request, jsonify
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from  all_func.dbmodel import User, Moderator, Session
from all_func.validation_schemas import UserSchema, ModeratorSchema

moderator = Blueprint('moderator', __name__)
bcrypt = Bcrypt()

session = Session()
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    try:
        user = session.query(Moderator).filter_by(moderatorname=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return username
    except:
        return None

@moderator.route('/api/v1/moderator', methods=['POST'])
@auth.login_required
def registerModerator():
    # Get data from request body
    data = request.get_json()

    # Validate input data
    try:
        ModeratorSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Check if user already exists
    exists = session.query(Moderator.moderator_id).filter_by(moderatorname=data['moderatorname']).first()
    if exists:
        return Response(status=404, response='Moderator with such moderatorname already exists.')

    # Hash user's password
    hashed_password = bcrypt.generate_password_hash(data['password'])
    # Create new user
    new_moderator = Moderator(moderator_id = data['moderator_id'], moderatorname=data['moderatorname'], firstname=data['firstname'], lastname=data['lastname'], email=data['email'], password=hashed_password, moderatorkey=data['moderatorkey'])

    # Add new user to db
    session.add(new_moderator)
    session.commit()

    return Response(status=200, response='New moderator was successfully created!')
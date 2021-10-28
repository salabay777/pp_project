from flask import Blueprint, Response, request, jsonify
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from dbmodel import User, Moderator, Session
from validation_schemas import UserSchema, ModeratorSchema

moderator = Blueprint('moderator', __name__)
bcrypt = Bcrypt()

session = Session()

@moderator.route('/api/v1/moderator', methods=['POST'])
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
    new_moderator = Moderator(moderatorname=data['moderatorname'], firstname=data['firstname'], lastname=data['lastname'], email=data['email'], password=hashed_password, moderatorkey=data['moderatorkey'])

    # Add new user to db
    session.add(new_moderator)
    session.commit()

    return Response(status=200, response='New moderator was successfully created!')
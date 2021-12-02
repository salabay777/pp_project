from flask import Blueprint, Response, request, jsonify
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from all_func.dbmodel import User, Session
from all_func.validation_schemas import UserSchema

user = Blueprint('user', __name__)
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


# Register new user
@user.route('/api/v1/user', methods=['POST'])
def registerUser():
    # Get data from request body
    data = request.get_json()

    # Validate input data
    try:
        UserSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Check if user already exists
    exists = session.query(User.user_id).filter_by(username=data['username']).first()
    if exists:
        return Response(status=404, response='User with such username already exists.')

    # Hash user's password
    hashed_password = bcrypt.generate_password_hash(data['password'])
    # Create new user
    new_user = User(username=data['username'], firstname=data['firstname'], lastname=data['lastname'],
                    email=data['email'], password=hashed_password)

    # Add new user to db
    session.add(new_user)
    session.commit()

    return Response(status=200, response='New user was successfully created!')


# Get user by id
@user.route('/api/v1/user/<userId>', methods=['GET'])
@auth.login_required
def get_user(userId):

    # Check if supplied userId correct
    if int(userId) < 1:
        return Response(status=400, response='Invalid userID supplied')
    # Check if user exists
    db_user = session.query(User).filter_by(user_id=userId).first()
    if not db_user:
        return Response(status=404, response='A user with provided ID was not found.')

    # Return user data
    user_data = {'user_id': db_user.user_id, 'username': db_user.username, 'firstname': db_user.firstname,
                 'lastname': db_user.lastname, 'email': db_user.email, 'password': db_user.password}
    return jsonify( user_data), 200


# Delete user by id
@user.route('/api/v1/user/<userId>', methods=['DELETE'])
@auth.login_required
def delete_user(userId):
    # if auth.username() != session.query(User).filter_by(user_id=userId).first().username:
    #     return Response(status=500, response='Access denied')

    # Check if supplied userId correct
    if int(userId) < 1:
        return Response(status=400, response='Invalid username supplied')

    # Check if user exists
    db_user = session.query(User).filter_by(user_id=userId).first()
    if not db_user:
        return Response(status=404, response='A user with provided ID was not found.')

    # Delete user
    session.delete(db_user)
    session.commit()
    return Response(status=200, response='User was deleted.')

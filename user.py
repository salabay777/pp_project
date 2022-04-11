from flask import Blueprint, Response, request, jsonify
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from dbmodel import User, Role, Session
from validation_schemas import UserSchema

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
    exists2 = session.query(User.user_id).filter_by(email=data['email']).first()
    if exists or exists2:
        return Response(status=409, response='User with such username or email already exists.')

    # Check if role exists
    roleExists = session.query(Role).filter_by(role=data["role"]).first()
    if not roleExists:
        return Response(status=404, response='Role with such name does not exist.')

    # Hash user's password
    hashed_password = bcrypt.generate_password_hash(data['password'])
    # Create new user
    new_user = User(username=data['username'], first_name=data['first_name'], last_name=data['last_name'],
                    email=data['email'], password=hashed_password, role_id=roleExists.role_id)

    # Add new user to db
    session.add(new_user)
    session.commit()

    return Response(status=200, response='New user was successfully created!')


@user.route('/api/v1/user/login', methods=['POST'])
def login_user():
    # Get data from request body
    data = request.get_json()

    # Check if user exists
    db_user = session.query(User).filter_by(username=data["username"]).first()
    if not db_user:
        return Response(status=404, response='User with such username does not exist.')

    username = verify_password(data["username"], data["password"])

    if username:
        return Response(status=200, response='Successful login!')
    else:
        return Response(status=403, response='Password is incorrect!')


# Get user by username
@user.route('/api/v1/user/<username>', methods=['GET'])
def get_user(username):
    # if auth.username() != session.query(User).filter_by(username=username).first().username:
    #     return Response(status=406, response='Access denied')

    # Check if user exists
    db_user = session.query(User).filter_by(username=username).first()
    if not db_user:
        return Response(status=404, response='A user with provided username was not found.')

    role = session.query(Role).filter_by(role_id=db_user.role_id).first().role

    # Return user data
    user_data = {'username': db_user.username, 'first_name': db_user.first_name,
                 'last_name': db_user.last_name, 'email': db_user.email, 'role': role}
    return jsonify({"user": user_data})


# Update user by username
@user.route('/api/v1/user/<username>', methods=['PUT'])
@auth.login_required
def update_user(username):
    # Get data from request body
    data = request.get_json()

    # Check if user exists
    db_user = session.query(User).filter_by(username=username).first()
    if not db_user:
        return Response(status=404, response='A user with provided ID was not found.')

    if db_user.username != auth.username():
        return Response(status=404, response='You can update only your information')

    # Check if username is not taken if user tries to change it
    if 'username' in data.keys() and db_user.username != data['username']:
        exists = session.query(User.user_id).filter_by(username=data['username']).first()
        if exists:
            return Response(status=400, response='User with such username already exists.')
        db_user.username = data['username']
    # Check if role exists
    roleExists = session.query(Role).filter_by(role=data["role"]).first()
    if not roleExists:
        return Response(status=404, response='Role with such name does not exist.')
    # Change user data
    if 'first_name' in data.keys():
        db_user.first_name = data['first_name']
    if "last_name" in data.keys():
        db_user.last_name = data['last_name']
    if 'password' in data.keys():
        hashed_password = bcrypt.generate_password_hash(data['password'])
        db_user.password = hashed_password
    if "email" in data.keys() and db_user.email != data['email']:
        exists = session.query(User.user_id).filter_by(email=data['email']).first()
        if exists:
            return Response(status=400, response='User with such email already exists.')
        db_user.email = data['email']
    if "role" in data.keys():
        db_user.role_id = roleExists.role_id

    # Save changes
    session.commit()

    role = session.query(Role).filter_by(role_id=db_user.role_id).first().role

    # Return new user data
    user_data = {'id': db_user.user_id, 'first_name': db_user.first_name, 'last_name': db_user.last_name,
                 'username': db_user.username, "email": db_user.email, "role": role}
    return jsonify({"user": user_data})


# Delete user by username
@user.route('/api/v1/user/<username>', methods=['DELETE'])
@auth.login_required
def delete_user(username):
    if auth.username() != session.query(User).filter_by(username=username).first().username:
        return Response(status=406, response='Access denied')

    # Check if user exists
    db_user = session.query(User).filter_by(username=username).first()
    if not db_user:
        return Response(status=404, response='A user with provided ID was not found.')

    # Delete user
    session.delete(db_user)
    session.commit()
    return Response(response='User was deleted.')


@user.route('/api/v1/moderators', methods=['GET'])
@auth.login_required
def get_all_moderators():
    moderator_role_id = session.query(Role).filter_by(role="moderator").first().role_id
    if not moderator_role_id:
        return Response(status=404, response="There are no moderators available")

    moderators = session.query(User).filter_by(role_id=moderator_role_id)
    if not moderators:
        return Response(status=404, response="There are no moderators available.")

    moderators_data = []
    for m in moderators:
        moderators_data.append({'username': m.username, 'email': m.email, 'first_name': m.first_name, 'last_name': m.last_name})

    return jsonify({"moderators": moderators_data})

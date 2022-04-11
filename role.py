from os import stat_result
from flask import Blueprint, Response, request, jsonify
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from dbmodel import Role, Session, User
from validation_schemas import RoleSchema

role = Blueprint('role', __name__)
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


@role.route('/api/v1/role', methods=['POST'])
@auth.login_required
def create_role():
    # Get data from request body
    data = request.get_json()

    # Validate input data
    try:
        RoleSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Check if role already exists
    exists = session.query(Role.role_id).filter_by(role=data['role']).first()
    if exists:
        return Response(status=404, response='Role with such name already exists')

    # Create new role
    new_role = Role(role=data['role'])

    # Add new article to db
    session.add(new_role)
    session.commit()

    return Response(response='New role was successfully created!')


# Get role by id
@role.route('/api/v1/role/<roleId>', methods=['GET'])
@auth.login_required
def get_role(roleId):
    # Check if supplied userId correct
    if int(roleId) < 1:
        return Response(status=400, response='Invalid roleId supplied')
    # Check if role exists
    db_role = session.query(Role).filter_by(role_id=roleId).first()
    if not db_role:
        return Response(status=404, response='A role with provided ID was not found')

    # Return role data
    role_data = {'role_id': db_role.role_id, 'role': db_role.role}
    return jsonify({"role": role_data})


# Delete role by id
@role.route('/api/v1/role/<roleId>', methods=['DELETE'])
@auth.login_required
def delete_role(roleId):
    # Check if supplied roleId correct
    if int(roleId) < 1:
        return Response(status=400, response='Invalid roleId supplied')

    # Check if role exists
    db_role = session.query(Role).filter_by(role_id=roleId).first()
    if not db_role:
        return Response(status=404, response='A role with provided ID was not found')

    # Delete role
    session.delete(db_role)
    session.commit()
    return Response(response='Role was deleted')

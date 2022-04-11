from os import stat_result
from flask import Blueprint, Response, request, jsonify
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from dbmodel import Status, Session, User
from validation_schemas import StatusSchema

status = Blueprint('status', __name__)
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


@status.route('/api/v1/status', methods=['POST'])
@auth.login_required
def create_status():
    # Get data from request body
    data = request.get_json()

    # Validate input data
    try:
        StatusSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Check if status already exists
    exists = session.query(Status.status_id).filter_by(status=data['status']).first()
    if exists:
        return Response(status=404, response='Status with such name already exists')

    # Create new status
    new_status = Status(status=data['status'])

    # Add new status to db
    session.add(new_status)
    session.commit()

    return Response(response='New status was successfully created!')


# Get status by id
@status.route('/api/v1/status/<statusId>', methods=['GET'])
@auth.login_required
def get_status(statusId):
    # Check if supplied userId correct
    if int(statusId) < 1:
        return Response(status=400, response='Invalid statusId supplied')
    # Check if status exists
    db_status = session.query(Status).filter_by(status_id=statusId).first()
    if not db_status:
        return Response(status=404, response='A status with provided ID was not found')

    # Return user data
    status_data = {'status_id': db_status.status_id, 'status': db_status.status}
    return jsonify({"status": status_data})


# Delete status by id
@status.route('/api/v1/status/<statusId>', methods=['DELETE'])
@auth.login_required
def delete_status(statusId):
    # Check if supplied statusId correct
    if int(statusId) < 1:
        return Response(status=400, response='Invalid statusId supplied')

    # Check if status exists
    db_status = session.query(Status).filter_by(status_id=statusId).first()
    if not db_status:
        return Response(status=404, response='A status with provided ID was not found')

    # Delete status
    session.delete(db_status)
    session.commit()
    return Response(response='Status was deleted')

from os import stat_result
from flask import Blueprint, Response, request, jsonify
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from dbmodel import State, Session
from validation_schemas import StateSchema

state = Blueprint('state', __name__)
bcrypt = Bcrypt()

session = Session()

@state.route('/api/v1/state', methods=['POST'])
def create_state():
    # Get data from request body
    data = request.get_json()

    # Validate input data
    try:
        StateSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Check if article already exists
    exists = session.query(State.state_id).filter_by(name=data['name']).first()
    if exists:
        return Response(status=404, response='state with such name already exists')

    # Create new article
    new_state = State(name=data['name'])

    # Add new article to db
    session.add(new_state)
    session.commit()

    return Response(response='New state was successfully created!')

# Get article by id
@state.route('/api/v1/state/<stateId>', methods=['GET'])
def get_state(stateId):
    # Check if supplied userId correct
    if int(stateId)<1:
        return Response(status=400, response='Invalid stateId supplied')
    # Check if user exists
    db_user = session.query(State).filter_by(state_id=stateId).first()
    if not db_user:
        return Response(status=404, response='A state with provided ID was not found')

    # Return user data
    state_data = {'state_id': db_user.state_id, 'name': db_user.name}
    return jsonify({"state": state_data})


# Delete article by id
@state.route('/api/v1/state/<stateId>', methods=['DELETE'])
def delete_state(stateId):
    # Check if supplied userId correct
    if int(stateId)<1:
        return Response(status=400, response='Invalid stateId supplied')

    # Check if user exists
    db_user = session.query(State).filter_by(state_id=stateId).first()
    if not db_user:
        return Response(status=404, response='A state with provided ID was not found')

    # Delete user
    session.delete(db_user)
    session.commit()
    return Response(response='state was deleted')
from marshmallow import Schema, fields
from marshmallow.validate import Length, Range


class UserSchema(Schema):
    username = fields.String(required=True, validate=Length(min=3))
    first_name = fields.String(required=True, validate=Length(min=3))
    last_name = fields.String(required=True, validate=Length(min=3))
    email = fields.Email(required=True, validate=Length(min=6))
    password = fields.String(required=True, validate=Length(min=6))
    role = fields.String(required=True, validate=Length(min=3))


class ArticleSchema(Schema):
    title = fields.String(required=True, validate=Length(min=3))
    text = fields.String(required=True, validate=Length(min=6))
    # user_id = fields.Integer(strict=True, required=True, validate=Range(min=0))
    moderator = fields.String(required=True, validate=Length(min=3))
    # date = fields.Date(required=True)
    # status_id = fields.Integer(strict=True, required=True, validate=Range(min=0))


class RoleSchema(Schema):
    role = fields.String(required=True, validate=Length(min=3))


class StatusSchema(Schema):
    status = fields.String(required=True, validate=Length(min=3))

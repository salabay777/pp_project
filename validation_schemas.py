from marshmallow import Schema, fields
from marshmallow.validate import Length, Range


class UserSchema(Schema):
    username = fields.String(required=True, validate=Length(min=3))
    firstname = fields.String(required=True, validate=Length(min=3))
    lastname = fields.String(required=True, validate=Length(min=3))
    email = fields.String(required=True, validate=Length(min=6))
    password = fields.String(required=True, validate=Length(min=6))


class ModeratorSchema(Schema):
    moderatorname = fields.String(required=True, validate=Length(min=3))
    firstname = fields.String(required=True, validate=Length(min=3))
    lastname = fields.String(required=True, validate=Length(min=3))
    email = fields.String(required=True, validate=Length(min=3))
    password = fields.String(required=True, validate=Length(min=6))
    moderatorkey = fields.String(required=True, validate=Length(min=6))


class ArticleSchema(Schema):
    name = fields.String(required=True, validate=Length(min=3))
    body = fields.String(required=True, validate=Length(min=6))
    version = fields.String(required=True, validate=Length(min=6))

class StateSchema(Schema):
    name = fields.String(required=True, validate=Length(min=3))

class UpdatedArticleSchema(Schema):
    # updated_article_id = fields.Integer(strict=True, required=True, validate=Range(min=0))
    article_id = fields.Integer(strict=True, required=True, validate=Range(min=0))
    user_id = fields.Integer(strict=True, required=True, validate=Range(min=0))
    moderator_id = fields.Integer(strict=True, required=True, validate=Range(min=0))
    state_id = fields.Integer(strict=True, required=True, validate=Range(min=0))
    article_body = fields.String(required=True, validate=Length(min=6))
    date = fields.Date(required=True)
    # status = fields.String(required=True)
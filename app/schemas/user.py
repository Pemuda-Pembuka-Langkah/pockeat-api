from marshmallow import Schema, fields, validate, post_load
from app.models.user import User

class UserSchema(Schema):
    """Schema for serializing and deserializing User objects."""
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @post_load
    def make_user(self, data, **kwargs):
        """Create a user instance from validated data."""
        return User(**data) 
from flask_restful import fields

controller_fields = {
    "name": fields.String,
    "size": fields.Integer,
    # "drive_dir": fields.String,
    # "base_length": fields.Integer
}

control_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "c_type": fields.Integer,
    "parent": fields.Integer,
    # "start": fields.Integer,
    "mime": fields.String,
    # "end": fields.Integer,
    "deleted": fields.Boolean
}
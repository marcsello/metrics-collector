#!/usr/bin/env python3
from marshmallow import Schema, fields
import marshmallow.validate


class FilesystemSchama(Schema):
    used_percent = fields.Float(validate=marshmallow.validate.Range(min=0, max=100), required=True)
    used_bytes = fields.Integer(validate=marshmallow.validate.Range(min=0), required=True)


class MemorySchema(Schema):
    used_percent = fields.Float(validate=marshmallow.validate.Range(min=0, max=100), required=True)
    used_bytes = fields.Integer(validate=marshmallow.validate.Range(min=0), required=True)


class RecordSchema(Schema):
    cpu = fields.List(fields.Float(validate=marshmallow.validate.Range(min=0, max=100)), validate=marshmallow.validate.Length(min=1, max=128), allow_none=True, required=False)  # percentages
    memory = fields.Nested(MemorySchema, required=False, allow_none=True, many=False)
    filesystem = fields.Dict(keys=fields.String(), values=fields.Nested(FilesystemSchama), allow_none=True, required=False)

    class Meta:
        pass

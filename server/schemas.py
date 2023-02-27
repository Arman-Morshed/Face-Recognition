from marshmallow import Schema, fields

class EmbeddingSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Str(required=True)
    name = fields.Str(required=True)
    model = fields.Str(required=True)
    embedding = fields.Str(required=True)
    precision = fields.Float(required=False)

class VerifySchema(Schema):
    id = fields.Int(required=False)
    name = fields.Str(required=False)


# class PlainUserInfoSchema(Schema):
#     id = fields.Str(dump_only=True)
#     name = fields.Str(required=True)
 
# class EmbeddingSchema(PlainEmbeddingSchema):
#     user_id = fields.Str(required=True)
#     user_info = fields.Nested(PlainUserInfoSchema(), dump_only=True)

# class UserInfoSchema(PlainUserInfoSchema):
#     embeddings = fields.Nested(PlainEmbeddingSchema(), dump_only=True) 
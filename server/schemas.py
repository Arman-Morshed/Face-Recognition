from marshmallow import Schema, fields

class EmbeddingSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    model = fields.Str(required=True)
    embedding = fields.Str(required=True)
    # precision = fields.Str(required=False)

class VerifySchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)


# class PlainUserInfoSchema(Schema):
#     id = fields.Str(dump_only=True)
#     name = fields.Str(required=True)
 
# class EmbeddingSchema(PlainEmbeddingSchema):
#     user_id = fields.Str(required=True)
#     user_info = fields.Nested(PlainUserInfoSchema(), dump_only=True)

# class UserInfoSchema(PlainUserInfoSchema):
#     embeddings = fields.Nested(PlainEmbeddingSchema(), dump_only=True) 
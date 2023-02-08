from flask import Flask
from server.db import db
from flask_smorest import Api
from server.resources.info import blp as UserInfoBluePreint
import os

def create_app(db_url=None):
	app = Flask(__name__)

	app.config["PROPAGATE_EXCEPTIONS"] = True
	app.config["API_TITLE"] = "Stores REST API"
	app.config["API_VERSION"] = "v1"
	app.config["OPENAPI_VERSION"] = "3.0.3"
	app.config["OPENAPI_URI_PREFIX"] = "/"
	app.config["OPENAI_SWAGGER_UI_PATH"] = "/swagger-ui"
	app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
	app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
	db.init_app(app)

	api = Api(app)

	@app.before_first_request
	def create_tables():
		db.create_all()

	api.register_blueprint(UserInfoBluePreint)
	return app
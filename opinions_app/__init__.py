from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from settings import Config


app = Flask(__name__, static_folder='static_dir')
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from . import api_views, cli_commands, error_handlers, views

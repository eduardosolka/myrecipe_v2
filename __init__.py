from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from flask_pagedown import PageDown

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:***@myrecipe.c80e6zvozgrv.us-east-1.rds.amazonaws.com/myrecipe_producao'
app.config['SECRET_KEY'] = 'secret'

login_manager = LoginManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app,db)
pagedown = PageDown(app)
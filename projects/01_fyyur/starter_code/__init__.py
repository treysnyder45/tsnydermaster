from flask import Flask
from flask_moment import Moment
import os
from starter_code.config import *

basedir = os.getcwd()

app = Flask(__name__)
moment = Moment(app)
app.debug = config.DEBUG
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = config.SECRET_KEY

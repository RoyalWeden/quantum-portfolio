from flask import Flask
from dotenv import dotenv_values
import os

app = Flask(__name__, static_folder='static')
config = dict(os.environ)

app.secret_key = config['SECRET_KEY']

from app import routes
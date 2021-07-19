from flask import Flask
from dotenv import dotenv_values
import os

app = Flask(__name__)
config = dict(os.environ)

from app import routes
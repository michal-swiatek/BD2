from flask import Flask

app = Flask(__name__)

app.config['SECRET_KEY'] = '32760782cd6db55d4feb2d5418b9d288'

from application import routes

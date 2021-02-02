from flask import Flask
import mysql.connector as connector
from .dashboards.dashboard import create_app

app = Flask(__name__)

app.config['SECRET_KEY'] = '32760782cd6db55d4feb2d5418b9d288'
passwd = "1234321"
db = connector.connect(host="localhost", user="root", password=passwd)
cursor = db.cursor(buffered=True)

# db = connector.connect(host="localhost", user="bd2app", password="passwd", database="bd2")
# cursor = db.cursor(buffered=True)

dash_app = create_app(app, cursor)

from application import routes
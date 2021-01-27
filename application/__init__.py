from flask import Flask
import mysql.connector as connector

app = Flask(__name__)

app.config['SECRET_KEY'] = '32760782cd6db55d4feb2d5418b9d288'

db = connector.connect(host="localhost", user="root", password="")

from application import routes

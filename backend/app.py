import os
import cx_Oracle
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  #for React frontend

#DB config from env vars stored on OS.
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "1521")  
DB_SERVICE = os.getenv("DB_SERVICE")


dsn = cx_Oracle.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE)

connection = cx_Oracle.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn)

cursor = connection.cursor()


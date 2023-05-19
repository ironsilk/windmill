from flask_executor import Executor

from dotenv import load_dotenv
import os
import json
from itertools import groupby

from resources.data import fetch_data
from resources.models import db
from flask import Flask, request, jsonify
from flask_cors import CORS
from loguru import logger
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()


POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.environ.get('DB_NAME')
DB_CONNECTION_NAME = os.environ.get('DB_CONNECTION_NAME')
DB_IP = os.environ.get('DB_IP')
DB_PORT = os.environ.get('DB_PORT')

db_uri = f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_IP}:{DB_PORT}/{DB_NAME}'


app = Flask(__name__)
CORS(app)
executor = Executor(app)
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config['EXECUTOR_TYPE'] = 'thread'
app.config['EXECUTOR_PROPAGATE_EXCEPTIONS'] = True
db.init_app(app)
with app.app_context():
    # db.drop_all()
    db.create_all()
    scheduler = BackgroundScheduler()
    scheduler.start()

scheduler.add_job(fetch_data, 'interval', minutes=1)


@app.route('/', methods=['GET'])
def home():
    return "ok"


@app.route('/fetch', methods=['GET'])
def trigger_data_fetch():
    logger.info(f"Running user-triggerd data fetching...")
    executor.submit(fetch_data)
    return "Data fetching triggered"


if __name__ == '__main__':
    with app.app_context():
        fetch_data()











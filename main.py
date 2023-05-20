import os

from dotenv import load_dotenv
from flask import Flask
from flask import jsonify
from flask_cors import CORS
from flask_executor import Executor
from loguru import logger

from resources.data import fetch_data
from resources.db import db_get_anomalies
from resources.models import db

load_dotenv()


POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.environ.get('DB_NAME')
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


@app.route('/', methods=['GET'])
def home():
    return "ok"


@app.route('/fetch', methods=['GET'])
def trigger_data_fetch():
    logger.info(f"Running user-triggerd data fetching...")
    executor.submit(fetch_data)
    return "Data fetching triggered"


@app.route('/anomalies', methods=['GET'])
def get_anomalies():
    anomalies = db_get_anomalies()
    return jsonify(anomalies)


if __name__ == '__main__':
    with app.app_context():
        fetch_data()
    app.run(host='0.0.0.0', port=5001)












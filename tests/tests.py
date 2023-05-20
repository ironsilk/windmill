import os

import pandas as pd
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_testing import TestCase

from resources.data import preprocess_data
from resources.models import db


class MyTest(TestCase):

    TESTING = True

    def create_app(self):
        load_dotenv()

        POSTGRES_USER = os.getenv("POSTGRES_USER")
        POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
        DB_NAME = os.environ.get('DB_NAME')
        DB_IP = os.environ.get('DB_IP')
        DB_PORT = os.environ.get('DB_PORT')

        db_uri = f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_IP}:{DB_PORT}/{DB_NAME}'

        app = Flask(__name__)
        CORS(app)
        app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
        app.config['EXECUTOR_TYPE'] = 'thread'
        app.config['EXECUTOR_PROPAGATE_EXCEPTIONS'] = True
        db.init_app(app)
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):

        db.session.remove()
        db.drop_all()

    def test_preprocess_data(self):
        # Create sample DataFrame with test data
        data = {
            "timestamp": ["2023-01-01 00:00:00", "2023-01-01 01:00:00", "2023-01-01 02:00:00"],
            "wind_speed": [20, 30, 10],
            "wind_direction": [180, 270, 90],
            "power_output": [100, 200, 300]
        }
        df = pd.DataFrame(data)

        # Preprocess the data
        preprocessed_df = preprocess_data(df).reset_index(drop=True)

        # Assert the expected output after preprocessing
        expected_output = pd.DataFrame({
            "timestamp": pd.to_datetime(["2023-01-01 00:00:00", "2023-01-01 02:00:00"]),
            "wind_speed": [20, 10],
            "wind_direction": [180, 90],
            "power_output": [100, 300]
        })
        pd.testing.assert_frame_equal(preprocessed_df, expected_output)

    def test_compute_batch_stats(self):
        # TODO: Implement this test case
        pass

    def test_compute_anomalies(self):
        # TODO: Implement this test case
        pass

    def test_compute_data(self):
        # TODO: Implement this test case
        pass

    def test_compute_data_and_anomalies(self):
        # TODO: Implement this test case
        pass

    def test_fetch_data(self):
        # TODO: Implement this test case
        pass
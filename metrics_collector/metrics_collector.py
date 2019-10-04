#!/usr/bin/env python3
from flask import Flask
from flask_jwt_simple import JWTManager
import os

from utils import register_all_error_handlers
from views import RecordView

app = Flask(__name__)

app.config['JWT_PUBLIC_KEY'] = open(os.environ['MC_JWT_PUBLIC_KEY'], 'r').read()
app.config['JWT_ALGORITHM'] = 'RS512'

app.config['INFLUXDB_HOST'] = os.environ['MC_INFLUXDB_HOST']
app.config['INFLUXDB_USER'] = os.environ['MC_INFLUXDB_USER']
app.config['INFLUXDB_PASSWORD'] = os.environ['MC_INFLUXDB_PASSWORD']
app.config['INFLUXDB_DATABASE'] = os.environ['MC_INFLUXDB_DATABASE']


jwt = JWTManager(app)
RecordView.influx_db.init_app(app)  # This is very fuking ugly...
register_all_error_handlers(app)


# register views
for view in [RecordView]:
    view.register(app, trailing_slash=False)


if __name__ == "__main__":
    app.run(debug=True)

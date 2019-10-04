#!/usr/bin/env python3
from flask_classful import FlaskView
from flask import request, abort, jsonify
from utils import json_required
from flask_jwt_simple import jwt_required, get_jwt_identity
from flask_influxdb import InfluxDB
from tzlocal import get_localzone
from datetime import datetime
from marshmallow.exceptions import ValidationError

from schemas import RecordSchema


class RecordView(FlaskView):

    influx_db = InfluxDB()
    record_schema = RecordSchema()

    @staticmethod
    def _convert_cpu_to_influx_datapoints(hostname: str, timestamp: str, cpu_percentages: list) -> list:

        datapoints = []

        for i in range(len(cpu_percentages)):
            datapoints.append({
                "measurement": "cpu_utilization",
                "time": timestamp,
                "tags": {
                    "host": hostname,
                    "core": i
                },
                "fields": {
                    "utilized_percent": cpu_percentages[i]
                }
            })

        return datapoints

    @staticmethod
    def _convert_memory_to_influx_datapoints(hostname: str, timestamp: str, memory_usage: dict) -> dict:
        return {
            "measurement": "memory_utilization",
            "time": timestamp,
            "tags": {
                "host": hostname
            },
            "fields": {
                "used_bytes": memory_usage['used_bytes'],
                "used_percent": memory_usage['used_percent']
            }
        }

    @staticmethod
    def _convert_filesystem_to_influx_datapoints(hostname: str, timestamp: str, filesystems: dict) -> list:

        datapoints = []

        for filesystem, utilization in filesystems.items():
            datapoints.append({
                "measurement": "filesystem_utilization",
                "time": timestamp,
                "tags": {
                    "host": hostname,
                    "filesystem": filesystem
                },
                "fields": {
                    "used_bytes": utilization['used_bytes'],
                    "used_percent": utilization['used_percent']
                }
            })

        return datapoints

    @jwt_required
    @json_required
    def post(self):

        hostname = get_jwt_identity()
        timestamp = datetime.now(get_localzone()).isoformat()

        try:
            record = self.record_schema.load(request.get_json())
        except (ValidationError) as e:
            abort(422, str(e))

        datapoints = []

        if 'cpu' in record.keys():
            datapoints.extend(self._convert_cpu_to_influx_datapoints(hostname, timestamp, record['cpu']))

        if 'memory' in record.keys():
            datapoints.append(self._convert_memory_to_influx_datapoints(hostname, timestamp, record['memory']))

        if 'filesystem' in record.keys():
            datapoints.extend(self._convert_filesystem_to_influx_datapoints(hostname, timestamp, record['filesystem']))

        conn = self.influx_db.connection
        conn.write_points(datapoints)

        return jsonify(record), 201

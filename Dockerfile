FROM python:3

ADD . /metrics_collector
WORKDIR /metrics_collector/metrics_collector

RUN pip3 install -r  ../requirements.txt && pip3 install gunicorn

CMD ["gunicorn", "-b", "0.0.0.0:8000", "metrics_collector:app"]

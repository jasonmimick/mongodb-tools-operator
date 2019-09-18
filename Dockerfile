FROM python:3.7-alpine as base-env
COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

FROM base-env as mongodb-kubemgr
COPY operator.py /operator.py
COPY simple-operator.py /simple-operator.py
CMD kopf run /simple-operator.py

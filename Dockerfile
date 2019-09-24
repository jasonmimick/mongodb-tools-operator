FROM python:3.7-alpine as base-layer
COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

FROM base-layer as kubectl-layer
RUN apk --no-cache add curl
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl 
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl

FROM kubectl-layer as mongodb-kubemgr
COPY operator.py /operator.py
COPY simple-operator.py /simple-operator.py
COPY pkg /pkg
COPY crds /crds
COPY templates /templates
CMD kopf run --standalone --namespace ${NAMESPACE} /simple-operator.py

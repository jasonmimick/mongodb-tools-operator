The MongoDB Tools Kubernetes Operator
---

Manage MongoDB Tools in your Kubernete clusters.
Built for the MongoDB Engineering Offsite Hackathon 2019.

Limitations: Only supports the MongoDB Charts tool.

# Installation

Setup and install the [MongoDB Kubernetes Operator](https://github.com/mongodb/mongodb-enterprise-kubernetes).

Then,

```bash
kubectl apply -f crds/mongodb-charts.crd.yaml
kubectl apply -f mongodb-tools-operator.yaml
```

# Get started

To launch a new MongoDB Charts instance, you need to first
create a Secret to hold the first admin's signon credentials.
Then, you create an instance of the `MongoDBCharts` custom
resource definition.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mongodb-charts-admin
type: Opaque
stringData:
  findName: admin
  lastName: charts
  email: admin@example.com
  password: password
---
apiVersion: mongodb.com/v1alpha1
kind: MongoDBCharts
metadata:
  name: mongodb-charts
spec:
  useradmin: mongodb-charts-admin
  version: "19.09"
```  

Create a similar file and apply it to your cluster.

```bash
kubectl apply -f my-mongodb-charts.yaml
```

# Contributing

# Tool integration

Each tool should define a crd and template and place these 
in the appropriate location.

Naming convention
crds/<tool-name>.crd.yaml
templates/<tool-name>.template.yaml

Optional,
pkg/tools/<tool-name>.operator.py  # runtime code




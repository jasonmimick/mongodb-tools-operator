The MongoDB Tools Kubernetes Operator
---

Manage MongoDB Tools in your Kubernete clusters.
Built for the MongoDB Engineering Offsite Hackathon 2019.

Limitations: Only supports the MongoDB Charts tool.

# Installation

```bash
kubectl apply -f crds/mongodb-charts.crd.yaml
kubectl apply -f mongodb-tools-operator.yaml
```

# Tool integration

Each tool should define a crd and template and place these 
in the appropriate location.

Naming convention
crds/<tool-name>.crd.yaml
templates/<tool-name>.template.yaml

Optional,
pkg/tools/<tool-name>.operator.py  # runtime code




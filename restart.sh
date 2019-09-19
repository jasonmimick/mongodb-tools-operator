kubectl delete -f samples/mongodb-charts-sample.yaml
kubectl delete -f mongodb-tools-operator.yaml
kubectl delete -f crds/mongodbcharts.crd.yaml
kubectl delete service mongodb-charts-mongodb-charts-svc
kubectl delete -f samples/opsmanager.configmap.yaml
kubectl delete -f templates/mongodbcharts.metadb.template.yaml.DEMO
kubectl delete deployment.apps/mongodb-charts 

docker build -t jmimick/mongodb-tools-operator . && docker push jmimick/mongodb-tools-operator

kubectl apply -f samples/opsmanager.configmap.yaml
kubectl apply -f templates/mongodbcharts.metadb.template.yaml.DEMO
kubectl apply -f crds/mongodbcharts.crd.yaml
kubectl apply -f mongodb-tools-operator.yaml
kubectl apply -f samples/mongodb-charts-sample.yaml


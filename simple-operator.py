import kopf

print('MongoDB Tools Kubernetes Operator - is online')
@kopf.on.create('mongodb.com', 'v1alpha1', 'mongodb-charts')
def create_fn(spec, **kwargs):
    # Get info from Database object
    # Update status
    msg = f"{spec} created by MongoDB Tools Kubernetes Manager"
    print(msg)
    return {'message': msg}

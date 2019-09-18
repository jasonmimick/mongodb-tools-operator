import kopf
import logging
import sys
from pkg.kube_apply import fromYaml 
from jinja2 import Template
from pkg.kubehelper import KubeHelper
from pkg.operatorhelper import OperatorHelper

logger = logging.getLogger('mongodb-tools-operator')
log_level = "INFO"
logger.setLevel(log_level)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(log_level)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
welcome='MongoDB Tools Kubernetes Operator - is online'
#kopf.info({}, reason='Startup', message=welcome)
print(welcome)

OperatorHelper.test('hi')

@kopf.on.create('mongodb.com', 'v1alpha1', 'mongodbcharts')
def create_fn(spec, **kwargs):
    logger.info(f'keys:{kwargs.keys()}')
    template = OperatorHelper.load_template('mongodbcharts') 
    template_instance = template['mongodbcharts']['template']
    #logger.info(f"kwargs:{kwargs['body']}")
    body = kwargs['body']
    rendered_template = OperatorHelper.render_template(template_instance,spec,body) 
    logger.info('calling fromYaml!!!!')
    res = fromYaml( rendered_template ) 
    logger.info(f'res:{res}')
    msg = f"{spec} created by MongoDB Tools Kubernetes Manager"
    logger.info(msg)
    return {'message': msg}

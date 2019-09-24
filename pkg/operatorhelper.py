import logging
from jinja2 import Template
import sys

logger = logging.getLogger('mongodb-tools-operator')
log_level = "INFO"
logger.setLevel(log_level)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(log_level)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class OperatorHelper:

  @staticmethod
  def test(msg):
    print(f'OperatorHelper test: {msg}')

  @staticmethod
  def load_chart(tool_id):
    # Load all templates in repo
    chart_instance = { 'template' : 'raw template data',
                          'rendered_template' : 'merged' }
    chart_dir = "templates"
    template_file = f'{template_dir}/{tool_id}.template.yaml'
    logger.debug(f'load_template template_file={template_dir}')
    with open(template_file, 'r') as t:
      template = t.read()
      logger.info("loaded template: %s" % template)
      template_instance[tool_id] = { 'template' : str(template), 
                                     'rendered_template' : None }

    return template_instance

  @staticmethod:
  def render_template(template_instance, spec, body):
    # merge params
    parameters = { **spec, **body }
    parameters['name'] = parameters['metadata']['name']
    parameters['namespace'] = parameters['metadata']['namespace']
    logger.info(f'render_template parameters:{parameters}')
    t = Template(template_instance)
    rendered_template = t.render(parameters)
    return rendered_template
  

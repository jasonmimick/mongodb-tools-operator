from kubernetes import client, config, utils
from kubernetes.client.rest import ApiException
import yaml
import os
import re
import abc
import logging
from typing import List
from pprint import pprint
import glob 
import sys
import urllib
from werkzeug.exceptions import BadRequest


logger = logging.getLogger('mongodb-tools-operator')
log_level = "INFO"
logger.setLevel(log_level)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(log_level)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class KubeHelper():

  @staticmethod
  def get_ns_kind_name(yaml_filepath_or_contents,verbose=False):
    y = yaml.load(yaml_filepath_or_contents)
    # TODO: add error handling to make sure keys exist
    x = { 'kind' : y['kind'], 'name' : y['name'] }
    if "namespace" in y["metadata"]:
      x['namespace'] = y["metadata"]["namespace"]
    else:
      x['namespace'] = "default"
    return x

  @staticmethod
  def get_documents(yaml_filepath_or_contents, verbose=False):
    if verbose:
     logger.debug("get_documents yaml_filepath_or_contents=%s" % yaml_filepath_or_contents)
    docs = []
    if os.path.isfile(yaml_filepath_or_contents):
      if verbose:
       logger.debug("os.path.isfile was True")
      with open(yaml_filepath_or_contents, 'r') as stream:
        for doc in yaml.load_all(stream):
          if doc is None:
            logger.debug("get_documents: doc was None!")
            continue
          if verbose:
            logger.debug("get_documents loaded: %s" % doc)
          docs.append(doc)
    else:
      for doc in yaml.load_all(yaml_filepath_or_contents):
        if doc is None:
          logger.debug("get_documents: doc was None!")
          continue
        if verbose:
          logger.debug("get_documents loaded: %s" % doc)
        docs.append(doc)
    return docs 

 


  @staticmethod
  def utils_create_from_yaml(k8s_client, yaml_file, verbose=False, **kwargs):
    return KubeHelper.make_it_so("create", k8s_client, yaml_file, verbose, **kwargs)

  @staticmethod
  def make_it_so(op,k8s_client, yaml_file, verbose=False, **kwargs):
    ### https://github.com/kubernetes-client/python/issues/740
    ops = [ "create", "delete", "patch" ]
    if not op in ops:
      raise BadRequest(f'Invalid operation={op}')      
       
    yml_object = yaml.load(yaml.dump(yaml_file))
    # TODO: case of yaml file containing multiple objects
    group, _, version = yml_object["apiVersion"].partition("/")
    if version == "":
      version = group
      group = "core"
    # Take care for the case e.g. api_type is "apiextensions.k8s.io"
    # Only replace the last instance
    logger.debug("-1 --> group: %s" % group)
    group = "".join(group.rsplit(".k8s.io", 1))
    logger.debug("0 --> group: %s" % group)
    if len(group.split('.'))>1:
      if verbose:
        logger.debug("Found API group with multiple dots")
      g2 = ""
      g3 = group.split('.')
      logger.debug("g3=%s" % g3)
      for xx in g3:
        logger.debug("-----> xx=%s" % xx)
        g2+=xx.capitalize()
      logger.debug("g2=%s" % g2)
      fcn_to_call = "{0}{1}Api".format(g2, version.capitalize())
    else:
      fcn_to_call = "{0}{1}Api".format(group.capitalize(),version.capitalize())
    if verbose:
      logger.debug("fcn_to_call=%s" % fcn_to_call)
    try:
      if hasattr(client, fcn_to_call):
        k8s_api = getattr(k8s_client, fcn_to_call)(k8s_client)
      
      # Replace CamelCased action_type into snake_case
      kind = yml_object["kind"]
      logger.debug("1 --> kind: %s" % kind)
      kind = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', kind)
      logger.debug("2 --> kind: %s" % kind)
      kind = re.sub('([a-z0-9])([A-Z])', r'\1_\2', kind).lower()
      logger.debug("3 --> kind: %s" % kind)
      # Decide which namespace we are going to put the object in,
      # if any
      if "namespace" in yml_object["metadata"]:
        namespace = yml_object["metadata"]["namespace"]
      else:
        namespace = "default"
      # Expect the user to create namespaced objects more often
      if hasattr(k8s_api, "{0}_namespaced_{1}".format(op,kind)):
        resp = getattr(k8s_api, "{0}_namespaced_{1}".format(op,kind))(body=yml_object, namespace=namespace, **kwargs)
      else:
        resp = getattr(k8s_api, "{0}_{1}".format(op,kind))(body=yml_object, **kwargs)
      if verbose:
        logger.debug("{0} {1}. resp={2}".format(kind, op, resp))

    except Exception as error:
      
      logger.debug("error: %s" % error)
      # Decide which namespace we are going to put the object in,
      # if any
      if "namespace" in yml_object["metadata"]:
        namespace = yml_object["metadata"]["namespace"]
      else:
        namespace = "mongodb"
      api_instance = client.CustomObjectsApi(client.ApiClient())
      group = 'mongodb.com' # str | The custom resource's group name
      version = 'v1' # str | The custom resource's version
      plural = 'mongodbreplicasets' 
      body = yaml_file # object | The JSON schema of the Resource to create.
      pretty = 'true' # str | If 'true', then the output is pretty printed. (optional)

      try: 
        ns = yml_object['metadata']['namespace']
        #resp = api_instance.create_cluster_custom_object(group, version, plural, body, pretty=pretty)
        resp = api_instance.create_namespaced_custom_object(group, version, ns, plural, body, pretty=pretty)
        if verbose:
          logger.debug("resp={0}".format(resp))
      except ApiException as e:
        logger.debug("Exception when calling CustomObjectsApi->create_cluster_custom_object: %s\n" % e)
        resp = e
    return resp 

  @staticmethod
  def create_from_many_yaml(k8s_client, yaml_file, verbose=False):
    responses = []
    yamls = KubeHelper.get_documents(yaml_file, verbose)
    for y in yamls:
      if verbose:
        logger.debug("create_from_many_yaml y=%s" % y)
      responses.append( KubeHelper.utils_create_from_yaml(k8s_client, y,verbose) ) 
    return responses

  @staticmethod
  def create_from_yaml(yaml_file, verbose=False):
    if not os.getenv('KUBERNETES_SERVICE_HOST'): 
      if verbose:
        logger.debug("create_from_yaml: - KUBERNETES_SERVICE_HOST not set!")
      return
    config.load_incluster_config()
    k8s_client = client.ApiClient()
    responses = KubeHelper.create_from_many_yaml(k8s_client, yaml_file, verbose)
    logger.debug("responses: %s" % responses)
    if verbose:
      #info = [ { "kind" : r['kind'], "name" : r['metadata']['name'] } for r in responses ]
      #info = [ { "kind" : r.kind, "name" : r.metadata.name } for r in responses ]
      logger.debug("create_from_yaml: Created: %s" % responses) 
    return responses


  @staticmethod
  def delete_from_yaml(yaml_file, verbose=False):
    config.load_incluster_config()
    k8s_client = client.ApiClient()
    responses = KubeHelper.make_it_so("delete",k8s_client, yaml_file, verbose)
    logger.debug("responses: %s" % responses)
    if verbose:
      #info = [ { "kind" : r['kind'], "name" : r['metadata']['name'] } for r in responses ]
      info = [ { "kind" : r.kind, "name" : r.metadata.name } for r in responses ]
      logger.debug("create_from_yaml: Created: %s" % info) 
    return responses
    


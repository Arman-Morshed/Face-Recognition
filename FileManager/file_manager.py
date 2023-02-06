from Models.Configuration import Configuration
import json

def get_configuration_file():
    with open('configuration.json', 'r') as config_file:
        config_file_json = json.load(config_file)
        schema = config_file_json['schema']
        endpoint = config_file_json['endpoint']
        host = config_file_json['host']
        return Configuration(schema, endpoint, host)
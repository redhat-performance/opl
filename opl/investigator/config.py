import logging

import yaml


def load_config(conf, fp):
    """
    Load config from yaml file pointer and add to conf which is an ArgParser namespace
    """
    data = yaml.load(fp, Loader=yaml.SafeLoader)
    logging.debug(f"Loaded config from {fp.name}: {data}")
    conf.history_type = data['history']['type']
    conf.current_type = data['current']['type']
    conf.sets = data['sets']
    if conf.history_type == 'csv':
        conf.history_file = open(data['history']['file'], 'r')
    if conf.history_type == 'elasticsearch':
        conf.history_es_server = data['history']['es_server']
        assert not conf.history_es_server.endswith('/')
        conf.history_es_index = data['history']['es_index']
        conf.history_es_query = data['history']['es_query']
    if conf.current_type == 'status_data':
        conf.current_file = open(data['current']['file'], 'r')

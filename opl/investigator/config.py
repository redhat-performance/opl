import logging

import jinja2

import yaml


def render_sets(sets, template_data):
    if not isinstance(sets, str):
        logging.debug("No need to render, sets is already a list")
        return sets

    logging.debug(f"Rendering Jinja2 template sets {sets} with data {template_data}")
    env = jinja2.Environment(
        loader=jinja2.DictLoader({'sets': sets}))
    template = env.get_template('sets')
    rendered = template.render(template_data)
    logging.debug(f"Rendered Jinja2 template sets {rendered}")
    return yaml.load(rendered, Loader=yaml.SafeLoader)


def load_config(conf, fp):
    """
    Load config from yaml file pointer and add to conf which is an ArgParser namespace
    """
    data = yaml.load(fp, Loader=yaml.SafeLoader)
    logging.debug(f"Loaded config from {fp.name}: {data}")

    conf.history_type = data['history']['type']
    conf.current_type = data['current']['type']
    conf.sets = data['sets']
    conf.decisions_type = data['decisions']['type']

    if conf.history_type == 'csv':
        conf.history_file = open(data['history']['file'], 'r')

    if conf.history_type == 'elasticsearch':
        conf.history_es_server = data['history']['es_server']
        assert not conf.history_es_server.endswith('/')
        conf.history_es_index = data['history']['es_index']
        conf.history_es_query = data['history']['es_query']

    if conf.current_file is None:
        if conf.current_type == 'status_data':
            conf.current_file = open(data['current']['file'], 'r')

    if conf.decisions_type == 'elasticsearch':
        conf.decisions_es_server = data['decisions']['es_server']
        assert not conf.decisions_es_server.endswith('/')
        conf.decisions_es_index = data['decisions']['es_index']

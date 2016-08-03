from os.path import join

from yaml import safe_load

from svggen import SVGGEN_DIR

def load_yaml(file_name):
    if file_name[-5:] != '.yaml':
        file_name += '.yaml'

    fqn = join(SVGGEN_DIR, 'library', file_name)
    with open(fqn, 'r') as fd:
        return safe_load(fd)


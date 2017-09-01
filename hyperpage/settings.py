from configparser import ConfigParser
import copy
import curtsies.fmtfuncs as fmt
import os.path
from collections import defaultdict

defaults = {
    'em' : 'underline',
    'strong' : 'bold',
    'code' : 'blue',
    'h1' : 'bold red center',
    'h2' : 'bold blue',
    'h3' : 'bold green',
    'a' : 'underline blue',
    'hint' : 'on_red'
}

style_attrs = dict()
render_attrs = defaultdict(list)

def load_ini(path):
    """Load an INI into a dict.

    Only load the "HyperPage" section."""
    cp = ConfigParser()
    cp.read(path)
    if 'HyperPage' not in cp.sections():
        raise RuntimeError('Invalid config file!')
    return dict(cp.items('HyperPage'))

def init(path=None):
    """Initialize the settings."""
    if path is None:
        path = '~/.config/HyperPage/config.ini'
    config = defaults
    if os.path.isfile(path):
        config = load_ini(path)
    rasterize_config(config)

def rasterize_config(config):
    """Fill the settings dicts according to the string-based config dict."""
    for key in config:
        stylestrs = select_stylestrs(config[key])
        renderstrs = select_renderstrs(config[key])
        if stylestrs:
            style_attrs[key] = compose_style(stylestrs)
        if renderstrs:
            render_attrs[key] = renderstrs

def select_stylestrs(cfgstr):
    """Select the style strings from a space-separated config str."""
    stylestrs = []
    for s in cfgstr.split():
        if s in vars(fmt):
            stylestrs.append(s)
    return stylestrs

def select_renderstrs(cfgstr):
    """Select the render strings from a space-separated config str."""
    renderstrs = []
    for s in cfgstr.split():
        if s not in vars(fmt):
            renderstrs.append(s)
    return renderstrs

def compose_style(stylestrs):
    """Compose a style function from the given style strings."""
    funstack = []
    for s in stylestrs:
        funstack.append(vars(fmt)[s])
    def f(t):
        for fun in funstack:
            t = fun(t)
        return t
    return f

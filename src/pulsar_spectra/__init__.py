from importlib.metadata import version
from os import path

__version__ = version(__name__)

CONFIG_DIR = path.join(path.dirname(__file__), "configs")

DEFAULT_PLOTTING_CONFIG = path.join(path.dirname(__file__), "configs/plotting_config.yaml")

DEFAULT_MARKER_CSV = path.join(path.dirname(__file__), "configs/default_markers.csv")

del version
del path

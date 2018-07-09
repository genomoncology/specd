from .model import SpecDir, create_spec_dict
from .app import create_app
from . import tasks, monkey_patch

__all__ = (
    "SpecDir",
    "create_spec_dict",
    "create_app",
    "tasks",
    "monkey_patch",
)

__author__ = """Ian Maurer"""
__email__ = "ian@genomoncology.com"
__version__ = "0.2.0"

__uri__ = "http://www.github.com/genomoncology/specd"
__copyright__ = "Copyright (c) 2018 genomoncology.com"
__description__ = "specd: Swagger Specification Directories"
__doc__ = __description__ + " <" + __uri__ + ">"
__license__ = "MIT"
__title__ = "specd"

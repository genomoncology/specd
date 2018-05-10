from .model import SpecDir
from .app import create_app

__all__ = ("SpecDir", "create_app", "tasks")

__author__ = """Ian Maurer"""
__email__ = "ian@genomoncology.com"
__version__ = "0.1.3"

__uri__ = "http://www.github.com/genomoncology/specd"
__copyright__ = "Copyright (c) 2018 genomoncology.com"
__description__ = "specd: Swagger Specification Directories"
__doc__ = __description__ + " <" + __uri__ + ">"
__license__ = "MIT"
__title__ = "specd"

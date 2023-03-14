"""
Generate a version value from the package metadata.
"""
from importlib_metadata import version as get_version

VERSION = get_version(__package__)

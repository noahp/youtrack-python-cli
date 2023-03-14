"""
Generate a version value from the package metadata.
"""
from importlib_metadata import PackageNotFoundError
from importlib_metadata import version as get_version

# when running tests on the repo, provide a fallback value, since the
# memfault-cli package is not installed at that time
try:
    VERSION = get_version(__package__)
except PackageNotFoundError:
    VERSION = "dev"

try:
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as get_version
except ImportError:
    # fallback for python <3.8
    from importlib_metadata import PackageNotFoundError  # type: ignore[assignment]
    from importlib_metadata import version as get_version

# when running tests on the repo, provide a fallback value, since the
# memfault-cli package is not installed at that time
try:
    version = get_version(__package__)
except PackageNotFoundError:
    version = "dev"

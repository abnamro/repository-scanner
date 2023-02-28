# Standard Library
import argparse
import os


class EnvDefault(argparse.Action):
    """
    Helper for the CLI argparse to allow setting defaults through environment variables
    Usage: In an argparse argument, set the Action to this class.
        Add the extra variable envvar added that has the name of the environment variable containing the default value.
    Example: parser.add_argument("--gitleaks-path", action=EnvDefault, envvar="RESC_GITLEAKS_PATH")
        This would result in the parser reading the env var if it exists and using it as the default,
        always to be overrideable using the cli argument.
    """
    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
        super().__init__(default=default, required=required, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)

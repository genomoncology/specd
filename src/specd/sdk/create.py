from types import ModuleType

from bravado.config import CONFIG_DEFAULTS
from bravado_core.model import ModelMeta
from bravado_core.spec import Spec

from specd import create_spec_dict
from . import client_async, client_sync


def create_sdk(
    specd_path,
    headers=None,
    targets=None,
    host=None,
    config=None,
    models=None,
    origin_url=None,
    async_enabled=False,
    verify_ssl=True,
    loop=None,
    schemes=None,
):
    """ Convenience method for creating an SDK client. """
    spec_dict = create_spec_dict(
        specd_path, targets=targets, host=host, schemes=schemes
    )

    client_ = client_async if async_enabled else client_sync

    http_client = client_.make_http_client(verify_ssl=verify_ssl, loop=loop)

    # Apply bravado config defaults
    config = dict(CONFIG_DEFAULTS, **(config or {}))

    also_return_response = config.pop("also_return_response", False)

    swagger_spec = Spec(spec_dict, origin_url, http_client, config)
    swagger_spec.model_overrides = make_model_overrides(models)
    swagger_spec.build()

    swagger_client = client_.SwaggerClient(
        swagger_spec, also_return_response=also_return_response
    )

    swagger_client.set_headers(headers)

    return swagger_client


def make_model_overrides(models):
    model_overrides = {}
    for override in make_iterable(models):
        if isinstance(override, dict):
            model_overrides.update(override)

        if isinstance(override, ModuleType):
            for name, value in override.__dict__.items():
                if isinstance(value, ModelMeta):
                    model_overrides[name] = value

        if isinstance(override, ModelMeta):
            model_overrides[override.__name__] = override

    return model_overrides


def make_iterable(x):
    """
    Makes the given object or primitive iterable.
    :param x: item to check if is iterable and return as iterable
    :return: list of items that is either x or contains x
    """

    if x is None:
        x = []

    elif not isinstance(x, (list, tuple, set)):
        x = [x]

    return x

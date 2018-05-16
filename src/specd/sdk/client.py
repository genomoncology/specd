from types import ModuleType

import aiohttp
from aiobravado import client
from bravado.config_defaults import CONFIG_DEFAULTS
from bravado_asyncio.definitions import RunMode
from bravado_core.model import ModelMeta
from bravado_core.spec import Spec

from specd import create_spec_dict
from .functions import create_model_type, get_definitions


class SwaggerClient(client.SwaggerClient):
    """ Overrides bravado client to set global headers. """

    def __init__(self, swagger_spec, also_return_response=False):
        super().__init__(swagger_spec, also_return_response)
        self.headers = {}

    def set_headers(self, headers=None, **kwargs):
        self.headers.update(headers or {})
        self.headers.update(kwargs)

    def get_model_type(self, model_name):
        return create_model_type(self.swagger_spec, model_name)

    def instantiate(self, model_name, obj_dict=None, **kwargs):
        obj_dict = obj_dict or {}
        return self.get_model_type(model_name)._from_dict(obj_dict)

    @property
    def definitions(self):
        return get_definitions(self.swagger_spec)

    def _get_resource(self, item):
        """
        :param item: name of the resource to return
        :return: :class:`Resource`
        """
        resource = self.swagger_spec.resources.get(item)
        if not resource:  # pragma: no cover
            raise AttributeError(
                "Resource {0} not found. Available resources: {1}".format(
                    item, ", ".join(dir(self))
                )
            )

        # Wrap bravado-core's Resource and Operation objects in order to
        # execute a service call via the http_client.
        return ResourceDecorator(
            self.headers, resource, self.__also_return_response
        )


class ResourceDecorator(client.ResourceDecorator):
    """ Overrides bravado client to set global headers. """

    def __init__(self, headers, resource, also_return_response=False):
        self.headers = headers
        super(ResourceDecorator, self).__init__(resource, also_return_response)

    def __getattr__(self, name):
        return CallableOperation(
            self.headers,
            getattr(self.resource, name),
            self.also_return_response,
        )


class CallableOperation(client.CallableOperation):
    """ Overrides bravado client to set global headers. """

    def __init__(self, headers, operation, also_return_response=False):
        self.headers = headers
        super(CallableOperation, self).__init__(
            operation, also_return_response
        )

    def update_headers(self, op_kwargs):
        if self.headers:
            # get headers handle from request options, set to {} if N/A
            options = op_kwargs.setdefault("_request_options", {})
            headers = options.setdefault("headers", {})

            # only add global headers to request headers if not included
            for (key, value) in self.headers.items():
                if key not in headers:
                    headers[key] = value

    def __call__(self, **op_kwargs):  # pragma: no cover
        self.update_headers(op_kwargs)
        return super(CallableOperation, self).__call__(**op_kwargs)


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
):
    """ Convenience method for creating an SDK client. """
    spec_dict = create_spec_dict(specd_path, targets=targets, host=host)

    run_mode = RunMode.FULL_ASYNCIO if async_enabled else RunMode.THREAD
    http_client = client.AsyncioClient(run_mode=run_mode, loop=loop)

    # override the
    if not verify_ssl:
        connector = aiohttp.TCPConnector(verify_ssl=verify_ssl)
        http_client._connector = connector

    # Apply bravado config defaults
    config = dict(CONFIG_DEFAULTS, **(config or {}))

    also_return_response = config.pop("also_return_response", False)

    swagger_spec = Spec(spec_dict, origin_url, http_client, config)
    swagger_spec.model_overrides = make_model_overrides(models)
    swagger_spec.build()

    swagger_client = SwaggerClient(
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

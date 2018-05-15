from bravado import client
from bravado.config_defaults import CONFIG_DEFAULTS
from bravado_core.model import ModelMeta
from bravado_core.spec import Spec
from types import ModuleType

from specd import create_spec_dict
from .functions import create_model_type, get_definitions


class SwaggerClient(client.SwaggerClient):
    """ Overrides bravado client to set global headers. """

    def __init__(self, swagger_spec, also_return_response=False, models=None):
        super().__init__(swagger_spec, also_return_response)
        self.headers = {}
        self.swagger_spec.model_overrides = self._determine_overrides(models)

    @staticmethod
    def _determine_overrides(models):
        all_overrides = {}
        for override in make_iterable(models):
            if isinstance(override, dict):
                all_overrides.update(override)

            if isinstance(override, ModuleType):
                for name, value in override.__dict__.items():
                    if isinstance(value, ModelMeta):
                        all_overrides[name] = value

            if isinstance(override, ModelMeta):
                all_overrides[override.__name__] = override

        return all_overrides

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
    verify=True,
    config=None,
    models=None,
    origin_url=None,
):
    """ Convenience method for creating an SDK client. """
    spec_dict = create_spec_dict(specd_path, targets=targets, host=host)

    http_client = client.RequestsClient()
    http_client.session.verify = verify

    # Apply bravado config defaults
    config = dict(CONFIG_DEFAULTS, **(config or {}))

    also_return_response = config.pop("also_return_response", False)
    swagger_spec = Spec.from_dict(spec_dict, origin_url, http_client, config)

    swagger_client = SwaggerClient(
        swagger_spec, also_return_response=also_return_response, models=models
    )

    swagger_client.set_headers(headers)

    return swagger_client


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

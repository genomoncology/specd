import aiohttp
import asyncio

from aiobravado import client
from bravado_asyncio.definitions import RunMode

from .functions import create_model_type, get_definitions


class SwaggerClient(client.SwaggerClient):
    """ Overrides bravado client to set global headers. """

    def __init__(self, swagger_spec, also_return_response=False):
        super().__init__(swagger_spec, also_return_response)
        self.headers = {}

    async def close(self):
        await self.swagger_spec.http_client.client_session.close()

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


def make_http_client(loop=None, verify_ssl=True):
    run_mode = RunMode.FULL_ASYNCIO
    loop = loop or asyncio.get_event_loop()
    http_client = client.AsyncioClient(run_mode=run_mode, loop=loop)

    if not verify_ssl:
        connector = aiohttp.TCPConnector(verify_ssl=verify_ssl, loop=loop)
        http_client.client_session._connector = connector

    return http_client

from bravado_core.model import Model as BravadoModel

from .functions import get_definitions, create_model_type


class BaseModel(BravadoModel):
    @property
    def definitions(self):
        return get_definitions(self._swagger_spec)

    @classmethod
    def get_model_type(cls, model_name):
        return create_model_type(cls._swagger_spec, model_name)

    @classmethod
    def instantiate(cls, model_name, obj_dict=None, **kwargs):
        obj_dict = obj_dict or {}
        obj_dict.update(kwargs)
        return cls.get_model_type(model_name)._from_dict(obj_dict)

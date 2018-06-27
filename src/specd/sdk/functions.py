import enum

from bravado_core import model


def get_definitions(swagger_spec):
    """ Converts definition dict into an enum to eliminate magic strings. """
    if not hasattr(swagger_spec, "_definitions_enum"):
        def_dict = swagger_spec.spec_dict.get("definitions")
        swagger_spec._definitions_enum = enum.Enum("Definitions", def_dict)
    return swagger_spec._definitions_enum


def get_model_spec(swagger_spec, model_name):
    return get_definitions(swagger_spec)[model_name].value


def create_model_type(
    swagger_spec, model_name, model_spec=None, json_reference=None, **_
):
    """ Overrides default type construction to inject new base class. """

    if isinstance(model_name, enum.Enum):
        model_spec = model_name.value
        model_name = model_name.name

    model_spec = model_spec or get_model_spec(swagger_spec, model_name)

    inherits_from = []
    if "allOf" in model_spec:  # pragma: no cover
        for schema in model_spec["allOf"]:
            inherited_name = swagger_spec.deref(schema).get(
                model.MODEL_MARKER, None
            )
            if inherited_name:
                inherits_from.append(inherited_name)

    model_overrides = getattr(swagger_spec, "model_overrides", {})
    base = model_overrides.get(model_name, model.Model)

    return type(
        str(model_name),
        (base,),
        dict(
            __doc__=model.ModelDocstring(),
            _swagger_spec=swagger_spec,
            _model_spec=model_spec,
            _properties=model.collapsed_properties(model_spec, swagger_spec),
            _inherits_from=inherits_from,
            _json_reference=json_reference,
        ),
    )


model.create_model_type = create_model_type

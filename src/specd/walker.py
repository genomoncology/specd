from datetime import datetime

import inflect
import related

TYPE_META_MAPPING = {
    str: {"format": "char", "type": "string"},
    bool: {"format": "boolean", "type": "boolean"},
    int: {"format": "int64", "type": "integer"},
    float: {"format": "double", "type": "number"},
    datetime: {"format": "date-time", "type": "string"},
    list: {"type": "array"},
    dict: {"type": "object"},
}

UNKNOWN = {"format": "unknown", "type": "unknown"}

plural = inflect.engine()


@related.immutable()
class Definition(object):
    name = related.StringField()
    properties = related.ChildField(dict)


def make_name(parent_name: str, prop_key: str):
    prop_name = "".join(
        (plural.singular_noun(x) or x).capitalize()
        for x in prop_key.split("_")
    )
    return f"{parent_name}{prop_name}"


def get_prop_meta(value):
    value_type = type(value)
    return TYPE_META_MAPPING.get(value_type, UNKNOWN).copy()


def generate_for_array(parent: str, prop_key: str, result: list):
    first_value = result[0] if result else None

    if isinstance(first_value, dict):
        super_dict = {}
        for item in result:
            super_dict.update(item)

        child_cls_name = make_name(parent, prop_key)
        for definition in generate_definitions(child_cls_name, super_dict):
            yield definition

    else:
        yield get_prop_meta(first_value)


def generate_for_child(parent: str, prop_key: str, child: dict):
    child_cls_name = make_name(parent, prop_key)
    for definition in generate_definitions(child_cls_name, child):
        yield definition


def generate_definitions(name: str, result_dict: dict):
    this_properties = {}
    for (key, value) in result_dict.items():
        child_props = get_prop_meta(value)
        this_properties[key] = child_props

        if isinstance(value, list):
            for item_def in generate_for_array(name, key, value):
                if isinstance(item_def, Definition):
                    yield item_def
                    child_props["items"] = {
                        "$ref": f"#/definitions/{item_def.name}"
                    }
                else:
                    child_props["items"] = item_def

        elif isinstance(value, dict):
            for child_def in generate_for_child(name, key, value):
                yield child_def
                child_props["$ref"] = f"#/definitions/{child_def.name}"

    yield Definition(name, this_properties)

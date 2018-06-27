import json
import yaml


def str_to_dict(content_str: str) -> dict:
    try:
        return json.loads(content_str)
    except json.JSONDecodeError:
        return yaml.safe_load(content_str)


def file_path_to_dict(input_file_path: str) -> dict:
    content_str = open(input_file_path, "rU").read()
    return str_to_dict(content_str)


def dict_to_str(spec: dict, format: str) -> str:
    if format.lower() == "yaml":
        return yaml.dump(spec, default_flow_style=False)
    else:
        return json.dumps(spec, indent=4)

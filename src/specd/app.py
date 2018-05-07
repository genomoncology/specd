import os
from flask import Flask, redirect, jsonify, abort, request
from flask_swagger_ui import get_swaggerui_blueprint
from .model import SpecDir


def build_doc_url(host, targets):
    params = [f"host={host}"] if host else []
    for target in targets:
        params.append(f"target={target}")
    return f"/doc?{'&'.join(params)}" if params else "/doc"


def add_swagger(app, host, name, target):
    target = target or []
    DOC_URL = build_doc_url(host, target)
    UI_URL = "/ui"

    swagger_blueprint = get_swaggerui_blueprint(
        UI_URL, DOC_URL, config={"app_name": name or "Swagger UI"}
    )

    @app.route("/")
    def main():
        return redirect("/ui", code=302)

    @app.route("/doc")
    def doc():
        targets = request.args.getlist("target")
        spec_dir = SpecDir(os.getcwd())
        spec_dir.exists() or abort(404)
        spec_dict = spec_dir.as_dict(targets=targets)

        host = request.args.get("host", None)
        if host:
            spec_dict["host"] = host

        return jsonify(spec_dict)

    app.register_blueprint(swagger_blueprint, url_prefix=UI_URL)


def create_app(include_swagger=True, host=None, name=None, target=None):
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["ENV"] = "swagger"

    if include_swagger:
        add_swagger(app, host, name, target)

    return app

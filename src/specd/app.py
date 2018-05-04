import os
from flask import Flask, redirect, jsonify, abort, request
from flask_swagger_ui import get_swaggerui_blueprint
from .model import SpecDir


def add_swagger(app):
    UI_URL = '/ui'
    DOC_URL = '/doc'

    swagger_blueprint = get_swaggerui_blueprint(
        UI_URL,
        DOC_URL,
        config={
            'app_name': "specd",
        },
    )

    @app.route("/")
    def main():
        return redirect("/ui", code=302)

    @app.route("/doc")
    def doc():
        spec_dir = SpecDir(os.getcwd())
        spec_dir.exists() or abort(404)
        spec_dict = spec_dir.as_dict()

        host = request.args.get("host", None)
        if host:
            spec_dict["host"] = host

        return jsonify(spec_dict)

    app.register_blueprint(swagger_blueprint, url_prefix=UI_URL)


def create_app(include_swagger=True):
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['ENV'] = 'swagger'

    if include_swagger:
        add_swagger(app)

    return app

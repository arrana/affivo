import os

from flask import Flask
from .config import config

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    from .db import db
    db.init_app(app)
    # app.config.from_mapping(
    #     SECRET_KEY=,
    #     DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    # )
    from . import AuthUser
    from .email import EmailAuthentication
    app.register_blueprint(AuthUser.bp)
    app.register_blueprint(EmailAuthentication.ebp)
    # filename = app.root_path + '/config/application.cfg'
    # with open(filename) as f:
    #     config = f.read()
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object(app.config.from_object(config.ProdConfig))
        app.config.from_mapping(
            SECRET_KEY=app.config['SECRET_KEY']
        )
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app



import click
from flask import current_app, g, Flask
from flask.cli import with_appcontext
app = Flask(__name__)
import mysql.connector

from flask import current_app
from mysql.connector import errorcode

# DB_NAME = 'affivoweb'
#
# host_args = {
#     "host": "localhost",
#     "user": "root",
#     "password": "",
#     "database":DB_NAME
# }


def get_db(want_db_creation=None):
    try:
        if want_db_creation is None:
            cnx = mysql.connector.connect(**current_app.config['HOST_ARGS'])
        else:
            cnx = mysql.connector.connect(user='root', password='')
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return err.errno
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            return err.errno
        else:
            return err
    else:
        cnx.close()


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'utf8'".format(current_app.config['DB_NAME']))
        cursor.execute("USE {}".format(current_app.config['DB_NAME']))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)


def init_db():
    db = get_db(want_db_creation='Yes')
    if db.is_connected():
        cursor = db.cursor()
        create_database(cursor)
        for line in current_app.open_resource('db/sql/schema.sql').read().decode('utf8').split(';\n'):
            cursor.execute(line)
        cursor.close()
    db.close()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

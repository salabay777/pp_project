import flask
from flask import Flask
from waitress import serve

app = Flask(__name__)


@app.route("/api/v1/hello-world-20")
def starting_endpoint():
    return flask.Response(status=200, response="Hello World 20")


serve(app, port='8081')

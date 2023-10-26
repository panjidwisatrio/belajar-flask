from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello world</p>"


@app.route("/test")
def open_test():
    return render_template('hello.html')

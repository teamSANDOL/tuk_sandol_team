from flask import Flask

app = Flask(__name__)


@app.route("/")
def root():
    return "Hello Sandol"


@app.route("/lib")
def library():
    return "Hello lib"


if __name__ == "__main__":
    app.run()

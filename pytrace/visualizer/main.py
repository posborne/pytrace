from pytrace.reader import tables
from pytrace.reader.tables import Trace, Arg, ArgName, ArgValue, Type, Module, Func
import os
import sys
import flask

app = flask.Flask(__name__)
db = None

@app.route("/")
def index():
    return "Hello, world!"


@app.route("/bythread")
def bythread():
    data_by_tid= {}
    for tid in db.session.query(Trace.tid).distinct():
        data_by_tid[tid[0]] = db.session.query(Trace).filter(Trace.tid == tid[0])
    return flask.render_template("index.html", data_by_tid=data_by_tid)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = sys.argv[1]
        os.chdir(os.path.dirname(path))

    db = tables.DB(uri='sqlite:///traces.sqlite')
    app.run(host='0.0.0.0', debug=True)

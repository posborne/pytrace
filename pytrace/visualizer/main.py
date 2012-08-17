from pytrace.reader import tables
from pytrace.reader.tables import Trace, Arg, ArgName, ArgValue, Type, Module, Func
import os
import sys
import flask
import pprint

app = flask.Flask(__name__)
db = None

@app.route("/")
def by_thread_function():
    traces_by_tid= {}
    for tid in db.session.query(Trace.tid).distinct():
        traces_by_tid[tid[0]] = (db.session.query(Trace)
                                 .filter(Trace.tid == tid[0])
                                 .order_by(Trace.id))  # call order?

    funcstats_by_tid = {}
    for tid, traces in traces_by_tid.iteritems():
        funcs = {}
        funcstats_by_tid[tid] = {'traces': traces,
                                 'funcs': funcs, }
        call_times = {}  # depth -> call_time
        for trace in traces:
            if trace.func_id not in funcs:
                funcs[trace.func_id] = {'func': trace.func,
                                        'call_count': 0,
                                        'tottime': 0, }
            funcdata = funcs[trace.func_id]
            if trace.type == "call":
                call_times.setdefault(trace.func_id, {})[trace.depth] = trace.time
                funcdata['call_count'] += 1
            elif trace.type == "return" or trace.type == "exception":
                start_time = call_times.setdefault(trace.func_id, {}).setdefault(trace.depth, trace.time)
                timedelta = trace.time - start_time
                del call_times[trace.func_id][trace.depth]
                funcdata['tottime'] += timedelta

    return flask.render_template("index.html", funcstats_by_tid=funcstats_by_tid)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = sys.argv[1]
        os.chdir(os.path.dirname(path))

    db = tables.DB(uri='sqlite:///traces.sqlite')
    app.run(host='0.0.0.0', debug=True)

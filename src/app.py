from flask import Flask, render_template, redirect, request
from flask_fontawesome import FontAwesome
from queue import Queue, Empty
from io import StringIO
import csv

from tree_mergesort import decision_ui, prepare, update_tree, BadPath

app = Flask(__name__)
FontAwesome(app)

tree = None
paths = Queue()
paths_in_use = []
passed = []
headers = []
max_pass = 0

def get_next_path():
    try:
        return paths.get(False)
    except Empty:
        if len(paths_in_use) > 0:
            return paths_in_use.pop(0)
        else:
            raise Empty

@app.route("/")
def main_page():
    if tree == None:
        return render_template('input_data.html')
    elif tree.complete:
        return render_template('complete.html', list = passed + tree.elts, headers = headers)
    elif len(passed) >= max_pass:
        return render_template('complete.html', list = passed, headers = headers)
    else:
        try:
            path = get_next_path()
            paths_in_use.append(path)
            return decision_ui(path, tree, headers)
        except Empty:
            return render_template('no_work.html')

@app.route("/input", methods=["POST"])
def upload_data():
    global max_pass, headers, tree, paths

    if tree != None:
        return redirect("/")

    csvstream = StringIO(request.files["csv"].stream.read().decode("UTF8"), newline=None)
    csvlist = list(csv.reader(csvstream))
    headers = csvlist[0]
    tree, tree_paths = prepare(csvlist[1:])
    for path in tree_paths:
        paths.put(path)
    
    if "max_pass" not in request.form or request.form["max_pass"] == "":
        max_pass = len(csvlist)
    else:
        max_pass = int(request.form["max_pass"])

    return redirect("/")

@app.route("/update", methods=["POST"])
def tree_post():
    global max_pass
    path = request.form["path"]
    if path not in paths_in_use:
        return redirect('')
    paths_in_use.remove(path)
    left_id = request.form["left"]
    right_id = request.form["right"]
    command = request.form["command"]
    direction = request.form["direction"]
    if command in ["PASS", "STRIKE", "SORT"] and direction in ["l", "r"]:
        try:
            new_path = update_tree(tree, passed, path, left_id, right_id, command, direction, max_pass)
            if new_path != None:
                paths.put(new_path)
        except BadPath:
            pass
    return redirect("/")

if __name__ == "__main__":
    app.run()
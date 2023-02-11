from flask import Flask, render_template, redirect, request, send_file
from queue import Queue, Empty
from io import StringIO, BytesIO
import csv
import pickle
from html import escape

from tree_mergesort import decision, prepare, update_tree, BadPath

app = Flask(__name__)

def replace_newlines(str):
    return "<br>".join(escape(str).split("\n"))

app.jinja_env.globals.update(replace_newlines=replace_newlines)

tree = None
paths = Queue()
paths_in_use = []
passed = []
headers = []
max_pass = 0

def get_next_path():
    """Get a path from the queue, or steal a path currently in use by someone else if the queue has no paths left.  Return the path plus a flag indicating if it was stolen."""
    try:
        return paths.get(False), False
    except Empty:
        if len(paths_in_use) > 0:
            oldest = paths_in_use.pop(0)
            paths_in_use.append(oldest)
            return(oldest, True)
        else:
            raise Empty

@app.route("/")
def main_page():
    # There are three options for the main page.
    # 1: "Upload data for sorting"
    if tree == None:
        return render_template('input_data.html')
    # 2: "Sorting complete; view sorted data"
    elif tree.complete:
        return render_template('complete.html', list = passed + tree.elts, headers = headers)
    elif len(passed) >= max_pass:
        return render_template('complete.html', list = passed, headers = headers)
    # 3: "Sort these two pieces of data"
    else:
        path, stolen = get_next_path()
        paths_in_use.append(path)
        left, right = decision(path, tree)
        return render_template("decision.html", path=path, left=left, right=right, headers=headers, stolen=stolen)

@app.route("/input", methods=["POST"])
def upload_data():
    global max_pass, headers, tree, paths

    # Don't let anyone upload new data if there's already any there.
    # Also serves as a safeguard against people finding long-running instances and uploading malicious pickles.
    if tree != None:
        return redirect("/")

    uploaded_file = request.files["csv"] # "csv" is the name of the upload control in the HTML form.  It doesn't have to be an actual CSV.  If it's a save pickle, it won't be.

    if uploaded_file.mimetype not in ["text/csv", "text/plain"]:
        load(pickle.loads(uploaded_file.stream.read()))
        return redirect("/")

    csvstream = StringIO(uploaded_file.stream.read().decode("UTF8"), newline=None)
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

@app.route("/save")
def save():
    global tree, paths, paths_in_use, passed, headers, max_pass
    data = {
        "tree": tree,
        "paths": list(paths.queue), # Queues have various threading abilities that don't pickle, so we reduce ours to its core list.
        "paths_in_use": paths_in_use,
        "passed": passed,
        "headers": headers,
        "max_pass": max_pass
    }
    return send_file(BytesIO(pickle.dumps(data)), download_name="Ranking.trib", mimetype="application/octet-stream")

# No @app.route -- this is called by upload_data
def load(data):
    global tree, paths, paths_in_use, passed, headers, max_pass
    tree = data["tree"]
    paths_in_use = data["paths_in_use"]
    passed = data["passed"]
    headers = data["headers"]
    max_pass = data["max_pass"]
    for p in data["paths"]: # This queue was stored as a list, so we have to push each item individually.  Changing the order doesn't matter.
        paths.put(p)

@app.route("/export") # Only linked to from the final screen
def export():
    global tree, max_pass, headers

    if tree == None or not (tree.complete or len(passed) >= max_pass):
        return redirect("/")
    
    si = StringIO()
    csvwriter = csv.writer(si)
    csvwriter.writerow(['Original Position'] + headers)
    for index, item in passed + (tree.elts if len(passed) < max_pass else []):
        csvwriter.writerow([index] + item)
    
    return send_file(BytesIO(bytes(si.getvalue(), "UTF8")), download_name="Ranking.csv", mimetype="text/csv")

@app.route("/update", methods=["POST"])
def sort_update():
    global max_pass

    path = request.form["path"]

    if path not in paths_in_use:
        return redirect("/")
    
    paths_in_use.remove(path)

    left_id = request.form["left"]
    right_id = request.form["right"]
    command = request.form["command"]
    direction = request.form["direction"]

    if command not in ["PASS", "STRIKE", "SORT"] or direction not in ["l", "r"]:
        return redirect("/")
    
    try:
        new_path = update_tree(tree, passed, path, left_id, right_id, command, direction, max_pass)
        if new_path != None:
            paths.put(new_path)
    except BadPath: # Exception indicates the user has tried to sort two elements which no longer need sorting.  This usually happens if someone else has stolen that work.  We just fail silently and continue.
        pass

    return redirect("/")

if __name__ == "__main__":
    app.run()
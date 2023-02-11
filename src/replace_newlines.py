from html import escape

def replace_newlines(str):
    return "<br>".join(escape(str).split("\n"))

def replaceNewlines(app):
    app.jinja_env.globals.update(replace_newlines=replace_newlines)
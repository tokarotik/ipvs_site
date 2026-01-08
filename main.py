from flask import Flask, send_from_directory, send_file

app = Flask(__name__)

@app.route("/")
def home():
    return open("site/index.html", encoding="utf-8").read()

@app.route("/license")
def license():
    return f"<pre>{ open('LICENSE.txt', encoding='utf-8').read() }</pre>"

@app.route("/<namepage>")
def page(namepage=None):
    if namepage is None: return home()
    try:
        return open(f"site/pages/{namepage}.html", encoding="utf-8").read()
    except FileNotFoundError:
        return page_not_found(404)
    
@app.route("/scripts/<namepage>")
def scripts(namepage=None):
    if namepage is None: return page_not_found(404)
    try:
        return open(f"site/scripts/{namepage}", encoding="utf-8").read()
    except FileNotFoundError:
        return page_not_found(404)
    
@app.route("/scripts/libs/<namepage>")
def libs(namepage=None):
    return scripts(f"libs/{namepage}")

@app.route("/styles/<namepage>")
@app.route("/styles/<namepage>/<sheet>")
def styles(namepage=None, sheet=None):
    if namepage is None: return page_not_found(404)
    if sheet is None:
        sheet = namepage
    try:
        return send_from_directory(f"site/pages/{namepage.replace('.css', '')}", sheet)
    except FileNotFoundError:
        return page_not_found(404)
    
@app.errorhandler(404)
def page_not_found(e):
    return open("site/404.html", encoding="utf-8").read(), 404


app.run(host="2a02:587:4d09:b400:4b07:bf9c:8f95:e226", port=8000)
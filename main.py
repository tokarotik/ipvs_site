import os
import requests

from enum import Enum
from flask import Flask


class MimeTypes(Enum):
    TEXT = "text/plain;"
    HTML = "text/html;"
    CSS = "text/css;"
    JS = "application/javascript;"
    JSON = "application/json;"
    
    
app = Flask(__name__)
#rootdir = os.getcwd().replace('\\', '/') + '/'
github_url = "https://raw.githubusercontent.com/tokarotik/ipvs_site/refs/heads/main/"

def get_source_file(path: str, mimetype: MimeTypes):
    url = github_url + path
    
    try:
        req = requests.get(url)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return '', 500
    
    if req.status_code == 200:
        return req.text, 200, {'Content-Type': mimetype.value + ' charset=utf-8'}
    if req.status_code == 404:
        print(f"Not found {url}")
        return '', 404
    else:
        print(f"Error fetching {url}: Status code {req.status_code}")
        return '', 500  
    
    

@app.route("/")
def home():
    return get_source_file("site/index.html", MimeTypes.HTML)

@app.route("/license")
def license():
    return get_source_file("site/LICENSE.txt", MimeTypes.TEXT)

@app.route("/<namepage>")
def page(namepage=None):
    if namepage is None: return home()
    try:
        return get_source_file(f"site/pages/{namepage}.html", MimeTypes.HTML)
    except FileNotFoundError:
        return page_not_found(404)
    except Exception:
        return "000", 500
    
@app.route("/scripts/<namepage>")
def scripts(namepage=None):
    if namepage is None: return page_not_found(404)
    try:
        return get_source_file(f"site/scripts/{namepage}", MimeTypes.JS)
    except FileNotFoundError:
        return page_not_found(404)
    except Exception:
        return "000", 500
    
@app.route("/scripts/libs/<namepage>")
def libs(namepage=None):
    return scripts(f"libs/{namepage}")

@app.route("/styles/<namepage>")
@app.route("/styles/<namepage>/<sheet>")
def styles(namepage=None, sheet=None):
    if namepage is None: return page_not_found(404)
    if sheet is None:
        sheet = namepage
    namepage = namepage.replace('.css', '')
    try:
        return get_source_file(f"site/pages/{namepage}/{sheet}", MimeTypes.CSS)
    
    except FileNotFoundError:
        return page_not_found(404)
    except Exception:
        return "000", 500
    
@app.errorhandler(404)
def page_not_found(e):
    return get_source_file("site/404.html", MimeTypes.HTML)

app.run(host="::", port=8000)
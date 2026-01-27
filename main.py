import os
import requests

from enum import Enum
from flask import Flask, send_from_directory, Response, stream_with_context


class MimeTypes(Enum):
    TEXT = "text/plain;"
    HTML = "text/html;"
    CSS = "text/css;"
    JS = "application/javascript;"
    JSON = "application/json;"
    WASM = "application/wasm;"
    BIN = "application/octet-stream"
    PNG = "image/png"
    
app = Flask(__name__)
rootdir = os.getcwd().replace('\\', '/') + '/'
github_url = "https://raw.githubusercontent.com/tokarotik/ipvs_site/refs/heads/main/"

is_deploy = 'home' in rootdir
#is_deploy = True

if is_deploy:
    def get_source_file(path: str, mimetype: MimeTypes, work_text_func = None):
        url = github_url + path
        
        try:
            req = requests.get(url)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return '', 500
        
        charset = ' charset=utf-8'
        if mimetype in [MimeTypes.BIN, MimeTypes.PNG, MimeTypes.WASM]:
            charset = ''
        
        if req.status_code == 200:
            content = req.text
            if work_text_func != None:
                content = work_text_func(content)
            
            def generate(req):
                for chunk in req.iter_content(chunk_size=8192):
                    if chunk:
                        if work_text_func != None:
                            yield work_text_func(chunk.decode()).encode()
                        else:
                            yield chunk
            
            return Response(
                stream_with_context(generate(req)),
                    headers={
                        "Content-Type": mimetype
                    }
                    
            )
        
        
        #content, 200, {'Content-Type': mimetype.value + charset}
        if req.status_code == 404:
            print(f"Not found {url}")
            return '', 404
        else:
            print(f"Error fetching {url}: Status code {req.status_code}")
            return '', 500  

else:
    def get_source_file(path: str, mimetype: MimeTypes, work_text_func = None):
        full_path = os.path.join(os.path.dirname(__file__), path)
        
        charset = ' charset=utf-8'
        if mimetype in [MimeTypes.BIN, MimeTypes.PNG, MimeTypes.WASM]:
            charset = ''
        
        try:
            if charset != '':
                with open(full_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if work_text_func != None:
                        content = work_text_func(content)
                        
                return content, 200, {'Content-Type': mimetype.value + charset}       
             
            with open(full_path, 'rb') as file:
                content = file.read()
            return content, 200, {'Content-Type': mimetype.value} 
            
        except FileNotFoundError:
            print(f"File not found: {full_path}")
            return page_not_found()
        except Exception as e:
            print(f"Error reading file {full_path}: {e}")
            return '', 500

def get_mimetype(filename):
    match filename.split('.')[-1]:
        case 'html': return MimeTypes.HTML
        case 'wasm': return MimeTypes.WASM
        case 'png': return MimeTypes.PNG
        case 'js': return MimeTypes.JS
        case 'pck': return MimeTypes.BIN
        case _: return MimeTypes.TEXT
    


@app.route("/")
def home():
    return get_source_file("site/index.html", MimeTypes.HTML)

@app.route("/assets-games/<game>/")
@app.route("/assets-games/<game>/<path:filename>")
def games_assets(game = None, filename = None):
    if game == None: return page_not_found()
    is_first_page = filename == None
    if is_first_page: filename = 'index.html'
    
    return get_source_file("site/games/"+ str(game) +"/"+ filename, get_mimetype(filename))

@app.route("/games/<game>/")
def games(game=None):
    if game == None: return page_not_found()
    return get_source_file(
        "site/games/template.html", 
        MimeTypes.HTML, 
        lambda x: x.replace("{{ game_name }}", game)
    )

    
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
        
    
@app.route("/scripts/<namepage>/<scriptfile>")
def scripts(namepage=None, scriptfile=None):
    if namepage is None: return page_not_found()
    if scriptfile is None: scriptfile = namepage + '.js'
    try:
        return get_source_file(f"site/pages/{namepage}/{scriptfile}", MimeTypes.JS)
    except FileNotFoundError:
        return page_not_found()
    except Exception:
        return "000", 500
    
@app.route("/scripts/libs/<namepage>")
def libs(namepage=None):
    return scripts(f"libs/{namepage}")

@app.route("/styles/<namepage>")
@app.route("/styles/<namepage>/<sheet>")
def styles(namepage=None, sheet=None):
    if namepage is None: return page_not_found()
    if sheet is None:
        sheet = namepage
    namepage = namepage.replace('.css', '')
    try:
        return get_source_file(f"site/pages/{namepage}/{sheet}", MimeTypes.CSS)
    
    except FileNotFoundError:
        return page_not_found()
    except Exception:
        return "000", 500

@app.route("/assets/<namepage>/<nameassets>")
def assets(namepage: str, nameassests: str):
    if namepage is None: return page_not_found()
    if nameassests is None: return page_not_found()
    try:
        return send_from_directory("size/pages/" + namepage, nameassests)
    
    except FileNotFoundError:
        return page_not_found()
    except Exception:
        return "000", 500  

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.errorhandler(404)
def page_not_found(e = 404):
    return get_source_file("site/404.html", MimeTypes.HTML)

app.run(host="::", port=8000)
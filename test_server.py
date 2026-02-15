from enum import Enum
from flask import Flask


SITE_FOLDER = '.games'
app = Flask(__name__, static_folder = SITE_FOLDER, static_url_path='')

class MimeTypes(Enum):
    TEXT = "text/plain;"
    HTML = "text/html;"
    CSS = "text/css;"
    JS = "application/javascript;"
    JSON = "application/json;"
    WASM = "application/wasm;"
    BIN = "application/octet-stream"
    PNG = "image/png"

def get_mimetype(filename):
    match filename.split('.')[-1]:
        case 'html': return MimeTypes.HTML
        case 'wasm': return MimeTypes.WASM
        case 'png': return MimeTypes.PNG
        case 'js': return MimeTypes.JS
        case 'pck': return MimeTypes.BIN
        case _: return MimeTypes.HTML

def file_mimetype(filename):
	return get_mimetype(filename).value

def get_url(url):
	if url[0] != '/':
		url = '/' + url
	return SITE_FOLDER + url


#@app.route("/")
#def 
"""
@app.route("/<path:url>")
def main(url="index.html"):
	try:
		file = open(get_url(url), 'r', encoding='utf8')
		print("Successfull got", url)
	except FileNotFoundError:
		return page_not_found()

	text = file.read()
	file.close()

	return text, 200, {'Content-Type': file_mimetype(url)}
"""
@app.route("/favicon.ico")
def nothing():
	return ';'

def page_not_found():
	url = '/404.html'
	file = open(get_url(url), 'r', encoding='utf8')
	text = file.read()
	file.close()
	return text, 404, {'Content-Type': file_mimetype(url)}

@app.errorhandler(404)
def _page_not_found(e):
    return page_not_found()


if __name__ == "__main__":
	app.run(debug=True)
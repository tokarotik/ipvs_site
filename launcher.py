
import os
import types
import requests
import importlib
import traceback
from flask import Flask, request

URL: str = "https://github.com/tokarotik/ipvs_site/raw/refs/heads/main/main.py"
LOCAL_CODE_FILE: str = ".last-server-code.py"
is_deploy = True

APP_NAME = "ipvs_site_launcher"
APP_NAME_ERROR = "ipvs_site_launcher_error"

app: Flask = Flask(__name__)
is_error = False

def _log(*message, type="log"):
    print(f"--- Launcher {type} ---", end = " " if type == 'log' else "\n")
    print(' '.join(map(str, message)))
    if type != "log":
        print()

def log(*message):
    _log(*message)
def warning(*message):
    _log(*message, type="warning")
def error(*message):
    _log(*message, type="error")


log(f"Launcer deploy ?", is_deploy)

def return_error(message):
    global app
    
    app = Flask(__name__)
    
    error(f"Can't to start launcher!\n Error: {message}")
    print(traceback.format_exc())
    is_error = True
    
    @app.route("/")
    def index():
        return f"<h1>Oops... Error in launcher of site!</h1><p>{message}</p>", 500


def read_local_code():
    file_saves = open(LOCAL_CODE_FILE, "r", encoding="utf-8")
    text = file_saves.read()
    file_saves.close()
    return text

def save_local_code(text):
    file_saves = open(LOCAL_CODE_FILE, "w", encoding="utf-8")
    file_saves.write(text)
    file_saves.close()


def handle_code_request(CODE_REQUEST):
    if not is_deploy:
        warning("Running in development mode. Code will be loaded from local file, not from GitHub.")
        return open("main.py", "r", encoding="utf-8").read()
    
    if CODE_REQUEST.status_code != 200:
        try:
            warning("Failed to fetch code from GitHub, but found last saved code. Using it.")
            return read_local_code()
            
        except Exception as e:
            raise Exception(f"Failed to fetch code: {CODE_REQUEST.status_code}")
    
    text = CODE_REQUEST.text
    save_local_code(text)
    
    return text

CODE_REQUEST = requests.get(URL)
CODE = None
try:
    log(f"Fetching code from {URL}...")
    CODE = handle_code_request(CODE_REQUEST)
except Exception as e:
    return_error(f"Error fetching code: {e}")

if not is_error:
    try:
        warning("Code will start without restricted imports. Be careful, because it can be unsafe! (hard-coded)")

        
        #env = {"app": app}
        env = {"app": app, "__builtins__": __builtins__}
        exec(CODE, env)
        
        app = env.get("app")
        if app is None:
            return_error("'app' variable not found")
        
    except Exception as e:
        return_error(f"Error executing code: {e}")
        
    print("done")
else:
    print("error")



if __name__ == "__main__":
    log("Is deploy debug ? ", is_deploy)
    app.run(debug=not is_deploy)
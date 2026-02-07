
import os
import types
import requests
import importlib
from flask import Flask

URL: str = "https://github.com/tokarotik/ipvs_site/raw/refs/heads/main/main.py"
ALLOWED_IMPORTS: dict = {
    "modules": ["requests"],
    "functions": {
        "os.path": ["join", "dirname"],
        "os": ["getcwd"],
        "enum": ["Enum"],
        "flask": ["Flask", "redirect", "Response", "stream_with_context"]
    }
}

is_deploy = False
app: Flask = None

print(f"Launcer deploy ?", is_deploy)

def restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    # 1️⃣ Allow full module imports
    if name in ALLOWED_IMPORTS["modules"]:
        return importlib.import_module(name)

    # 2️⃣ Allow function/class-level imports
    if name in ALLOWED_IMPORTS["functions"]:
        allowed_attrs = set(ALLOWED_IMPORTS["functions"][name])
        real_module = importlib.import_module(name)

        # No fromlist: block access to full module
        if not fromlist:
            raise ImportError(f"Direct import of '{name}' is blocked")

        proxy = types.SimpleNamespace()

        for attr in fromlist:
            if attr not in allowed_attrs:
                raise ImportError(f"{attr} not allowed from {name}")
            setattr(proxy, attr, getattr(real_module, attr))

        return proxy

    raise ImportError(f"Import of '{name}' is blocked")

def return_error(message):
    print("--- Launcher error ---")
    print(f"Can't to start launcher!\n Error: {message}")
    
    app = Flask(__name__)
    @app.route("/")
    def error():
        return f"<h1>Oops... Error in launcher of site!</h1><p>{message}</p>", 500
    return app

def handle_code_request(CODE_REQUEST):
    if not is_deploy:
        print("--- Launcher warning ---")
        print("Running in development mode. Code will be loaded from local file, not from GitHub.")
        return open("main.py", "r", encoding="utf-8").read()
    
    if CODE_REQUEST.status_code != 200:
        try:
            file_saves = open("last-server-code.py", "r", encoding="utf-8")
            text = file_saves.read()
            file_saves.close()
            
            print("--- Launcher warning ---")
            print("Failed to fetch code from GitHub, but found last saved code. Using it.")
            return text
            
        except Exception as e:
            raise Exception(f"Failed to fetch code: {CODE_REQUEST.status_code}")
    
    text = CODE_REQUEST.text
    
    file_saves = open("last-server-code.py", "w", encoding="utf-8")
    file_saves.write(text)
    file_saves.close()
    
    return text

CODE_REQUEST = requests.get(URL)
CODE = None
try:
    print(f"Fetching code from {URL}...")
    CODE = handle_code_request(CODE_REQUEST)
except Exception as e:
    app = return_error(f"Error fetching code: {e}")

if app is None:
    try:
        print("--- Launcher warning ---")
        print("Code will start withound restricted imports. Be careful, because it can be unsafe!")
        print()
        exec(CODE, globals=app)
    except Exception as e:
        app = return_error(f"Error executing code: {e}")
    

print("done")

if __name__ == "__main__":
    app.run(debug=True)
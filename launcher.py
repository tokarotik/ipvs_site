
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

app: Flask = None

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
    if CODE_REQUEST.status_code != 200:
        raise Exception(f"Failed to fetch code: {CODE_REQUEST.status_code}")
    
    return CODE_REQUEST.text
    

CODE_REQUEST = requests.get(URL)
CODE = None
try:
    CODE = handle_code_request(CODE_REQUEST)
except Exception as e:
    app = return_error(f"Error fetching code: {e}")

if app is None:
    try:
        exec(CODE, {"__builtins__": {"__import__": restricted_import}})
    except Exception as e:
        app = return_error(f"Error executing code: {e}")
    

print("done")

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, url_for, render_template, send_from_directory, request
import os
from flask_cors import CORS
from app.settings import config
from app.routes import set_routes

app=Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)
config(app)
set_routes(app)

# heroku requires using env var for port
port = .get("PORT", "5000")
# actually doesn't run when in docker, and actualy shouldn't (hence why the conditional is there)
if __name__ == "__main__":
    # Only for debugging while developing
    print("NOW RUNNING!!!!!!!!!!!!!!")
    app.run(host='0.0.0.0', debug=True, port=port)
    print("started")
else:
    print("while then what is my name", __name__)

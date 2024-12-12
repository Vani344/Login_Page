import json
from os import environ as env
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for

# Load environment variables from .env file
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Flask App setup
app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")  # Replace with a secure key stored in .env

load_dotenv()

# Access the variables
client_id = os.getenv('AUTH0_CLIENT_ID')
client_secret = os.getenv('AUTH0_CLIENT_SECRET')
domain = os.getenv('AUTH0_DOMAIN')
secret_key = os.getenv('SECRET_KEY')

# Print the values
print(f"Auth0 Client ID: {client_id}")
print(f"Auth0 Client Secret: {client_secret}")
print(f"Auth0 Domain: {domain}")
print(f"Secret Key: {secret_key}")

# Configure OAuth for Auth0
oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

# Login route
@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

# Login page route (renders the login.html page)
@app.route("/login-page")
def login_page():
    return render_template("login.html")

# Logout route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        f'https://{env.get("AUTH0_DOMAIN")}/v2/logout?'
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

# Callback route (handles Auth0 response)
@app.route("/callback")
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token.get("userinfo")
    return redirect(url_for("home"))

# Home route
@app.route("/")
def home():
    user = session.get("user")
    return render_template("home.html", user=user, pretty=json.dumps(user, indent=4))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))

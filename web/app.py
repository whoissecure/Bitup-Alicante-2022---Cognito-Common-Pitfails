from flask import Flask, render_template, request, redirect, url_for, make_response, session
from flask_awscognito import AWSCognitoAuthentication
from flask_cors import CORS
from jwt.algorithms import RSAAlgorithm
from flask_jwt_extended import (
    JWTManager,
    set_access_cookies,
    verify_jwt_in_request,
    get_jwt_identity,
)
from keys import get_cognito_public_keys
import sqlite3

app = Flask(__name__, template_folder="static")
app.config.from_object("config")
app.config["JWT_PUBLIC_KEY"] = RSAAlgorithm.from_jwk(get_cognito_public_keys())

CORS(app)
aws_auth = AWSCognitoAuthentication(app)
jwt = JWTManager(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    return redirect(aws_auth.get_sign_in_url())

@app.route("/loggedin", methods=["GET"])
def logged_in():
    access_token = aws_auth.get_access_token(request.args)
    session['isAdmin'] = aws_auth.get_user_info(access_token).get('custom:isAdmin')
    session['email'] = aws_auth.get_user_info(access_token).get('email')
    resp = make_response(redirect(url_for("index")))
    set_access_cookies(resp, access_token, max_age=30 * 60)
    return resp

@app.route("/secret")
def protected():
    verify_jwt_in_request()
    if get_jwt_identity():
        connection = sqlite3.connect('app.db')
        cursor = connection.cursor()
        messages = cursor.execute('select * from messages where to_email=?', [session['email'].lower()]).fetchall()
        connection.close()
        return render_template("secret.html", messages=messages)
    else:
        return redirect(aws_auth.get_sign_in_url())

@app.route("/admin")
def admin():
    verify_jwt_in_request()
    if get_jwt_identity():
        if session['isAdmin'] == "1":
            message = "Eres admin!"
        else:
            message = "No eres admin >:|"
        return render_template("admin.html", message=message)
    else:
        return redirect(aws_auth.get_sign_in_url())

@app.route("/files")
def files():
    if 'file' in request.args:
        file = request.args.get('file')
    else:
        return "No file provided"

    try:
        content = open(file).read()
    except Exception as e:
        content = e

    return render_template("files.html", content=content)
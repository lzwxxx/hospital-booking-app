from crypt import methods
from flask import Flask, request, render_template, abort, url_for, session, escape, redirect
from invokes import invoke_http
from os import environ

from __main__ import app

app.secret_key = 'mnUtY272Cy'

admin_user = 'admin'
password = 'admin'

@app.route("/login")
def login():
    if session.get("username") != None:
        return redirect(url_for('index'))
    else:
        return render_template('login.html')

@app.route("/submit_login",methods=["POST"])
def submit_login():
    user = request.form['user']
    pw = request.form['password']

    if user == admin_user and pw == password:
        session["username"] = 'admin'
    else:
        abort(403)
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    session.pop("username", None)

    return redirect(url_for('index'))
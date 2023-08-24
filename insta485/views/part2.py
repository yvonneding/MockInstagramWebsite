"""
Insta485 index (main) view.

URLs include:
/
"""
import uuid
import hashlib
import os
import pathlib
import flask
from flask import redirect, url_for, render_template, request, session
import insta485

insta485.app.secret_key = 'hello'


@insta485.app.route('/accounts/login/', methods=['POST', 'GET'])
def login():
    """Allow user to login."""
    if 'current' in session:
        return redirect(url_for('show_index'))
    if request.method == 'POST':  # not in session
        connection = insta485.model.get_db()
        name = request.form["username"]
        password = request.form["password"]
        cur0 = connection.execute(
            "SELECT EXISTS(SELECT password FROM users WHERE users.username = '"
            + name + "') AS count"
        )
        count = cur0.fetchall()[0]['count']
        if count == 1:  # if user exist
            cur = connection.execute(
                "SELECT password FROM users WHERE users.username = '"
                + name + "'"
            )
            check = cur.fetchall()[0]['password']
            algorithm = 'sha512'
            salt = check[7:39]  # grab salt from stored password
            hash_obj = hashlib.new(algorithm)
            password_salted = salt + password
            hash_obj.update(password_salted.encode('utf-8'))
            password_hash = hash_obj.hexdigest()
            password_db_string = "$".join([algorithm, salt, password_hash])
            if password_db_string == check:  # check for password
                session["current"] = name
                return redirect(url_for("show_index"))
            return flask.abort(403)  # wrong password
        return flask.abort(403)  # user does not exist
    return render_template('login.html')  # get


@insta485.app.route('/accounts/logout/', methods=['POST', 'GET'])
def logout():
    """Allow user to logout."""
    session.pop('current', None)
    return redirect(url_for('login'))


@insta485.app.route('/accounts/create/', methods=['POST', 'GET'])
def create():
    """Allow user to create an account."""
    if request.method == 'POST':
        connection = insta485.model.get_db()
        username = request.form["username"]
        fullname = request.form["fullname"]
        email = request.form["email"]
        fileobj = request.files["file"]
        uuid_basename = "{stem}{suffix}".format(
            stem=uuid.uuid4().hex,
            suffix=pathlib.Path(fileobj.filename).suffix
        )
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)
        password = request.form["password"]
        cur0 = connection.execute(
            "SELECT EXISTS(SELECT * FROM users WHERE users.username = '"
            + username + "') AS count"
        )
        if cur0.fetchall()[0]['count'] == 1:  # if the user already exist
            return flask.abort(409)
        if len(password) == 0:  # if password is empty
            return flask.abort(400)
        # store user into database
        algorithm = 'sha512'
        salt = uuid.uuid4().hex
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        p_db_string = "$".join([algorithm, salt, password_hash])
        connection.execute(
            "INSERT INTO users(username, fullname, email, filename, "
            + "password) VALUES('" + username + "', '" + fullname +
            "', '" + email + "', '" + uuid_basename + "', '" + p_db_string
            + "')"
        )
        session["current"] = username
        return redirect(url_for('show_index'))
    if 'current' in session:  # get
        return redirect(url_for('edit'))
    return render_template('create.html')


@insta485.app.route('/accounts/delete/', methods=['POST', 'GET'])
def delete():
    """Allow user to delete their account."""
    if 'current' in session:
        current = session['current']
        if request.method == 'POST':
            connection = insta485.model.get_db()
            curr2 = connection.execute(
                "SELECT filename "
                "FROM posts WHERE owner = '" + current + "'"
            )
            filename = curr2.fetchall()
            for files in filename:
                pho = insta485.app.config["UPLOAD_FOLDER"]/files['filename']
                os.remove(pho)
            curr3 = connection.execute(
                "SELECT filename FROM users "
                "WHERE username = '" + current + "'"
            )
            icon = curr3.fetchall()[0]['filename']
            iconphoto = insta485.app.config["UPLOAD_FOLDER"]/icon
            os.remove(iconphoto)
            connection.execute(
                "DELETE FROM users WHERE username = '" + current + "'"
            )
            session.pop('current', None)
            return redirect(url_for('create'))
        return render_template('delete.html', current=current)  # get
    return redirect(url_for('login'))  # not logged in


@insta485.app.route('/accounts/edit/', methods=['POST', 'GET'])
def edit():
    """Allow user to edit their file, fullname, and email."""
    if 'current' in session:
        current = session['current']
        connection = insta485.model.get_db()
        cur0 = connection.execute(
            "SELECT * FROM users WHERE username = '" + current + "'"
        )
        user = cur0.fetchall()[0]
        if request.method == 'POST':
            newname = request.form['fullname']
            newemail = request.form['email']
            newfile = request.files.get('file')
            connection.execute(
                "UPDATE users SET fullname = '" + newname + "', email = '"
                + newemail + "' WHERE username = '" + current + "'"
            )
            if newfile:  # if upload file exists
                oldfile = user['filename']
                path = insta485.app.config["UPLOAD_FOLDER"]/oldfile
                os.remove(path)
                newnewfile = request.files['file']
                newfilename = newnewfile.filename
                uuid_basename = "{stem}{suffix}".format(
                    stem=uuid.uuid4().hex,
                    suffix=pathlib.Path(newfilename).suffix
                )
                path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
                newnewfile.save(path)
                connection.execute(
                    "UPDATE users SET filename = '" + uuid_basename +
                    "' WHERE username = '" + current + "'"
                )
            cur1 = connection.execute(
                "SELECT * FROM users WHERE username = '" + current + "'"
            )
            updateuser = cur1.fetchall()[0]
            return render_template('edit.html', user=updateuser)
        return render_template('edit.html', user=user)  # get
    return redirect(url_for('login'))  # not logged in


@insta485.app.route('/accounts/password/', methods=['POST', 'GET'])
def reset_password():
    """Allow user to reset their password."""
    if 'current' in session:
        current = session['current']
        if request.method == 'POST':
            connection = insta485.model.get_db()
            password = request.form['password']
            new_password1 = request.form['new_password1']
            new_password2 = request.form['new_password2']
            cur = connection.execute(
                "SELECT password FROM users WHERE users.username = '"
                + current + "'"
            )
            check = cur.fetchall()[0]['password']
            algorithm = 'sha512'
            salt = check[7:39]  # grab salt from stored password
            hash_obj = hashlib.new(algorithm)
            password_salted = salt + password
            hash_obj.update(password_salted.encode('utf-8'))
            password_hash = hash_obj.hexdigest()
            password_db_string = "$".join([algorithm, salt, password_hash])
            if password_db_string == check:
                if new_password1 == new_password2:
                    salt = uuid.uuid4().hex
                    hash_obj = hashlib.new(algorithm)
                    password_salted = salt + new_password2
                    hash_obj.update(password_salted.encode('utf-8'))
                    password_hash = hash_obj.hexdigest()
                    p_new_db_string = "$".join([algorithm, salt,
                                               password_hash])
                    connection.execute(
                        "UPDATE users SET password = '" + p_new_db_string +
                        "' WHERE username = '" + current + "'"
                    )
                    return redirect(url_for("edit"))
                return flask.abort(401)  # two new passwords do not match
            return flask.abort(403)  # wrong password
        return render_template("password.html", current=current)  # get
    return redirect(url_for('login'))  # not logged in

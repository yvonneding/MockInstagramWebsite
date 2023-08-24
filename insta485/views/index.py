"""
Insta485 index (main) view.

URLs include:
/
"""
import pathlib
import uuid
import os
import flask
import arrow
from flask import redirect, url_for, request, session
import insta485


def post_func_user(current, connection):
    """Help user function."""
    if "follow" in request.form:
        person = request.form['username']
        connection.execute(
            "INSERT INTO following(username1, username2) "
            "VALUES('" + current + "', '" + person + "')"
        )
    elif "unfollow" in request.form:
        person = request.form['username']
        connection.execute(
            "DELETE FROM following WHERE username1 = '" + current
            + "' AND username2 = '" + person + "'"
        )


def post_func(current, connection):
    """Help main function."""
    if "like" in request.form:
        connection.execute(
            "INSERT INTO likes(owner, postid) VALUES('" + current
            + "', " + request.form['postid'] + ")"
        )
    elif "unlike" in request.form:
        connection.execute(
            "DELETE FROM likes WHERE postid = " + request.form['postid'] +
            " AND owner = '" + current + "'"
        )
    if "comment" in request.form:
        text = request.form['text']
        connection.execute(
            "INSERT INTO comments(owner, postid, text) VALUES('" +
            current + "', " + request.form['postid'] + ", '" + text + "')"
        )
    cur = connection.execute(
        "SELECT username, filename "
        "FROM users"
    )
    users = cur.fetchall()
    cur = connection.execute(
        "SELECT DISTINCT posts.postid, posts.owner, posts.filename,"
        " posts.created FROM posts, (SELECT username2 FROM following"
        " WHERE following.username1 = '" + current + "' ) follow"
        " WHERE posts.owner = '" + current + "' OR posts.owner ="
        " follow.username2 ORDER BY posts.postid DESC"
    )
    posts = cur.fetchall()
    for post in posts:
        timestamp = arrow.get(post['created'])
        post['created'] = timestamp.humanize()
    cur = connection.execute(
        "SELECT postid, owner "
        "FROM likes"
    )
    likes = cur.fetchall()
    whetherlike = {}
    numoflike = {}
    for post in posts:
        temp = 0
        for like in likes:
            if post['postid'] == like['postid']:
                temp = temp+1
                if like['owner'] == current:
                    whetherlike[post['postid']] = True
        numoflike[post['postid']] = temp
    cur = connection.execute(
        "SELECT owner as owner, postid, text "
        "FROM comments"
    )
    comments = cur.fetchall()
    # Add database info to context
    context = {"users": users, "posts": posts, "comments": comments,
               "numoflike": numoflike, "whetherlike": whetherlike}
    return flask.render_template("index.html", **context,
                                 logname=current)


@insta485.app.route('/', methods=['POST', 'GET'])
def show_index():
    """Display / route."""
    if ('current' in session) and (request.method == 'GET'):
        current = session['current']
        # Connect to database
        connection = insta485.model.get_db()
        # Query database
        cur = connection.execute(
            "SELECT username, filename FROM users"
        )
        users = cur.fetchall()
        cur = connection.execute(
            "SELECT DISTINCT posts.postid, posts.owner, posts.filename,"
            " posts.created FROM posts, (SELECT username2 FROM following"
            " WHERE following.username1 = '" + current + "' ) follow"
            " WHERE posts.owner = '" + current + "' OR posts.owner ="
            " follow.username2 ORDER BY posts.postid DESC"
        )
        posts = cur.fetchall()
        for post in posts:
            post['created'] = (arrow.get(post['created'])).humanize()
        cur = connection.execute(
            "SELECT postid, owner "
            "FROM likes"
        )
        likes = cur.fetchall()
        whetherlike = {}
        numoflike = {}
        for post in posts:
            temp = 0
            for like in likes:
                if post['postid'] == like['postid']:
                    temp = temp+1
                    if like['owner'] == current:
                        whetherlike[post['postid']] = True
            numoflike[post['postid']] = temp
        cur = connection.execute(
            "SELECT owner as owner, postid, text "
            "FROM comments"
        )
        comments = cur.fetchall()
        # Add database info to context
        context = {"users": users, "posts": posts, "comments": comments,
                   "numoflike": numoflike, "whetherlike": whetherlike}
        return flask.render_template("index.html", **context,
                                     logname=current)
    if ('current' in session) and (request.method == 'POST'):
        current = session['current']
        connection = insta485.model.get_db()
        post_func(current, connection)
    return redirect(url_for("login"))  # not logged in


@insta485.app.route('/uploads/<path:filename>')
def download_file(filename):
    """Display the file."""
    if 'current' not in session:
        return flask.abort(403)
    return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                     filename, as_attachment=True)


@insta485.app.route('/u/<username>/', methods=['POST', 'GET'])
def show_user_url_slug(username):
    """Display the main page of a user."""
    connection = insta485.model.get_db()
    if 'current' in session:
        current = session['current']
        valid = connection.execute(
            "SELECT EXISTS(SELECT username FROM users WHERE username = '"
            + username + "') AS count"
        )
        if valid.fetchall()[0]['count'] == 0:
            return flask.abort(404)
        if request.method == 'GET':
            # Query database
            cur = connection.execute(
                "SELECT EXISTS(SELECT username2 "
                "FROM following WHERE username1 = '" + current + "' "
                "AND username2 = '" + username + "') AS count"
            )
            whether = cur.fetchall()[0]['count']
            cur = connection.execute(
                "SELECT username1, username2 "
                "FROM following"
            )
            followings = cur.fetchall()
            numfollow = 0  # number of following
            numfollower = 0  # number of follower
            for following in followings:
                if following['username1'] == username:
                    numfollow = numfollow + 1
                if following['username2'] == username:
                    numfollower = numfollower + 1

            cur = connection.execute(
                "SELECT postid, filename "
                "FROM posts WHERE posts.owner = '" + username + "'"
            )
            posts = cur.fetchall()

            cur = connection.execute(
                "SELECT fullname "
                "FROM users WHERE username = '" + username + "'"
            )
            users = cur.fetchall()[0]['fullname']

            context = {"posts": posts, "followings":
                       numfollow, "followers": numfollower, "users": users,
                       "whether": whether,
                       "numofpost": len(posts)}
            return flask.render_template("user.html", **context,
                                         logname=current, username=username)
        # post
        post_func_user(current, connection)
        if "logout" in request.form:
            return redirect(url_for('logout'))
        if "create_post" in request.form:
            fileobj = flask.request.files["file"]
            uuid_basename = "{stem}{suffix}".format(
                stem=uuid.uuid4().hex,
                suffix=pathlib.Path(fileobj.filename).suffix
            )
            fileobj.save(insta485.app.config["UPLOAD_FOLDER"]/uuid_basename)
            connection.execute(
                "INSERT INTO posts(filename, owner) VALUES('" + uuid_basename +
                "', '" + current + "')"
            )
        cur = connection.execute(
            "SELECT EXISTS(SELECT username2 "
            "FROM following WHERE username1 = '" + current + "' "
            "AND username2 = '" + username + "') AS count"
        )
        whether = cur.fetchall()[0]['count']
        cur = connection.execute(
            "SELECT username1, username2 "
            "FROM following"
        )
        followings = cur.fetchall()
        numfollow = 0  # number of following
        numfollower = 0  # number of follower
        for following in followings:
            if following['username1'] == username:
                numfollow = numfollow + 1
            if following['username2'] == username:
                numfollower = numfollower + 1
        cur = connection.execute(
            "SELECT postid, filename "
            "FROM posts WHERE posts.owner = '" + username + "'"
        )
        posts = cur.fetchall()
        cur = connection.execute(
            "SELECT fullname "
            "FROM users WHERE username = '" + username + "'"
        )
        users = cur.fetchall()[0]['fullname']
        context = {"following": following, "posts": posts, "followings":
                   numfollow, "followers": numfollower, "users": users,
                   "whether": whether, "numofpost": len(posts)}
        return flask.render_template("user.html", **context,
                                     logname=current, username=username)
    return redirect(url_for("login"))  # not logged in


@insta485.app.route('/u/<username>/following/', methods=['POST', 'GET'])
def show_following(username):
    """Display current user's following."""
    if 'current' in session:
        current = session['current']
        connection = insta485.model.get_db()
        if request.method == 'GET':
            # Query database
            cur = connection.execute(
                "SELECT DISTINCT users.username AS username,"
                " users.filename AS filename FROM following, users "
                "WHERE username1 = '" + username +
                "' AND users.username = username2"
            )
            followings = cur.fetchall()

            cur2 = connection.execute(
                "SELECT DISTINCT username2 "
                "FROM following WHERE username1 = '" + current + "'"
            )
            follows = cur2.fetchall()

            for following in followings:
                numfollow = len(following)
                for follow in follows:
                    if following['username'] == follow['username2']:
                        following['whether'] = True
                if numfollow == len(following):
                    following['whether'] = False
            context = {"followings": followings}
            return flask.render_template("following.html", **context,
                                         logname=current, username=username)
        # post request
        if "follow" in request.form:
            person = request.form['username']
            connection.execute(
                "INSERT INTO following(username1, username2) "
                "VALUES('" + current + "', '" + person + "')"
            )
        elif "unfollow" in request.form:
            person = request.form['username']
            connection.execute(
                "DELETE FROM following WHERE username1 = '" + current
                + "' AND username2 = '" + person + "'"
            )
        cur = connection.execute(
            "SELECT DISTINCT users.username AS username, "
            "users.filename AS filename FROM following, users "
            "WHERE username1 = '" + username +
            "' AND users.username = username2"
        )
        followings = cur.fetchall()
        cur2 = connection.execute(
            "SELECT DISTINCT username2 "
            "FROM following WHERE username1 = '" + current + "'"
        )
        follows = cur2.fetchall()
        for following in followings:
            numfollow = len(following)
            for follow in follows:
                if following['username'] == follow['username2']:
                    following['whether'] = True
            if numfollow == len(following):
                following['whether'] = False
        context = {"followings": followings}
        return flask.render_template("following.html", **context,
                                     logname=current, username=username)
    return redirect(url_for("login"))  # not logged in


@insta485.app.route('/u/<username>/followers/', methods=['POST', 'GET'])
def show_follower(username):
    """Display current user's followers."""
    if 'current' in session:
        current = session['current']
        connection = insta485.model.get_db()
        if request.method == "GET":
            # Query database
            cur = connection.execute(
                "SELECT DISTINCT users.username AS username, "
                "users.filename AS filename FROM following, users "
                "WHERE username2 = '" + username +
                "' AND users.username = username1"
            )
            followers = cur.fetchall()

            cur2 = connection.execute(
                "SELECT DISTINCT username2 "
                "FROM following WHERE username1 = '" + current + "'"
            )
            follows = cur2.fetchall()

            for follower in followers:
                numfollower = len(follower)
                for follow in follows:
                    if follower['username'] == follow['username2']:
                        follower['whether'] = True
                if numfollower == len(follower):
                    follower['whether'] = False
            context = {"followers": followers}
            return flask.render_template("follower.html", **context,
                                         logname=current, username=username)
        # post
        if "follow" in request.form:
            person = request.form['username']
            connection.execute(
                "INSERT INTO following(username1, username2) "
                "VALUES('" + current + "', '" + person + "')"
            )
        if "unfollow" in request.form:
            person = request.form['username']
            connection.execute(
                "DELETE FROM following WHERE username1 = '" + current
                + "' AND username2 = '" + person + "'"
            )
        cur = connection.execute(
            "SELECT DISTINCT users.username AS username, "
            "users.filename AS filename FROM following, users "
            "WHERE username2 = '" + username +
            "' AND users.username = username1"
        )
        followers = cur.fetchall()
        cur2 = connection.execute(
            "SELECT DISTINCT username2 "
            "FROM following WHERE username1 = '" + current + "'"
        )
        follows = cur2.fetchall()
        for follower in followers:
            numfollower = len(follower)
            for follow in follows:
                if follower['username'] == follow['username2']:
                    follower['whether'] = True
            if numfollower == len(follower):
                follower['whether'] = False
        context = {"followers": followers}
        return flask.render_template("follower.html", **context,
                                     logname=current, username=username)
    return redirect(url_for("login"))  # not logged in


@insta485.app.route('/p/<post>/', methods=['POST', 'GET'])
def show_post(post):
    """Display current post."""
    if 'current' in session:
        current = session['current']
        connection = insta485.model.get_db()
        if request.method == "GET":
            cur = connection.execute(
                "SELECT username, filename "
                "FROM users"
            )
            users = cur.fetchall()
            cur = connection.execute(
                "SELECT filename, owner, created "
                "FROM posts WHERE postid = '" + post + "'"
            )
            posts = cur.fetchall()[0]

            timestamp = arrow.get(posts['created'])
            posts['created'] = timestamp.humanize()

            cur = connection.execute(
                "SELECT postid, owner "
                "FROM likes WHERE postid = " + post + ""
            )
            likes = cur.fetchall()

            cur = connection.execute(
                "SELECT EXISTS(SELECT owner FROM likes WHERE postid = " +
                post + " AND owner = '" + current + "') AS count"
            )
            whetherlike = cur.fetchall()[0]['count']
            cur = connection.execute(
                "SELECT commentid, owner, postid, text "
                "FROM comments WHERE postid = " + post + ""
            )
            comments = cur.fetchall()

            # Add database info to context
            context = {"users": users, "posts": posts, "comments": comments,
                       "numoflike": len(likes), "whetherlike": whetherlike}
            return flask.render_template("post.html", **context,
                                         logname=current, post=post)
        # post
        if "uncomment" in request.form:
            comment = request.form['commentid']
            connection.execute(
                "DELETE FROM comments WHERE commentid = " + comment
            )
        if "delete" in request.form:
            post = request.form['postid']
            cur = connection.execute(
                "SELECT owner FROM posts WHERE postid = " + post
            )
            if current != cur.fetchall()[0]['owner']:
                return flask.abort(403)
            cur = connection.execute(
                "SELECT filename FROM posts WHERE postid = " + post
            )
            path = insta485.app.config["UPLOAD_FOLDER"] / \
                cur.fetchall()[0]['filename']
            connection.execute(
                "DELETE FROM posts WHERE postid = " + post
            )
            os.remove(path)
            return redirect(url_for('show_user_url_slug',
                                    username=current))
        if "like" in request.form:
            connection.execute(
                "INSERT INTO likes(owner, postid) VALUES('" + current
                + "', " + request.form['postid'] + ")"
            )
        elif "unlike" in request.form:
            connection.execute(
                "DELETE FROM likes WHERE postid = " + request.form['postid'] +
                " AND owner = '" + current + "'"
            )
        if "comment" in request.form:
            text = request.form['text']
            connection.execute(
                "INSERT INTO comments(owner, postid, text) VALUES('"
                + current + "', " + request.form['postid']
                + ", '" + text + "')"
            )
        cur = connection.execute(
            "SELECT username, filename "
            "FROM users"
        )
        users = cur.fetchall()
        cur = connection.execute(
            "SELECT filename, owner, created "
            "FROM posts WHERE postid = '" + post + "'"
        )
        posts = cur.fetchall()[0]
        timestamp = arrow.get(posts['created'])
        posts['created'] = timestamp.humanize()
        cur = connection.execute(
            "SELECT postid, owner "
            "FROM likes WHERE postid = " + post + ""
        )
        likes = cur.fetchall()
        cur = connection.execute(
            "SELECT EXISTS(SELECT owner FROM likes WHERE postid = " +
            post + " AND owner = '" + current + "') AS count"
        )
        whetherlike = cur.fetchall()[0]['count']
        cur = connection.execute(
            "SELECT commentid, owner, postid, text "
            "FROM comments WHERE postid = " + post
        )
        comments = cur.fetchall()
        # Add database info to context
        context = {"users": users, "posts": posts, "comments": comments,
                   "numoflike": len(likes), "whetherlike": whetherlike}
        return flask.render_template("post.html", **context,
                                     logname=current, post=post)
    return redirect(url_for("login"))  # not logged in


@insta485.app.route('/explore/', methods=['POST', 'GET'])
def show_explore():
    """Display the explore page."""
    if 'current' in session:
        current = session['current']
        connection = insta485.model.get_db()
        if request.method == "GET":
            cur1 = connection.execute(
                "SELECT username2 FROM following WHERE username1 = '"
                + current + "'"
            )
            following = cur1.fetchall()

            cur2 = connection.execute(
                "SELECT username, filename FROM users"
            )
            users = cur2.fetchall()
            people = []
            for user in users:
                temp = 0
                for follow in following:
                    if user['username'] == follow['username2'] or \
                       user['username'] == current:
                        temp = temp + 1
                if temp == 0:
                    people.append({'filename': user['filename'], 'username':
                                  user['username']})
            context = {"people": people}
            return flask.render_template("explore.html", **context,
                                         logname=current)
        # post
        person = request.form['username']
        connection.execute(
            "INSERT INTO following(username1, username2) "
            "VALUES('" + current + "', '" + person + "')"
        )
        cur1 = connection.execute(
            "SELECT username2 FROM following WHERE username1 = '"
            + current + "'"
        )
        following = cur1.fetchall()
        cur2 = connection.execute(
            "SELECT username, filename FROM users"
        )
        users = cur2.fetchall()
        people = []
        for user in users:
            temp = 0
            for follow in following:
                if user['username'] == follow['username2'] or \
                   user['username'] == current:
                    temp = temp + 1
            if temp == 0:
                people.append({'filename': user['filename'], 'username':
                              user['username']})
        context = {"people": people}
        return flask.render_template("explore.html", **context,
                                     logname=current)
    return redirect(url_for("login"))  # not logged in

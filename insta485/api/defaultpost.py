"""REST API for posts."""
import flask
from flask import session
import insta485


@insta485.app.route('/api/v1/p/', methods=["GET"])
def get_posts():
    """GET /api/v1/p/."""
    if 'current' in session:
        size = flask.request.args.get("size", default=10, type=int)
        page = flask.request.args.get("page", default=0, type=int)
        current = session['current']
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT DISTINCT posts.postid AS postid FROM posts,"
            "(SELECT username2 AS username FROM following "
            "WHERE username1 = '" + current + "')follow "
            "WHERE posts.owner = '" + current + "' "
            "OR posts.owner = follow.username "
            "ORDER BY posts.postid DESC "
            "LIMIT " + str(size) + " OFFSET " + str(page * size)
        )
        posts = cur.fetchall()
        cur = connection.execute(
            "SELECT DISTINCT posts.postid AS postid FROM posts,"
            "(SELECT username2 AS username FROM following "
            "WHERE username1 = '" + current + "')follow "
            "WHERE posts.owner = '" + current + "' "
            "OR posts.owner = follow.username "
            "ORDER BY posts.postid DESC "
            "LIMIT " + str(size) + " OFFSET " + str((page+1)*size)
        )
        nextpost = cur.fetchall()
        nextpagepost = len(nextpost)
        context = {}
        results = []
        for post in posts:
            post_info = {}
            post_info["postid"] = post['postid']
            post_info["url"] = "/api/v1/p/" + str(post['postid']) + "/"
            results.append(post_info)
        context["next"] = ""
        if nextpagepost != 0:
            context["next"] = (flask.request.path + "?size=" + str(size)
                               + "&page=" + str(page+1))
        context["results"] = results
        context["url"] = flask.request.path

        return flask.jsonify(**context)
    forbidden = {
        "message": "Forbidden",
        "status_code": 403
    }
    return flask.jsonify(**forbidden), 403

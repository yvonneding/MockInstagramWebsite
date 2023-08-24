"""REST API for comments."""
import flask
from flask import session
import insta485


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/comments/',
                    methods=["GET"])
def get_comment(postid_url_slug):
    """GET /api/v1/p/<postid>/comments/."""
    if 'current' in session:
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(postid) AS exist FROM posts"
        )
        postnum = cur.fetchall()[0]['exist']
        if postid_url_slug > postnum:
            errormessage = {
                "message": "NOT FOUND",
                "status_code": 404
            }
            return flask.jsonify(**errormessage), 404
        cur = connection.execute(
            "SELECT DISTINCT comments.commentid AS commentid, "
            "comments.owner AS owner, comments.text AS text FROM comments "
            "WHERE comments.postid = " + str(postid_url_slug)
        )
        comments_info = cur.fetchall()
        context = {}
        comments = []
        for comment_info in comments_info:
            each_comment = {}
            each_comment["commentid"] = comment_info["commentid"]
            each_comment["owner"] = comment_info["owner"]
            each_comment["owner_show_url"] = ("/u/" +
                                              comment_info["owner"] + "/")
            each_comment["postid"] = postid_url_slug
            each_comment["text"] = comment_info["text"]
            comments.append(each_comment)
        context["comments"] = comments
        context["url"] = flask.request.path
        return flask.jsonify(**context)
    forbidden_error = {
        "message": "Forbidden",
        "status_code": 403
    }
    return flask.jsonify(**forbidden_error), 403


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/comments/',
                    methods=["POST"])
def post_comment(postid_url_slug):
    """POST /api/v1/p/<postid>/comments/."""
    if 'current' in session:
        current = session['current']
        comment = flask.request.json["text"]
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(postid) AS exist FROM posts"
        )
        postnum = cur.fetchall()[0]['exist']
        if postid_url_slug > postnum:
            errormessage = {
                "message": "NOT FOUND",
                "status_code": 404
            }
            return flask.jsonify(**errormessage), 404
        cur = connection.execute(
            "INSERT INTO comments(owner, postid, text) "
            "VALUES ('" + current + "', " + str(postid_url_slug) +
            ", '" + comment + "')"
        )
        cur = connection.execute(
            "SELECT commentid, owner, postid, text "
            "FROM comments WHERE commentid = last_insert_rowid()"
        )
        new_comment = cur.fetchall()[0]
        context = {
            "commentid": new_comment["commentid"],
            "owner": new_comment["owner"],
            "owner_show_url": "/u/" + new_comment["owner"] + "/",
            "postid": new_comment["postid"],
            "text": new_comment["text"]
        }
        return flask.jsonify(**context), 201
    loginerror = {
        "message": "Forbidden",
        "status_code": 403
    }
    return flask.jsonify(**loginerror), 403

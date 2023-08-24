"""REST API for likes."""
import flask
from flask import session
import insta485


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/likes/', methods=["GET"])
def get_likes(postid_url_slug):
    """Return likes on postid."""
    if 'current' in session:
        current = session['current']
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(postid) AS exist FROM posts"
        )
        postindex = cur.fetchall()[0]['exist']
        if postid_url_slug > postindex:
            errorcontext = {
                "message": "NOT FOUND",
                "status_code": 404
            }
            return flask.jsonify(**errorcontext), 404
        cur = connection.execute(
            "SELECT COUNT(owner) AS numoflike "
            "FROM likes WHERE postid = " + str(postid_url_slug)
        )
        numoflike = cur.fetchall()[0]['numoflike']
        cur = connection.execute(
            "SELECT EXISTS(SELECT owner FROM likes "
            "WHERE postid = '" + str(postid_url_slug) + "' "
            "AND owner = '" + current + "') AS whetherlike"
        )
        whetherlike = cur.fetchall()[0]['whetherlike']
        context = {
            "logname_likes_this": whetherlike,
            "likes_count": numoflike,
            "postid": postid_url_slug,
            "url": flask.request.path,
        }
        return flask.jsonify(**context)
    context = {
        "message": "Forbidden",
        "status_code": 403
    }
    return flask.jsonify(**context), 403


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/likes/',
                    methods=["DELETE"])
def delete_likes(postid_url_slug):
    """DELETE /api/v1/p/<postid>/likes/."""
    if 'current' in session:
        current = session['current']
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(postid) AS exist FROM posts"
        )
        numofpost = cur.fetchall()[0]['exist']
        if postid_url_slug > numofpost:
            context = {
                "message": "NOT FOUND",
                "status_code": 404
            }
            return flask.jsonify(**context), 404
        connection.execute(
            "DELETE FROM likes WHERE postid = " + str(postid_url_slug) +
            " AND owner = '" + current + "'"
        )
        return flask.jsonify(' '), 204
    # make_response(flask.jsonify({'error': 'Not'}), 204)
    errorcontext = {
        "message": "Forbidden",
        "status_code": 403
    }
    return flask.jsonify(**errorcontext), 403


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/likes/', methods=["POST"])
def post_likes(postid_url_slug):
    """POST /api/v1/p/<postid>/likes/."""
    if 'current' in session:
        current = session['current']
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(postid) AS exist FROM posts"
        )
        numofpost = cur.fetchall()[0]['exist']
        if postid_url_slug > numofpost:
            context = {
                "message": "NOT FOUND",
                "status_code": 404
            }
            return flask.jsonify(**context), 404
        cur = connection.execute(
            "SELECT EXISTS(SELECT owner FROM likes "
            "WHERE postid = " + str(postid_url_slug) + " "
            "AND owner = '" + current + "') AS count"
        )
        whetherlike = cur.fetchall()[0]['count']
        if whetherlike == 0:
            cur = connection.execute(
                "INSERT INTO likes(owner, postid) "
                "VALUES('" + current + "', " + str(postid_url_slug) + ")"
            )
            context = {
                "logname": current,
                "postid": postid_url_slug
            }
            return flask.jsonify(**context), 201
        context = {
            "logname": current,
            "message": "Conflict",
            "postid": postid_url_slug,
            "status": 409
        }
        return flask.jsonify(**context), 409
    ambiguitytext = {
        "message": "Forbidden",
        "status_code": 403
    }
    return flask.jsonify(**ambiguitytext), 403

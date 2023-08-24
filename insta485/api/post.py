"""REST API for posts."""
import flask
from flask import session
import insta485

# @insta485.app.errorhandler(InvalidUsage)
# def handle_invalid_usage(error):
#     response = jsonify(error.to_dict())
#     response.status_code = error.status_code
#     return response


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/', methods=["GET"])
def get_post(postid_url_slug):
    """GET /api/v1/p/<postid>/."""
    if 'current' in session:
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(created) AS exist FROM posts"
        )
        lenpost = cur.fetchall()[0]['exist']
        if postid_url_slug > lenpost:
            error = {
                "message": "NOT FOUND",
                "status_code": 404
            }
            return flask.jsonify(**error), 404
        cur = connection.execute(
            "SELECT DISTINCT posts.created AS age, "
            "posts.filename AS img_url, posts.owner AS owner, "
            "users.filename AS owner_img_url FROM posts, users "
            "WHERE posts.postid = " + str(postid_url_slug) + " "
            "AND users.username = posts.owner"
        )
        info = cur.fetchall()[0]
        context = {
            "age": info["age"],
            "img_url": "/uploads/" + info["img_url"],
            "owner": info["owner"],
            "owner_img_url": "/uploads/" + info["owner_img_url"],
            "owner_show_url": "/u/" + info["owner"] + "/",
            "post_show_url": "/p/" + str(postid_url_slug) + "/",
            "url": flask.request.path,
        }
        return flask.jsonify(**context)
    errormessage = {
        "message": "Forbidden",
        "status_code": 403
    }
    return flask.jsonify(**errormessage), 403

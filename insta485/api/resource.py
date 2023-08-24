"""Have func get_resource."""
import flask
from flask import session
import insta485


@insta485.app.route('/api/v1/', methods=['GET'])
def get_resource():
    """GET /api/v1/."""
    context = {
        "posts": "/api/v1/p/",
        "url": flask.request.path
    }
    if 'current' in session:
        return flask.jsonify(**context)
    return flask.jsonify(**context), 200
